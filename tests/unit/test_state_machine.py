from datetime import datetime, timedelta, timezone

from src.domain.pet_engine import apply_action, apply_elapsed_time, create_pet
from src.domain.pet_types import EventType, PetAction, PetState, StatBlock


BASE_TIME = datetime(2026, 4, 16, 12, 0, tzinfo=timezone.utc)


def test_any_stat_below_threshold_makes_pet_sick_on_next_evaluation():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1").with_stats(
        StatBlock(hunger=24, happiness=80, energy=80)
    )

    result = apply_elapsed_time(pet, now=BASE_TIME + timedelta(seconds=30))

    assert result.pet.state is PetState.SICK
    assert result.pet.sick_streak == 1
    assert result.events[0].event_type is EventType.BECAME_SICK


def test_action_that_drops_one_stat_below_threshold_makes_pet_sick():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1").with_stats(
        StatBlock(hunger=16, happiness=80, energy=80)
    )

    result = apply_action(pet, PetAction.PLAY, now=BASE_TIME)

    assert result.pet.state is PetState.SICK
    assert result.pet.sick_streak == 1
    assert any(event.event_type is EventType.BECAME_SICK for event in result.events)


def test_sick_pet_recovers_after_two_good_evaluations():
    pet = (
        create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")
        .with_stats(StatBlock(hunger=10, happiness=10, energy=80))
        .with_changes(state=PetState.SICK)
    )
    improved = pet.with_stats(StatBlock(hunger=50, happiness=50, energy=50))

    first = apply_action(improved, PetAction.FEED, now=BASE_TIME)
    assert first.pet.state is PetState.SICK
    assert first.pet.recovery_streak == 1

    second = apply_action(
        first.pet,
        PetAction.REST,
        now=BASE_TIME + timedelta(minutes=1),
    )
    assert second.pet.state is PetState.NORMAL
    assert second.pet.recovery_streak == 0
    assert any(event.event_type is EventType.RECOVERED for event in second.events)


def test_evolved_sick_pet_recovers_to_evolved_state():
    pet = (
        create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")
        .with_stats(StatBlock(hunger=50, happiness=50, energy=50))
        .with_changes(state=PetState.SICK, is_evolved=True)
    )

    first = apply_action(pet, PetAction.FEED, now=BASE_TIME)
    second = apply_action(
        first.pet,
        PetAction.REST,
        now=BASE_TIME + timedelta(minutes=1),
    )

    assert second.pet.state is PetState.EVOLVED
    assert second.pet.is_evolved is True


def test_pet_evolves_once_after_age_stats_and_action_requirement_are_met():
    pet = (
        create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")
        .with_stats(StatBlock(hunger=80, happiness=80, energy=80))
        .with_changes(age_ticks=12, care_action_count=5)
    )

    evolved = apply_action(pet, PetAction.FEED, now=BASE_TIME)
    repeated = apply_action(
        evolved.pet,
        PetAction.FEED,
        now=BASE_TIME + timedelta(minutes=1),
    )

    assert evolved.pet.state is PetState.EVOLVED
    assert evolved.pet.is_evolved is True
    assert evolved.pet.evolved_at == BASE_TIME
    assert sum(event.event_type is EventType.EVOLVED for event in evolved.events) == 1
    assert not any(event.event_type is EventType.EVOLVED for event in repeated.events)


def test_sick_state_blocks_evolution_even_with_age_stats_and_actions():
    pet = (
        create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")
        .with_stats(StatBlock(hunger=80, happiness=80, energy=80))
        .with_changes(
            state=PetState.SICK,
            age_ticks=12,
            care_action_count=6,
        )
    )

    result = apply_action(pet, PetAction.FEED, now=BASE_TIME)

    assert result.pet.state is PetState.SICK
    assert result.pet.is_evolved is False
    assert not any(event.event_type is EventType.EVOLVED for event in result.events)
