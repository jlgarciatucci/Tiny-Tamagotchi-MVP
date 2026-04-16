from __future__ import annotations

from src.data.repositories import PetRepository, SupabasePetRepository
from src.data.supabase_client import get_supabase_client


def build_supabase_repository() -> PetRepository:
    return SupabasePetRepository(get_supabase_client())
