from __future__ import annotations

from datetime import datetime

from src.data.repositories import PetRepository
from src.domain.pet_engine import apply_elapsed_time
from src.domain.pet_types import TickResult


def resume_from_last_tick(
    repository: PetRepository,
    pet_id: str,
    *,
    now: datetime | None = None,
) -> TickResult | None:
    pet = repository.fetch_active_pet()
    if pet is None or pet.id != pet_id:
        return None

    result = apply_elapsed_time(pet, now=now)
    if result.applied_ticks > 0 or result.events:
        repository.upsert_pet(result.pet)
        repository.append_events(result.events)
    return result
