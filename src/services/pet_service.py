from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.data.repositories import (
    ACTIVE_PET_ID,
    InvalidPetRecordError,
    PetRepository,
    RepositoryError,
)
from src.domain.pet_engine import create_pet as create_domain_pet
from src.domain.pet_engine import apply_action, apply_elapsed_time
from src.domain.pet_types import (
    ActionResult,
    EventType,
    Pet,
    PetAction,
    PetCharacter,
    PetEvent,
)


@dataclass(frozen=True)
class StartupResult:
    pet: Pet | None
    needs_creation: bool
    events: tuple[PetEvent, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class ServiceActionResult:
    pet: Pet
    message: str
    events: tuple[PetEvent, ...]
    error: str | None = None


def load_active_pet(
    repository: PetRepository,
    *,
    now: datetime | None = None,
) -> StartupResult:
    try:
        pet = repository.fetch_active_pet()
    except (RepositoryError, InvalidPetRecordError) as exc:
        return StartupResult(
            pet=None,
            needs_creation=True,
            error=str(exc),
        )

    if pet is None:
        return StartupResult(pet=None, needs_creation=True)

    pet = _apply_saved_character(repository, pet)
    tick_result = apply_elapsed_time(pet, now=now)
    if tick_result.applied_ticks > 0 or tick_result.events:
        try:
            repository.upsert_pet(tick_result.pet)
            repository.append_events(tick_result.events)
        except RepositoryError as exc:
            return StartupResult(
                pet=tick_result.pet,
                needs_creation=False,
                events=tick_result.events,
                error=str(exc),
            )

    return StartupResult(
        pet=tick_result.pet,
        needs_creation=False,
        events=tick_result.events,
    )


def advance_pet_time(
    repository: PetRepository,
    pet: Pet,
    *,
    now: datetime | None = None,
) -> StartupResult:
    pet = _apply_saved_character(repository, pet)
    tick_result = apply_elapsed_time(pet, now=now)
    if tick_result.applied_ticks > 0 or tick_result.events:
        try:
            repository.upsert_pet(tick_result.pet)
            repository.append_events(tick_result.events)
        except RepositoryError as exc:
            return StartupResult(
                pet=tick_result.pet,
                needs_creation=False,
                events=tick_result.events,
                error=str(exc),
            )

    return StartupResult(
        pet=tick_result.pet,
        needs_creation=False,
        events=tick_result.events,
    )


def create_pet(
    repository: PetRepository,
    name: str,
    *,
    now: datetime | None = None,
    character: PetCharacter | str = PetCharacter.ORIGINAL,
) -> StartupResult:
    resolved_character = PetCharacter(character)
    pet = create_domain_pet(
        name,
        now=now,
        pet_id=ACTIVE_PET_ID,
        character=resolved_character,
    )
    try:
        repository.upsert_pet(pet)
        if resolved_character is not PetCharacter.ORIGINAL:
            repository.append_events(
                (_character_event(pet.id, resolved_character, now=now),)
            )
    except RepositoryError as exc:
        return StartupResult(pet=pet, needs_creation=True, error=str(exc))
    return StartupResult(pet=pet, needs_creation=False)


def reset_active_pet(
    repository: PetRepository,
    name: str,
    *,
    now: datetime | None = None,
    character: PetCharacter | str = PetCharacter.ORIGINAL,
) -> StartupResult:
    resolved_character = PetCharacter(character)
    pet = create_domain_pet(
        name,
        now=now,
        pet_id=ACTIVE_PET_ID,
        character=resolved_character,
    )
    try:
        repository.delete_events_for_pet(ACTIVE_PET_ID)
        repository.upsert_pet(pet)
        if resolved_character is not PetCharacter.ORIGINAL:
            repository.append_events(
                (_character_event(pet.id, resolved_character, now=now),)
            )
    except RepositoryError as exc:
        return StartupResult(pet=pet, needs_creation=True, error=str(exc))
    return StartupResult(pet=pet, needs_creation=False)


def update_pet_character(
    repository: PetRepository,
    pet: Pet,
    character: PetCharacter | str,
    *,
    now: datetime | None = None,
) -> StartupResult:
    resolved_character = PetCharacter(character)
    timestamp = now or _utc_now()
    updated_pet = pet.with_changes(
        character=resolved_character,
        updated_at=timestamp,
    )
    try:
        repository.upsert_pet(updated_pet)
        repository.append_events(
            (_character_event(updated_pet.id, resolved_character, now=timestamp),)
        )
    except RepositoryError as exc:
        return StartupResult(
            pet=pet,
            needs_creation=False,
            error=str(exc),
        )
    return StartupResult(pet=updated_pet, needs_creation=False)


def care_for_pet(
    repository: PetRepository,
    pet: Pet,
    action: PetAction | str,
    *,
    now: datetime | None = None,
) -> ServiceActionResult:
    try:
        pet = _apply_saved_character(repository, pet)
        tick_result = apply_elapsed_time(pet, now=now)
        pet_after_time = tick_result.pet
        recent_events = repository.list_recent_events(pet.id, limit=20)
        result: ActionResult = apply_action(
            pet_after_time,
            action,
            now=now,
            recent_events=recent_events,
        )
        repository.upsert_pet(result.pet)
        repository.append_events((*tick_result.events, *result.events))
    except RepositoryError as exc:
        return ServiceActionResult(
            pet=pet,
            message="That action could not be saved. Please try again.",
            events=(),
            error=str(exc),
        )

    return ServiceActionResult(
        pet=result.pet,
        message=result.message,
        events=(*tick_result.events, *result.events),
    )


def _apply_saved_character(repository: PetRepository, pet: Pet) -> Pet:
    try:
        recent_events = repository.list_recent_events(pet.id, limit=50)
    except RepositoryError:
        return pet

    for event in reversed(recent_events):
        if event.payload.get("meta") == "character_selection":
            character_value = event.payload.get("character")
            try:
                return pet.with_changes(character=PetCharacter(character_value))
            except ValueError:
                return pet
    return pet


def _character_event(
    pet_id: str,
    character: PetCharacter,
    *,
    now: datetime | None = None,
) -> PetEvent:
    timestamp = now or _utc_now()
    return PetEvent(
        event_type=EventType.ACTION,
        pet_id=pet_id,
        action=None,
        message=f"Character changed to {character.value.title()}.",
        created_at=timestamp,
        payload={
            "meta": "character_selection",
            "character": character.value,
        },
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
