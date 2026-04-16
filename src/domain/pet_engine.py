from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.domain import pet_rules
from src.domain.pet_types import (
    ActionResult,
    EvaluationSource,
    EventType,
    Pet,
    PetAction,
    PetEvent,
    PetState,
    StatBlock,
    StatDelta,
    TickResult,
)
from src.domain.state_machine import evaluate_state


class PetValidationError(ValueError):
    pass


class InvalidPetActionError(ValueError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_pet_name(name: str) -> str:
    trimmed = name.strip()
    if len(trimmed) < pet_rules.MIN_NAME_LENGTH:
        raise PetValidationError("Pet name must contain at least 1 character.")
    if len(trimmed) > pet_rules.MAX_NAME_LENGTH:
        raise PetValidationError("Pet name must be 20 characters or fewer.")
    return trimmed


def create_pet(
    name: str,
    *,
    now: datetime | None = None,
    pet_id: str | None = None,
) -> Pet:
    created_at = _ensure_aware(now or utc_now())
    return Pet(
        id=pet_id or str(uuid4()),
        name=normalize_pet_name(name),
        state=PetState.NORMAL,
        stats=pet_rules.DEFAULT_STATS,
        age_ticks=pet_rules.DEFAULT_AGE_TICKS,
        is_evolved=False,
        evolved_at=None,
        last_tick_at=created_at,
        created_at=created_at,
        updated_at=created_at,
        sick_streak=0,
        recovery_streak=0,
        care_action_count=0,
    )


def clamp_stat(value: int) -> int:
    return max(pet_rules.STAT_MIN, min(pet_rules.STAT_MAX, value))


def clamp_stats(stats: StatBlock) -> StatBlock:
    return StatBlock(
        hunger=clamp_stat(stats.hunger),
        happiness=clamp_stat(stats.happiness),
        energy=clamp_stat(stats.energy),
    )


def apply_delta(stats: StatBlock, delta: StatDelta) -> StatBlock:
    return clamp_stats(
        StatBlock(
            hunger=stats.hunger + delta.hunger,
            happiness=stats.happiness + delta.happiness,
            energy=stats.energy + delta.energy,
        )
    )


def apply_action(
    pet: Pet,
    action: PetAction | str,
    *,
    now: datetime | None = None,
    recent_events: tuple[PetEvent, ...] = (),
) -> ActionResult:
    resolved_action = _resolve_action(action)
    action_time = _ensure_aware(now or utc_now())
    before = pet
    after_stats = apply_delta(pet.stats, pet_rules.ACTION_EFFECTS[resolved_action])
    changed_pet = pet.with_stats(
        after_stats,
        care_action_count=pet.care_action_count + 1,
        updated_at=action_time,
    )

    message = _action_message(
        action=resolved_action,
        before=before,
        after_stats=after_stats,
        now=action_time,
        recent_events=recent_events,
    )
    action_event = PetEvent(
        event_type=EventType.ACTION,
        pet_id=changed_pet.id,
        action=resolved_action,
        message=message,
        created_at=action_time,
        payload={
            "hunger": changed_pet.hunger,
            "happiness": changed_pet.happiness,
            "energy": changed_pet.energy,
        },
    )

    transition = evaluate_state(
        changed_pet,
        now=action_time,
        source=EvaluationSource.ACTION,
    )
    return ActionResult(
        pet=transition.pet,
        message=message,
        events=(action_event, *transition.events),
    )


def apply_elapsed_time(
    pet: Pet,
    *,
    now: datetime | None = None,
) -> TickResult:
    current_time = _ensure_aware(now or utc_now())
    last_tick_at = _ensure_aware(pet.last_tick_at)

    if last_tick_at > current_time:
        event = PetEvent(
            event_type=EventType.TIME_ANOMALY,
            pet_id=pet.id,
            message=pet_rules.STATE_EVENT_MESSAGES["future_tick"],
            created_at=current_time,
            payload={
                "last_tick_at": last_tick_at.isoformat(),
                "now": current_time.isoformat(),
            },
        )
        return TickResult(pet=pet, applied_ticks=0, events=(event,))

    elapsed = current_time - last_tick_at
    full_ticks = int(elapsed // pet_rules.TICK_DURATION)
    applied_ticks = min(full_ticks, pet_rules.MAX_OFFLINE_TICKS)

    if applied_ticks <= 0:
        return TickResult(pet=pet, applied_ticks=0, events=())

    ticked_pet = pet
    events: list[PetEvent] = []
    for _ in range(applied_ticks):
        ticked_pet = _apply_one_tick(ticked_pet)
        transition = evaluate_state(
            ticked_pet,
            now=current_time,
            source=EvaluationSource.ELAPSED_TICK,
        )
        ticked_pet = transition.pet
        events.extend(transition.events)

    ticked_pet = ticked_pet.with_changes(updated_at=current_time)
    return TickResult(
        pet=ticked_pet,
        applied_ticks=applied_ticks,
        events=tuple(events),
    )


def normalize_pet_stats(pet: Pet) -> Pet:
    return pet.with_stats(clamp_stats(pet.stats))


def _apply_one_tick(pet: Pet) -> Pet:
    return pet.with_stats(
        apply_delta(pet.stats, pet_rules.TICK_DECAY),
        age_ticks=pet.age_ticks + 1,
        last_tick_at=pet.last_tick_at + pet_rules.TICK_DURATION,
    )


def _resolve_action(action: PetAction | str) -> PetAction:
    if isinstance(action, PetAction):
        return action
    try:
        return PetAction(action)
    except ValueError as exc:
        raise InvalidPetActionError(f"Unsupported pet action: {action}") from exc


def _action_message(
    *,
    action: PetAction,
    before: Pet,
    after_stats: StatBlock,
    now: datetime,
    recent_events: tuple[PetEvent, ...],
) -> str:
    feed_count = _feed_count_in_window(now, recent_events) + 1
    if action is PetAction.FEED and feed_count >= pet_rules.SNACK_ATTACK_FEED_COUNT:
        return pet_rules.SNACK_ATTACK_MESSAGE
    if action is PetAction.PLAY and before.energy < 20:
        return pet_rules.TIRED_PLAY_MESSAGE
    if (
        action is PetAction.REST
        and before.energy < 15
        and after_stats.energy >= 30
    ):
        return pet_rules.COZY_REST_MESSAGE
    return pet_rules.ACTION_MESSAGES[action]


def _feed_count_in_window(now: datetime, events: tuple[PetEvent, ...]) -> int:
    window_start = now - pet_rules.SNACK_ATTACK_WINDOW
    return sum(
        event.event_type is EventType.ACTION
        and event.action is PetAction.FEED
        and window_start <= event.created_at <= now
        for event in events
    )


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
