from __future__ import annotations

from html import escape

import streamlit as st

from src.data.supabase_client import SupabaseConfigError
from src.domain.pet_engine import PetValidationError
from src.domain.pet_types import PetState
from src.services.asset_service import load_pet_sprite_asset
from src.services.persistence_service import build_supabase_repository
from src.services.pet_service import create_pet, load_active_pet, reset_active_pet


st.set_page_config(
    page_title="Tiny Tamagotchi MVP",
    page_icon="T",
    layout="centered",
    initial_sidebar_state="collapsed",
)


SESSION_PET_KEY = "active_pet"


@st.cache_resource
def _repository():
    return build_supabase_repository()


def main() -> None:
    _render_styles()

    try:
        repository = _repository()
    except SupabaseConfigError as exc:
        _render_landing_header(None)
        st.warning(str(exc))
        return

    mascot = load_pet_sprite_asset(repository, PetState.EVOLVED)
    _render_landing_header(mascot.image_url)
    if mascot.error:
        st.caption(mascot.error)

    startup = load_active_pet(repository)
    if startup.error:
        st.warning(startup.error)

    existing_pet = startup.pet if not startup.needs_creation else None
    default_name = existing_pet.name if existing_pet else ""

    with st.form("start-game"):
        name = st.text_input("Pet name", value=default_name, max_chars=20)
        submitted = st.form_submit_button("Start Game", use_container_width=True)

    if submitted:
        try:
            if existing_pet is None:
                result = create_pet(repository, name)
            elif name.strip() != existing_pet.name:
                result = reset_active_pet(repository, name)
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
            f"{existing_pet.name} is waiting for you. Enter a different name to start fresh."
        )


def _render_landing_header(mascot_url: str | None) -> None:
    if mascot_url:
        mascot_html = (
            f'<img class="mascot-img" src="{escape(mascot_url)}" '
            'alt="Evolved pet">'
        )
    else:
        mascot_html = '<div class="mascot">(^.^)</div>'

    st.markdown(
        f"""
<div class="wrap">
    <div class="mascot-stage">{mascot_html}</div>
    <div class="title">Tiny Tamagotchi</div>
    <div class="sub">Name your tiny friend and start caring for them.</div>
</div>
        """.strip(),
        unsafe_allow_html=True,
    )


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
.mascot-stage {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 150px;
    margin-bottom: 0.3rem;
}
.mascot-img {
    display: block;
    width: min(190px, 42vw);
    max-height: 180px;
    object-fit: contain;
    filter: drop-shadow(0 12px 10px rgba(165, 62, 111, 0.24));
    animation: landing-bob 2.4s ease-in-out infinite;
}
.mascot {
    font-family: monospace;
    font-size: 3rem;
    line-height: 1;
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
