from __future__ import annotations

from datetime import datetime

from src.domain import pet_rules
from src.domain.pet_types import (
    EvaluationSource,
    EventType,
    Pet,
    PetEvent,
    PetState,
    StateEvaluationResult,
)


def is_sickness_condition_met(pet: Pet) -> bool:
    low_stats = sum(
        value < pet_rules.SICK_STAT_THRESHOLD
        for value in (pet.hunger, pet.happiness, pet.energy)
    )
    return low_stats >= pet_rules.SICK_STAT_COUNT


def is_recovery_condition_met(pet: Pet) -> bool:
    return (
        pet.hunger >= pet_rules.RECOVERY_STAT_THRESHOLD
        and pet.happiness >= pet_rules.RECOVERY_STAT_THRESHOLD
        and pet.energy >= pet_rules.RECOVERY_STAT_THRESHOLD
    )


def is_evolution_eligible(pet: Pet) -> bool:
    return (
        not pet.is_evolved
        and pet.state is not PetState.SICK
        and pet.age_ticks >= pet_rules.EVOLUTION_MIN_AGE_TICKS
        and pet.hunger >= pet_rules.EVOLUTION_MIN_STAT
        and pet.happiness >= pet_rules.EVOLUTION_MIN_STAT
        and pet.energy >= pet_rules.EVOLUTION_MIN_STAT
        and pet.care_action_count >= pet_rules.EVOLUTION_MIN_CARE_ACTIONS
    )


def evaluate_state(
    pet: Pet,
    *,
    now: datetime,
    source: EvaluationSource,
) -> StateEvaluationResult:
    pet_after_streaks = _update_streaks(pet, source=source)
    sick_ready = (
        pet_after_streaks.state is not PetState.SICK
        and pet_after_streaks.sick_streak >= pet_rules.SICK_STREAK_THRESHOLD
    )

    if sick_ready:
        sick_pet = pet_after_streaks.with_changes(
            state=PetState.SICK,
            recovery_streak=0,
            updated_at=now,
        )
        return StateEvaluationResult(
            pet=sick_pet,
            events=(
                PetEvent(
                    event_type=EventType.BECAME_SICK,
                    pet_id=sick_pet.id,
                    message=pet_rules.STATE_EVENT_MESSAGES["became_sick"],
                    created_at=now,
                    payload={"source": source.value},
                ),
            ),
        )

    if pet_after_streaks.state is PetState.SICK:
        recovery_ready = (
            pet_after_streaks.recovery_streak
            >= pet_rules.RECOVERY_STREAK_THRESHOLD
        )
        if recovery_ready:
            recovered_state = (
                PetState.EVOLVED
                if pet_after_streaks.is_evolved
                else PetState.NORMAL
            )
            message_key = (
                "recovered_evolved"
                if recovered_state is PetState.EVOLVED
                else "recovered_normal"
            )
            recovered_pet = pet_after_streaks.with_changes(
                state=recovered_state,
                sick_streak=0,
                recovery_streak=0,
                updated_at=now,
            )
            return StateEvaluationResult(
                pet=recovered_pet,
                events=(
                    PetEvent(
                        event_type=EventType.RECOVERED,
                        pet_id=recovered_pet.id,
                        message=pet_rules.STATE_EVENT_MESSAGES[message_key],
                        created_at=now,
                        payload={"source": source.value},
                    ),
                ),
            )
        return StateEvaluationResult(pet=pet_after_streaks, events=())

    if is_evolution_eligible(pet_after_streaks):
        evolved_pet = pet_after_streaks.with_changes(
            state=PetState.EVOLVED,
            is_evolved=True,
            evolved_at=now,
            sick_streak=0,
            recovery_streak=0,
            updated_at=now,
        )
        return StateEvaluationResult(
            pet=evolved_pet,
            events=(
                PetEvent(
                    event_type=EventType.EVOLVED,
                    pet_id=evolved_pet.id,
                    message=pet_rules.STATE_EVENT_MESSAGES["evolved"],
                    created_at=now,
                    payload={"source": source.value},
                ),
            ),
        )

    return StateEvaluationResult(pet=pet_after_streaks, events=())


def _update_streaks(pet: Pet, *, source: EvaluationSource) -> Pet:
    sick_streak = pet.sick_streak
    recovery_streak = pet.recovery_streak

    if pet.state is PetState.SICK:
        if is_recovery_condition_met(pet):
            recovery_streak += 1
        else:
            recovery_streak = 0

        if is_sickness_condition_met(pet):
            sick_streak += 1
        elif not is_sickness_condition_met(pet):
            sick_streak = 0

        return pet.with_changes(
            sick_streak=sick_streak,
            recovery_streak=recovery_streak,
        )

    if is_sickness_condition_met(pet):
        sick_streak += 1
    elif not is_sickness_condition_met(pet):
        sick_streak = 0

    return pet.with_changes(
        sick_streak=sick_streak,
        recovery_streak=0,
    )
