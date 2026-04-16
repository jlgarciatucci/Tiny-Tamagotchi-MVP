from datetime import datetime, timedelta, timezone

import pytest

from src.domain import pet_rules
from src.domain.pet_engine import (
    InvalidPetActionError,
    PetValidationError,
    apply_action,
    apply_elapsed_time,
    create_pet,
    state_message,
)
from src.domain.pet_types import EventType, PetAction, PetEvent, PetState, StatBlock


BASE_TIME = datetime(2026, 4, 16, 12, 0, tzinfo=timezone.utc)


def test_create_pet_uses_deterministic_defaults_and_trims_name():
    pet = create_pet("  Mochi  ", now=BASE_TIME, pet_id="pet-1")

    assert pet.id == "pet-1"
    assert pet.name == "Mochi"
    assert pet.state is PetState.NORMAL
    assert pet.hunger == 80
    assert pet.happiness == 80
    assert pet.energy == 80
    assert pet.age_ticks == 0
    assert pet.is_evolved is False
    assert pet.evolved_at is None
    assert pet.created_at == BASE_TIME
    assert pet.updated_at == BASE_TIME
    assert pet.last_tick_at == BASE_TIME


@pytest.mark.parametrize("name", ["", "   ", "x" * 21])
def test_create_pet_rejects_invalid_names(name):
    with pytest.raises(PetValidationError):
        create_pet(name, now=BASE_TIME)


def test_apply_action_updates_stats_and_emits_action_event():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")

    result = apply_action(
        pet,
        PetAction.PLAY,
        now=BASE_TIME + timedelta(minutes=1),
    )

    assert result.pet.hunger == 76
    assert result.pet.happiness == 96
    assert result.pet.energy == 72
    assert result.pet.care_action_count == 1
    assert result.message in pet_rules.ACTION_MESSAGES[PetAction.PLAY]
    assert result.events[0].event_type is EventType.ACTION
    assert result.events[0].action is PetAction.PLAY


def test_feed_play_and_rest_have_distinct_specified_effects():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1").with_stats(
        StatBlock(hunger=50, happiness=50, energy=50)
    )

    fed = apply_action(pet, PetAction.FEED, now=BASE_TIME).pet
    played = apply_action(pet, PetAction.PLAY, now=BASE_TIME).pet
    rested = apply_action(pet, PetAction.REST, now=BASE_TIME).pet

    assert (fed.hunger, fed.happiness, fed.energy) == (68, 54, 50)
    assert (played.hunger, played.happiness, played.energy) == (46, 66, 42)
    assert (rested.hunger, rested.happiness, rested.energy) == (48, 47, 70)


def test_apply_action_rejects_unknown_action_without_mutating_pet():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")

    with pytest.raises(InvalidPetActionError):
        apply_action(pet, "dance", now=BASE_TIME)

    assert pet.hunger == 80
    assert pet.happiness == 80
    assert pet.energy == 80
    assert pet.care_action_count == 0


def test_action_clamps_stats_and_uses_easter_egg_messages():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1").with_stats(
        pet_rules.DEFAULT_STATS.__class__(hunger=95, happiness=95, energy=80)
    )
    prior_feeds = (
        PetEvent(
            event_type=EventType.ACTION,
            action=PetAction.FEED,
            pet_id=pet.id,
            message="older feed",
            created_at=BASE_TIME - timedelta(minutes=3),
        ),
        PetEvent(
            event_type=EventType.ACTION,
            action=PetAction.FEED,
            pet_id=pet.id,
            message="newer feed",
            created_at=BASE_TIME - timedelta(minutes=1),
        ),
    )

    result = apply_action(
        pet,
        PetAction.FEED,
        now=BASE_TIME,
        recent_events=prior_feeds,
    )

    assert result.pet.hunger == 100
    assert result.pet.happiness == 99
    assert result.message == pet_rules.SNACK_ATTACK_MESSAGE


def test_standard_action_messages_have_deterministic_variety():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")

    first = apply_action(pet, PetAction.REST, now=BASE_TIME)
    second = apply_action(
        first.pet,
        PetAction.REST,
        now=BASE_TIME + timedelta(minutes=1),
    )

    assert first.message in pet_rules.ACTION_MESSAGES[PetAction.REST]
    assert second.message in pet_rules.ACTION_MESSAGES[PetAction.REST]
    assert first.message != second.message


def test_apply_elapsed_time_uses_full_ticks_and_preserves_partial_tick():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")

    result = apply_elapsed_time(
        pet,
        now=BASE_TIME + timedelta(minutes=2, seconds=20),
    )

    assert result.applied_ticks == 4
    assert result.pet.hunger == 40
    assert result.pet.happiness == 48
    assert result.pet.energy == 64
    assert result.pet.age_ticks == 4
    assert result.pet.last_tick_at == BASE_TIME + timedelta(minutes=2)


def test_apply_elapsed_time_caps_offline_catchup():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")

    result = apply_elapsed_time(
        pet,
        now=BASE_TIME + timedelta(days=2),
    )

    assert result.applied_ticks == pet_rules.MAX_OFFLINE_TICKS
    assert result.pet.age_ticks == pet_rules.MAX_OFFLINE_TICKS
    assert result.pet.last_tick_at == (
        BASE_TIME + pet_rules.MAX_OFFLINE_TICKS * pet_rules.TICK_DURATION
    )
    assert result.pet.hunger == 0
    assert result.pet.happiness == 0
    assert result.pet.energy == 0


def test_apply_elapsed_time_handles_future_last_tick_without_decay():
    pet = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")

    result = apply_elapsed_time(
        pet,
        now=BASE_TIME - timedelta(minutes=1),
    )

    assert result.applied_ticks == 0
    assert result.pet == pet
    assert result.events[0].event_type is EventType.TIME_ANOMALY


def test_state_message_rotates_with_state_and_time():
    normal = create_pet("Mochi", now=BASE_TIME, pet_id="pet-1")
    sick = normal.with_changes(state=PetState.SICK)
    evolved = normal.with_changes(state=PetState.EVOLVED, is_evolved=True)

    normal_message = state_message(normal, now=BASE_TIME)
    later_normal_message = state_message(
        normal,
        now=BASE_TIME + timedelta(seconds=1),
    )

    assert normal_message in {
        template.format(name="Mochi")
        for template in pet_rules.STATE_MESSAGES[PetState.NORMAL]
    }
    assert later_normal_message in {
        template.format(name="Mochi")
        for template in pet_rules.STATE_MESSAGES[PetState.NORMAL]
    }
    assert normal_message != later_normal_message
    assert state_message(sick, now=BASE_TIME) in {
        template.format(name="Mochi")
        for template in pet_rules.STATE_MESSAGES[PetState.SICK]
    }
    assert state_message(evolved, now=BASE_TIME) in {
        template.format(name="Mochi")
        for template in pet_rules.STATE_MESSAGES[PetState.EVOLVED]
    }
