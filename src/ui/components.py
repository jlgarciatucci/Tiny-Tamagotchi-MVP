from __future__ import annotations

import streamlit as st

from src.domain.pet_types import Pet, PetAction, PetEvent
from src.ui.theme import STATE_AVATARS, STATE_CAPTIONS, STATE_LABELS


def render_pet_header(pet: Pet) -> None:
    st.markdown('<div class="tiny-shell">', unsafe_allow_html=True)
    st.title(pet.name)
    st.markdown(
        f'<div class="tiny-avatar">{STATE_AVATARS[pet.state]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="tiny-state">{STATE_LABELS[pet.state]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="tiny-caption">{STATE_CAPTIONS[pet.state]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_stats(pet: Pet) -> None:
    _stat("Hunger", pet.hunger)
    _stat("Happiness", pet.happiness)
    _stat("Energy", pet.energy)


def render_action_buttons() -> PetAction | None:
    feed, play, rest = st.columns(3)
    if feed.button("Feed", use_container_width=True):
        return PetAction.FEED
    if play.button("Play", use_container_width=True):
        return PetAction.PLAY
    if rest.button("Rest", use_container_width=True):
        return PetAction.REST
    return None


def render_message(message: str | None) -> None:
    if message:
        st.markdown(
            f'<div class="tiny-message">{message}</div>',
            unsafe_allow_html=True,
        )


def render_event_list(events: tuple[PetEvent, ...]) -> None:
    if not events:
        st.info("No tiny memories yet.")
        return

    for event in reversed(events):
        timestamp = event.created_at.strftime("%Y-%m-%d %H:%M")
        st.write(f"{timestamp} - {event.message}")


def _stat(label: str, value: int) -> None:
    st.write(f"{label}: {value}/100")
    st.progress(value / 100)
