from __future__ import annotations

from html import escape
from textwrap import dedent

import streamlit as st

from src.data.supabase_client import SupabaseConfigError
from src.domain import pet_rules
from src.domain.pet_engine import PetValidationError, state_message
from src.domain.pet_types import Pet, PetAction, PetCharacter, PetState
from src.services.asset_service import SceneAssets, load_scene_assets
from src.services.persistence_service import build_supabase_repository
from src.services.pet_service import (
    advance_pet_time,
    care_for_pet,
    create_pet,
    load_active_pet,
)


st.set_page_config(
    page_title="Pet Status",
    page_icon="T",
    layout="centered",
    initial_sidebar_state="collapsed",
)


SESSION_PET_KEY = "active_pet"


@st.cache_resource
def _repository():
    return build_supabase_repository()


@st.cache_data(ttl=300, show_spinner=False)
def _cached_scene_assets(
    pet_state_value: str,
    scene_mode: str,
    pet_character_value: str,
) -> SceneAssets:
    return load_scene_assets(
        _repository(),
        PetState(pet_state_value),
        scene_mode,
        PetCharacter(pet_character_value),
    )


def main() -> None:
    _render_styles()

    try:
        repository = _repository()
    except SupabaseConfigError as exc:
        st.warning(str(exc))
        return

    _render_live_status(repository)


@st.fragment(run_every=f"{int(pet_rules.TICK_DURATION.total_seconds())}s")
def _render_live_status(repository) -> None:
    startup = _load_live_pet(repository)
    if startup.error:
        st.warning(startup.error)

    if startup.needs_creation or startup.pet is None:
        st.session_state.pop(SESSION_PET_KEY, None)
        _render_creation(repository)
        return

    pet = startup.pet
    message = st.session_state.pop("pet_message", None) or _default_message(pet)
    scene_mode = st.session_state.setdefault("scene_mode", "day")
    scene_assets = _cached_scene_assets(
        pet.state.value,
        scene_mode,
        pet.character.value,
    )
    if scene_assets.error:
        st.warning(scene_assets.error)

    _render_scene(
        pet,
        message=message,
        scene_mode=scene_assets.effective_scene_mode,
        scene_assets=scene_assets,
    )

    action_label, scene_picker = st.columns([3, 1])
    with action_label:
        st.markdown("### Actions")
    with scene_picker:
        if pet.state is not PetState.EVOLVED:
            mode = st.selectbox(
                "Scene",
                ["day", "night"],
                index=0 if scene_mode == "day" else 1,
                label_visibility="collapsed",
            )
            if mode != scene_mode:
                st.session_state["scene_mode"] = mode
                _rerun_live_fragment()
        else:
            st.caption(scene_assets.effective_scene_mode.title())

    c1, c2, c3 = st.columns(3)
    actions = (
        (c1, "Feed", PetAction.FEED),
        (c2, "Play", PetAction.PLAY),
        (c3, "Rest", PetAction.REST),
    )
    for column, label, action in actions:
        with column:
            if st.button(label, use_container_width=True):
                result = care_for_pet(repository, pet, action)
                st.session_state[SESSION_PET_KEY] = result.pet
                st.session_state["pet_message"] = result.message
                if result.error:
                    st.warning(result.error)
                _rerun_live_fragment()

    st.caption(
        "This scene is powered by the real engine, timing, state transitions, and Supabase persistence."
    )


def _load_live_pet(repository):
    cached_pet = st.session_state.get(SESSION_PET_KEY)
    if isinstance(cached_pet, Pet):
        result = advance_pet_time(repository, cached_pet)
    else:
        result = load_active_pet(repository)

    if result.pet is not None:
        st.session_state[SESSION_PET_KEY] = result.pet

    return result


def _render_creation(repository) -> None:
    st.title("Tiny Tamagotchi")
    st.write("Name your tiny friend to begin.")

    with st.form("create-pet"):
        name = st.text_input("Pet name", max_chars=20)
        character_choice = st.radio(
            "Choose a character",
            options=[PetCharacter.ORIGINAL.value, PetCharacter.BEAGLE.value],
            format_func=_character_label,
            horizontal=True,
        )
        submitted = st.form_submit_button("Create pet")

    if not submitted:
        return

    try:
        result = create_pet(
            repository,
            name,
            character=PetCharacter(character_choice),
        )
    except PetValidationError as exc:
        st.error(str(exc))
        return

    if result.error:
        st.error(result.error)
        return

    if result.pet is not None:
        st.session_state[SESSION_PET_KEY] = result.pet
    st.session_state["pet_message"] = "Your tiny friend is here."
    _rerun_live_fragment()


def _rerun_live_fragment() -> None:
    st.rerun(scope="fragment")


def _render_scene(
    pet: Pet,
    *,
    message: str,
    scene_mode: str,
    scene_assets: SceneAssets,
) -> None:
    if scene_assets.has_images:
        _render_image_scene(pet, message=message, scene_assets=scene_assets)
        return

    _render_placeholder_scene(pet, message=message, scene_mode=scene_mode)


def _render_image_scene(
    pet: Pet,
    *,
    message: str,
    scene_assets: SceneAssets,
) -> None:
    aspect_style = _scene_aspect_style(scene_assets)
    background_url = escape(scene_assets.background_image_url or "")
    state_color = {
        PetState.NORMAL: "#fff4cc",
        PetState.SICK: "#ffd6d6",
        PetState.EVOLVED: "#d9ffe2",
    }[pet.state]
    state_text_color = {
        PetState.NORMAL: "#6f5200",
        PetState.SICK: "#8b1e1e",
        PetState.EVOLVED: "#176135",
    }[pet.state]

    html = dedent(f"""
    <div class="device-shell">
        <div class="device-top">
            <div class="brand">Tiny Tamagotchi</div>
            <div class="tiny-leds">
                <div class="tiny-led"></div>
                <div class="tiny-led"></div>
                <div class="tiny-led"></div>
            </div>
        </div>
        <div class="screen">
            <div class="scene image-scene" style="{aspect_style} background-image:url('{background_url}');">
                <div class="image-pet-wrap">
                    <div class="speech">{escape(message)}</div>
                    <img class="pet-sprite" src="{escape(scene_assets.pet_image_url or "")}" alt="{escape(pet.name)}">
                    <div class="pet-name">{escape(pet.name)}</div>
                </div>
            </div>
            <div class="pixel-panel">
                <div class="state-chip" style="background:{state_color}; color:{state_text_color};">
                    State: {pet.state.value.title()}
                </div>
                {_stat_bar_html("Hunger", pet.hunger, "#7AD97A")}
                {_stat_bar_html("Happiness", pet.happiness, "#7AD97A")}
                {_stat_bar_html("Energy", pet.energy, "#7AD97A")}
            </div>
        </div>
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)


def _scene_aspect_style(scene_assets: SceneAssets) -> str:
    if scene_assets.background_width and scene_assets.background_height:
        return (
            f"aspect-ratio:{scene_assets.background_width}/"
            f"{scene_assets.background_height};"
        )
    return "aspect-ratio:16/9;"


def _render_placeholder_scene(pet: Pet, *, message: str, scene_mode: str) -> None:
    if scene_mode == "day":
        sky = "linear-gradient(180deg, #87CEFA 0%, #BFE9FF 60%, #DFF6FF 100%)"
        ground = "#7CCB6B"
        sun = "sun"
    else:
        sky = "linear-gradient(180deg, #18233A 0%, #243B63 55%, #314E7B 100%)"
        ground = "#5E9F57"
        sun = "moon"

    state_color = {
        PetState.NORMAL: "#fff4cc",
        PetState.SICK: "#ffd6d6",
        PetState.EVOLVED: "#d9ffe2",
    }[pet.state]
    state_text_color = {
        PetState.NORMAL: "#6f5200",
        PetState.SICK: "#8b1e1e",
        PetState.EVOLVED: "#176135",
    }[pet.state]

    html = dedent(f"""
    <div class="device-shell">
        <div class="device-top">
            <div class="brand">Tiny Tamagotchi</div>
            <div class="tiny-leds">
                <div class="tiny-led"></div>
                <div class="tiny-led"></div>
                <div class="tiny-led"></div>
            </div>
        </div>
        <div class="screen">
            <div class="scene" style="background:{sky};">
                <div class="cloud" style="top:18px; left:26px;"></div>
                <div class="cloud" style="top:54px; left:120px;"></div>
                <div class="{sun}"></div>
                <div class="roof"></div>
                <div class="house"></div>
                <div class="door"></div>
                <div class="tree-top"></div>
                <div class="tree"></div>
                <div class="pet-wrap">
                    <div class="speech">{escape(message)}</div>
                    <div class="pet">{escape(_pet_face(pet))}</div>
                    <div class="pet-name">{escape(pet.name)}</div>
                </div>
                <div class="ground" style="background:{ground};"></div>
            </div>
            <div class="pixel-panel">
                <div class="state-chip" style="background:{state_color}; color:{state_text_color};">
                    State: {pet.state.value.title()}
                </div>
                {_stat_bar_html("Hunger", pet.hunger, "#7AD97A")}
                {_stat_bar_html("Happiness", pet.happiness, "#7AD97A")}
                {_stat_bar_html("Energy", pet.energy, "#7AD97A")}
            </div>
        </div>
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)


def _stat_bar_html(label: str, value: int, default_fill: str) -> str:
    if value >= 70:
        fill = default_fill
    elif value >= 35:
        fill = "#FFD166"
    else:
        fill = "#FF6B6B"

    return (
        f'<div class="stat-wrap">'
        f'<div class="stat-label"><span>{label}</span><span>{value}</span></div>'
        f'<div class="bar-track">'
        f'<div class="bar-fill" style="width:{value}%; background:{fill};"></div>'
        f"</div></div>"
    )


def _pet_face(pet: Pet) -> str:
    if pet.state is PetState.SICK:
        return ":-("
    if pet.state is PetState.EVOLVED:
        return "<(^o^)>"
    if pet.happiness < 30:
        return ":'("
    if pet.energy < 25:
        return "(-.-)z"
    return "(^.^)"


def _default_message(pet: Pet) -> str:
    return state_message(pet)


def _character_label(value: str) -> str:
    return {
        PetCharacter.ORIGINAL.value: "Original",
        PetCharacter.BEAGLE.value: "Beagle",
    }[value]


def _render_styles() -> None:
    st.markdown(
        dedent("""
        <style>
        .main > div {
            padding-top: 0.7rem;
            padding-bottom: 1rem;
            max-width: 720px;
        }
        h3 {
            margin-top: 0.75rem;
            margin-bottom: 0.45rem;
        }
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.35), transparent 30%),
                radial-gradient(circle at top right, rgba(255,255,255,0.18), transparent 24%),
                linear-gradient(180deg, #ffd9ec 0%, #ffeef7 100%);
        }
        .device-shell {
            background: linear-gradient(180deg, #ff9ec7 0%, #ff86b7 100%);
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 22px 50px rgba(165, 62, 111, 0.28), inset 0 3px 0 rgba(255,255,255,0.45);
            border: 2px solid rgba(255,255,255,0.45);
            max-width: 660px;
            margin: 0 auto;
        }
        .device-top {
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom: 10px;
            color:#5f2140;
            font-weight:800;
        }
        .brand {
            font-size: 1.25rem;
        }
        .tiny-leds {
            display:flex;
            gap:8px;
        }
        .tiny-led {
            width:12px;
            height:12px;
            border-radius:50%;
            background:#ffd7e8;
            border:1px solid rgba(95,33,64,0.2);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.8);
        }
        .screen {
            background: #f6fbff;
            border-radius: 8px;
            padding: 12px;
            border: 8px solid #5b5b75;
            box-shadow: inset 0 0 0 4px #9494b3, inset 0 0 22px rgba(0,0,0,0.08);
        }
        .scene {
            position: relative;
            height: 260px;
            border-radius: 8px;
            overflow: hidden;
            border: 2px solid rgba(0,0,0,0.08);
        }
        .image-scene {
            width:100%;
            height:auto;
            max-height:260px;
            margin:0 auto;
            background-position:center;
            background-repeat:no-repeat;
            background-size:100% 100%;
            border:0;
        }
        .image-pet-wrap {
            position:absolute;
            left:50%;
            transform: translateX(-50%);
            bottom: 16px;
            text-align:center;
            z-index:3;
        }
        .pet-sprite {
            display:block;
            width:min(150px, 28vw);
            max-height:135px;
            object-fit:contain;
            margin:0 auto;
            filter: drop-shadow(0 10px 8px rgba(0,0,0,0.18));
            animation: bob 2.2s ease-in-out infinite;
        }
        .cloud {
            position:absolute;
            width:70px;
            height:26px;
            background: rgba(255,255,255,0.9);
            border-radius: 999px;
        }
        .cloud:before, .cloud:after {
            content:"";
            position:absolute;
            background: rgba(255,255,255,0.95);
            border-radius:50%;
        }
        .cloud:before {
            width:32px;
            height:32px;
            left:10px;
            top:-15px;
        }
        .cloud:after {
            width:42px;
            height:42px;
            right:6px;
            top:-20px;
        }
        .sun, .moon {
            position:absolute;
            top: 18px;
            right: 24px;
            width:34px;
            height:34px;
            border-radius:50%;
        }
        .sun {
            background:#ffe46b;
            box-shadow:0 0 26px rgba(255,228,107,0.8);
        }
        .moon {
            background:#f7fbff;
            box-shadow: inset -12px 2px 0 #b9c6e8;
        }
        .ground {
            position:absolute;
            left:0;
            right:0;
            bottom:0;
            height: 64px;
            border-top: 3px solid rgba(255,255,255,0.25);
        }
        .house {
            position:absolute;
            left: 44px;
            bottom: 58px;
            width: 88px;
            height: 58px;
            background:#f8d98d;
            border: 3px solid #7c5b3f;
            border-radius: 8px;
        }
        .roof {
            position:absolute;
            left: 34px;
            bottom: 108px;
            width: 0;
            height: 0;
            border-left: 54px solid transparent;
            border-right: 54px solid transparent;
            border-bottom: 38px solid #d86c6c;
        }
        .door {
            position:absolute;
            left: 78px;
            bottom: 58px;
            width: 18px;
            height: 30px;
            background:#8c5a3c;
            border-radius: 8px 8px 0 0;
            border: 2px solid #6d432a;
        }
        .tree {
            position:absolute;
            right: 56px;
            bottom: 58px;
            width: 16px;
            height: 42px;
            background:#7b523a;
            border-radius: 8px;
        }
        .tree-top {
            position:absolute;
            right: 30px;
            bottom: 88px;
            width: 70px;
            height: 70px;
            background:#67c96b;
            border: 3px solid #44924e;
            border-radius: 50%;
        }
        .pet-wrap {
            position:absolute;
            left:50%;
            transform: translateX(-50%);
            bottom: 68px;
            text-align:center;
            z-index: 5;
        }
        .speech {
            background: rgba(255,255,255,0.95);
            color:#25324a;
            position: relative;
            padding: 10px 14px;
            border-radius: 8px;
            border: 3px solid #25324a;
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 14px;
            min-width: 220px;
            box-shadow: 5px 5px 0 rgba(37,50,74,0.22);
        }
        .speech:before {
            content: "";
            position: absolute;
            left: 50%;
            bottom: -17px;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 14px solid transparent;
            border-right: 14px solid transparent;
            border-top: 17px solid #25324a;
        }
        .speech:after {
            content: "";
            position: absolute;
            left: 50%;
            bottom: -11px;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-top: 13px solid rgba(255,255,255,0.95);
        }
        .pet {
            font-family: monospace;
            font-size: 3.4rem;
            line-height: 1;
            filter: drop-shadow(0 10px 6px rgba(0,0,0,0.12));
            animation: bob 2.2s ease-in-out infinite;
        }
        .pet-name {
            margin-top: 4px;
            font-weight: 800;
            color:#2a3550;
            font-size: 1rem;
        }
        .pixel-panel {
            margin-top: 10px;
            background: #21263a;
            color: #f7fbff;
            border-radius: 8px;
            padding: 12px;
            border: 3px solid #4c536d;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
        }
        .state-chip {
            display:inline-block;
            padding: 0.35rem 0.8rem;
            border-radius: 8px;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }
        .stat-wrap {
            margin-bottom: 0.45rem;
        }
        .stat-label {
            display:flex;
            justify-content:space-between;
            font-weight:700;
            margin-bottom:0.25rem;
        }
        .bar-track {
            width:100%;
            height:13px;
            background:#2f3347;
            border-radius:8px;
            overflow:hidden;
            border:1px solid rgba(255,255,255,0.08);
        }
        .bar-fill {
            height:100%;
            border-radius:8px;
            transition: width 0.35s ease, background 0.25s ease;
        }
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 800;
            font-size: 1rem;
            padding: 0.75rem 0.8rem;
            border: none;
            background: linear-gradient(180deg, #ffe46b 0%, #ffcb38 100%);
            color: #473700;
            box-shadow: 0 4px 0 #d79f09;
        }
        div.stButton > button:hover {
            filter: brightness(1.02);
        }
        @keyframes bob {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
            100% { transform: translateY(0px); }
        }
        </style>
        """).strip(),
        unsafe_allow_html=True,
    )


main()
