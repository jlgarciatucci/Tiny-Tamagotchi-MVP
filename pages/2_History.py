from __future__ import annotations

import streamlit as st

from src.data.supabase_client import SupabaseConfigError
from src.services.persistence_service import build_supabase_repository
from src.services.pet_service import load_active_pet
from src.ui.components import render_event_list


st.set_page_config(page_title="History", page_icon="T", layout="centered")
st.title("History")

try:
    repository = build_supabase_repository()
except SupabaseConfigError as exc:
    st.warning(str(exc))
else:
    startup = load_active_pet(repository)
    if startup.pet is None:
        st.info("Create a pet on the main page first.")
    else:
        events = repository.list_recent_events(startup.pet.id, limit=25)
        render_event_list(events)
