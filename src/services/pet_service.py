from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.data.repositories import (
    ACTIVE_PET_ID,
    InvalidPetRecordError,
    PetRepository,
    RepositoryError,
)
from src.domain.pet_engine import create_pet as create_domain_pet
from src.domain.pet_engine import apply_action, apply_elapsed_time
from src.domain.pet_types import ActionResult, Pet, PetAction, PetEvent


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
) -> StartupResult:
    pet = create_domain_pet(name, now=now, pet_id=ACTIVE_PET_ID)
    try:
        repository.upsert_pet(pet)
    except RepositoryError as exc:
        return StartupResult(pet=pet, needs_creation=True, error=str(exc))
    return StartupResult(pet=pet, needs_creation=False)


def reset_active_pet(
    repository: PetRepository,
    name: str,
    *,
    now: datetime | None = None,
) -> StartupResult:
    pet = create_domain_pet(name, now=now, pet_id=ACTIVE_PET_ID)
    try:
        repository.delete_events_for_pet(ACTIVE_PET_ID)
        repository.upsert_pet(pet)
    except RepositoryError as exc:
        return StartupResult(pet=pet, needs_creation=True, error=str(exc))
    return StartupResult(pet=pet, needs_creation=False)


def care_for_pet(
    repository: PetRepository,
    pet: Pet,
    action: PetAction | str,
    *,
    now: datetime | None = None,
) -> ServiceActionResult:
    try:
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
