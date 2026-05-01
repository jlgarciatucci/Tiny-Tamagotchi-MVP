from __future__ import annotations

from html import escape

import streamlit as st

from src.data.supabase_client import SupabaseConfigError
from src.domain.pet_engine import PetValidationError
from src.domain.pet_types import PetCharacter, PetState
from src.services.asset_service import load_pet_sprite_asset
from src.services.persistence_service import build_supabase_repository
from src.services.pet_service import (
    create_pet,
    load_active_pet,
    reset_active_pet,
    update_pet_character,
)


st.set_page_config(
    page_title="Tiny Tamagotchi MVP",
    page_icon="T",
    layout="centered",
    initial_sidebar_state="collapsed",
)


SESSION_PET_KEY = "active_pet"
SESSION_CHARACTER_KEY = "landing_character"


@st.cache_resource
def _repository():
    return build_supabase_repository()


@st.cache_data(ttl=300, show_spinner=False)
def _landing_preview_assets() -> dict[str, tuple[str | None, str | None]]:
    repository = _repository()
    preview_assets: dict[str, tuple[str | None, str | None]] = {}
    for character in (PetCharacter.ORIGINAL, PetCharacter.BEAGLE):
        asset = load_pet_sprite_asset(repository, PetState.NORMAL, character)
        preview_assets[character.value] = (asset.image_url, asset.error)
    return preview_assets


def main() -> None:
    _render_styles()

    try:
        repository = _repository()
    except SupabaseConfigError as exc:
        _render_landing_header()
        st.warning(str(exc))
        return

    startup = load_active_pet(repository)
    if startup.error:
        st.warning(startup.error)

    existing_pet = startup.pet if not startup.needs_creation else None
    default_name = existing_pet.name if existing_pet else ""
    default_character = existing_pet.character if existing_pet else PetCharacter.ORIGINAL
    _render_landing_header()
    selected_character = _render_character_carousel(default_character)

    with st.form("start-game"):
        name = st.text_input("Pet name", value=default_name, max_chars=20)
        submitted = st.form_submit_button("Start Game", use_container_width=True)

    if submitted:
        try:
            if existing_pet is None:
                result = create_pet(repository, name, character=selected_character)
            elif name.strip() != existing_pet.name:
                result = reset_active_pet(
                    repository,
                    name,
                    character=selected_character,
                )
            elif existing_pet.character is not selected_character:
                result = update_pet_character(
                    repository,
                    existing_pet,
                    selected_character,
                )
            else:
                result = startup
        except PetValidationError as exc:
            st.error(str(exc))
            return

        if result.error:
            st.error(result.error)
            return

        if result.pet is not None:
            st.session_state[SESSION_PET_KEY] = result.pet

        if existing_pet is None or name.strip() != existing_pet.name:
            st.session_state["pet_message"] = "Your tiny friend is here."

        st.switch_page("pages/1_Status.py")

    if existing_pet is not None:
        st.caption(
            f"{existing_pet.name} is waiting for you. Enter a different name to start fresh, or switch character to change their look."
        )


def _render_character_carousel(
    default_character: PetCharacter,
) -> PetCharacter:
    characters = (PetCharacter.ORIGINAL, PetCharacter.BEAGLE)
    selected_value = st.session_state.get(SESSION_CHARACTER_KEY, default_character.value)
    if selected_value not in {character.value for character in characters}:
        selected_value = default_character.value
    selected_character = PetCharacter(selected_value)

    left_column, preview_column, right_column = st.columns([1, 6, 1])
    with left_column:
        if st.button("◀", key="roller-left", use_container_width=True):
            selected_character = characters[
                (characters.index(selected_character) - 1) % len(characters)
            ]
            st.session_state[SESSION_CHARACTER_KEY] = selected_character.value

    with right_column:
        if st.button("▶", key="roller-right", use_container_width=True):
            selected_character = characters[
                (characters.index(selected_character) + 1) % len(characters)
            ]
            st.session_state[SESSION_CHARACTER_KEY] = selected_character.value

    preview_assets = _landing_preview_assets()
    with preview_column:
        st.markdown(
            _character_carousel_html(
                selected_character,
                preview_assets,
            ),
            unsafe_allow_html=True,
        )
    st.session_state[SESSION_CHARACTER_KEY] = selected_character.value
    st.caption(f"Selected character: {_character_label(selected_character.value)}")

    for _, error in preview_assets.values():
        if error:
            st.caption(error)

    return selected_character


def _character_label(value: str) -> str:
    return {
        PetCharacter.ORIGINAL.value: "Original",
        PetCharacter.BEAGLE.value: "Beagle",
    }[value]


def _render_landing_header() -> None:
    st.markdown(
        f"""
<div class="wrap">
    <div class="title">Tiny Tamagotchi</div>
    <div class="sub">Slide through the tiny carousel, pick your companion, and start caring for them.</div>
</div>
        """.strip(),
        unsafe_allow_html=True,
    )


def _character_carousel_html(
    selected_character: PetCharacter,
    preview_assets,
) -> str:
    other_character = (
        PetCharacter.BEAGLE
        if selected_character is PetCharacter.ORIGINAL
        else PetCharacter.ORIGINAL
    )
    cards = [
        _character_card_html(
            other_character,
            preview_assets[other_character.value][0],
            "left",
        ),
        _character_card_html(
            selected_character,
            preview_assets[selected_character.value][0],
            "center",
        ),
        _character_card_html(
            other_character,
            preview_assets[other_character.value][0],
            "right",
        ),
    ]
    return f"""
<div class="carousel-shell">
    <div class="carousel-caption">Pick the face you want to care for.</div>
    <div class="carousel-track">
        {''.join(cards)}
    </div>
    <div class="carousel-dots">
        <span class="carousel-dot {'active-dot' if selected_character is PetCharacter.ORIGINAL else ''}"></span>
        <span class="carousel-dot {'active-dot' if selected_character is PetCharacter.BEAGLE else ''}"></span>
    </div>
</div>
    """.strip()


def _character_card_html(
    character: PetCharacter,
    image_url: str | None,
    position: str,
) -> str:
    label = _character_label(character.value)
    card_class = {
        "center": "character-card selected-card",
        "left": "character-card side-card side-left",
        "right": "character-card side-card side-right",
    }[position]
    if image_url:
        visual = (
            f'<img class="character-image" src="{escape(image_url)}" alt="{escape(label)}">'
        )
    else:
        visual = '<div class="mascot">(^.^)</div>'

    return f"""
<div class="{card_class}">
    <div class="character-visual">{visual}</div>
    <div class="character-name">{escape(label)}</div>
</div>
    """.strip()


def _render_styles() -> None:
    st.markdown(
        """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #ffd9ec 0%, #fff1f8 100%);
}
.main > div {
    padding-top: 1.1rem;
    max-width: 680px;
}
.wrap {
    max-width: 640px;
    margin: 1rem auto 1.1rem;
    text-align: center;
    background: rgba(255,255,255,0.88);
    border-radius: 8px;
    padding: 1.2rem 1rem;
    box-shadow: 0 14px 34px rgba(0,0,0,0.08);
}
.mascot {
    font-family: monospace;
    font-size: 3rem;
    line-height: 1;
}
.carousel-shell {
    max-width: 640px;
    margin: 0.2rem auto 1rem;
    padding: 0.4rem 0.2rem 0.7rem;
}
.carousel-caption {
    text-align: center;
    font-size: 0.95rem;
    color: #6b4d5d;
    margin-bottom: 0.8rem;
}
.carousel-track {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
    perspective: 900px;
    min-height: 250px;
    overflow: hidden;
}
.character-card {
    width: min(220px, 34vw);
    min-height: 220px;
    background: rgba(255,255,255,0.92);
    border-radius: 18px;
    padding: 1rem 0.9rem;
    box-shadow: 0 16px 34px rgba(0,0,0,0.08);
    border: 2px solid rgba(255,255,255,0.65);
    transition: transform 0.35s ease, opacity 0.35s ease, box-shadow 0.35s ease, filter 0.35s ease;
    position: relative;
}
.selected-card {
    transform: translateY(0) scale(1.02);
    opacity: 1;
    box-shadow: 0 18px 38px rgba(165, 62, 111, 0.20);
    z-index: 3;
}
.side-card {
    opacity: 0.58;
    filter: saturate(0.9);
    z-index: 1;
}
.side-left {
    transform: translateX(44px) scale(0.82) rotateY(18deg);
}
.side-right {
    transform: translateX(-44px) scale(0.82) rotateY(-18deg);
}
.character-visual {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 150px;
}
.character-image {
    display: block;
    width: min(190px, 30vw);
    max-height: 165px;
    object-fit: contain;
    filter: drop-shadow(0 12px 10px rgba(165, 62, 111, 0.24));
    animation: landing-bob 2.4s ease-in-out infinite;
}
.character-name {
    margin-top: 0.45rem;
    font-size: 1rem;
    font-weight: 800;
    color: #5f2140;
}
.carousel-dots {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
}
.carousel-dot {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: rgba(95,33,64,0.22);
    transition: transform 0.2s ease, background 0.2s ease;
}
.active-dot {
    background: #ff8fba;
    transform: scale(1.25);
}
.title {
    font-size: 2rem;
    font-weight: 800;
    margin-top: 0.4rem;
}
.sub {
    font-size: 1rem;
    opacity: 0.8;
}
div.stButton > button,
div.stFormSubmitButton > button {
    width: 100%;
    border-radius: 8px;
    font-weight: 800;
    padding: 0.8rem;
    border: none;
    background: linear-gradient(180deg, #ffe46b 0%, #ffcb38 100%);
    color: #473700;
    box-shadow: 0 4px 0 #d79f09;
}
@keyframes landing-bob {
    0% { transform: translateY(0); }
    50% { transform: translateY(-7px); }
    100% { transform: translateY(0); }
}
</style>
        """.strip(),
        unsafe_allow_html=True,
    )


main()
