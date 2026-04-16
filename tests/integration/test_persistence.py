from datetime import datetime, timedelta, timezone

import pytest

from src.data.repositories import (
    AssetRecord,
    InMemoryPetRepository,
    InvalidPetRecordError,
    asset_from_record,
    event_from_record,
    event_to_record,
    pet_from_record,
    pet_to_record,
)
from src.domain.pet_types import EventType, PetAction, PetEvent
from src.services.pet_service import care_for_pet, create_pet, load_active_pet, reset_active_pet


BASE_TIME = datetime(2026, 4, 16, 12, 0, tzinfo=timezone.utc)


def test_first_run_routes_to_creation_without_crashing():
    repository = InMemoryPetRepository()

    result = load_active_pet(repository, now=BASE_TIME)

    assert result.needs_creation is True
    assert result.pet is None
    assert result.error is None


def test_existing_pet_resumes_and_persists_elapsed_time():
    repository = InMemoryPetRepository()
    created = create_pet(repository, "Mochi", now=BASE_TIME)

    result = load_active_pet(
        repository,
        now=BASE_TIME + timedelta(minutes=1),
    )

    assert result.needs_creation is False
    assert result.pet is not None
    assert result.pet.age_ticks == 2
    assert repository.pet == result.pet


def test_action_flow_saves_pet_and_appends_events():
    repository = InMemoryPetRepository()
    created = create_pet(repository, "Mochi", now=BASE_TIME)
    assert created.pet is not None

    result = care_for_pet(
        repository,
        created.pet,
        PetAction.FEED,
        now=BASE_TIME + timedelta(minutes=1),
    )

    assert result.error is None
    assert repository.pet == result.pet
    assert repository.events[0].event_type is EventType.ACTION
    assert repository.events[0].action is PetAction.FEED


def test_action_flow_applies_elapsed_decay_before_action():
    repository = InMemoryPetRepository()
    created = create_pet(repository, "Mochi", now=BASE_TIME)
    assert created.pet is not None

    result = care_for_pet(
        repository,
        created.pet,
        PetAction.PLAY,
        now=BASE_TIME + timedelta(minutes=1),
    )

    assert result.error is None
    assert result.pet.age_ticks == 2
    assert result.pet.hunger == 56
    assert result.pet.happiness == 80
    assert result.pet.energy == 64


def test_reset_active_pet_replaces_pet_and_clears_events():
    repository = InMemoryPetRepository()
    created = create_pet(repository, "Jose", now=BASE_TIME)
    assert created.pet is not None
    care_for_pet(repository, created.pet, PetAction.FEED, now=BASE_TIME)

    reset = reset_active_pet(
        repository,
        "Luna",
        now=BASE_TIME + timedelta(minutes=1),
    )

    assert reset.error is None
    assert reset.pet is not None
    assert repository.pet == reset.pet
    assert reset.pet.name == "Luna"
    assert reset.pet.hunger == 80
    assert reset.pet.state.value == "normal"
    assert repository.events == []


def test_pet_record_round_trip_clamps_out_of_range_stats():
    repository = InMemoryPetRepository()
    created = create_pet(repository, "Mochi", now=BASE_TIME)
    assert created.pet is not None

    record = pet_to_record(created.pet)
    record["hunger"] = 130
    record["energy"] = -5

    loaded = pet_from_record(record)

    assert loaded.hunger == 100
    assert loaded.energy == 0


def test_pet_record_accepts_supabase_five_digit_fractional_timestamps():
    repository = InMemoryPetRepository()
    created = create_pet(repository, "Mochi", now=BASE_TIME)
    assert created.pet is not None

    record = pet_to_record(created.pet)
    record["updated_at"] = "2026-04-16T13:58:15.71438+00:00"

    loaded = pet_from_record(record)

    assert loaded.updated_at.microsecond == 714380


def test_pet_record_rejects_unknown_state():
    repository = InMemoryPetRepository()
    created = create_pet(repository, "Mochi", now=BASE_TIME)
    assert created.pet is not None

    record = pet_to_record(created.pet)
    record["state"] = "haunted"

    with pytest.raises(InvalidPetRecordError):
        pet_from_record(record)


def test_event_record_round_trip_preserves_action_payload_and_timestamp():
    event = PetEvent(
        event_type=EventType.ACTION,
        pet_id="active-pet",
        action=PetAction.REST,
        message="A quiet rest helped the tiny paws recharge.",
        payload={"energy": 100},
        created_at=BASE_TIME,
    )

    loaded = event_from_record(event_to_record(event))

    assert loaded.event_type is EventType.ACTION
    assert loaded.pet_id == "active-pet"
    assert loaded.action is PetAction.REST
    assert loaded.payload == {"energy": 100}
    assert loaded.created_at == BASE_TIME


def test_asset_record_uses_public_url_when_present():
    asset = asset_from_record(
        {
            "asset_key": "normal_pet",
            "file_path": "pet-assets/normal_pet.png",
            "public_url": "https://example.test/normal_pet.png",
            "width": 128,
            "height": 128,
        }
    )

    assert asset == AssetRecord(
        asset_key="normal_pet",
        url="https://example.test/normal_pet.png",
        file_path="pet-assets/normal_pet.png",
        width=128,
        height=128,
    )
