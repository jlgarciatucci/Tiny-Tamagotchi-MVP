from __future__ import annotations

from dataclasses import dataclass

from src.data.repositories import AssetRecord, PetRepository, RepositoryError
from src.domain.pet_types import PetState


PET_ASSET_BY_STATE: dict[PetState, str] = {
    PetState.NORMAL: "normal_pet",
    PetState.SICK: "sick_pet",
    PetState.EVOLVED: "evolved_pet",
}

DEFAULT_BACKGROUND_BY_STATE: dict[PetState, str] = {
    PetState.NORMAL: "daytime_scene",
    PetState.SICK: "night_scene",
    PetState.EVOLVED: "evolved_scene",
}

NORMAL_SCENE_MODE_TO_BACKGROUND: dict[str, str] = {
    "day": "daytime_scene",
    "night": "night_scene",
}


@dataclass(frozen=True)
class SceneAssetKeys:
    pet_asset_key: str
    background_scene_type: str
    effective_scene_mode: str


@dataclass(frozen=True)
class SceneAssets:
    pet_image_url: str | None
    background_image_url: str | None
    effective_scene_mode: str
    background_width: int | None = None
    background_height: int | None = None
    error: str | None = None

    @property
    def has_images(self) -> bool:
        return bool(self.pet_image_url and self.background_image_url)


@dataclass(frozen=True)
class PetSpriteAsset:
    image_url: str | None
    error: str | None = None

    @property
    def has_image(self) -> bool:
        return bool(self.image_url)


def select_scene_asset_keys(
    pet_state: PetState,
    selected_scene_mode: str | None = None,
    *,
    normal_night_available: bool = True,
) -> SceneAssetKeys:
    pet_asset_key = PET_ASSET_BY_STATE[pet_state]

    if pet_state is PetState.EVOLVED:
        return SceneAssetKeys(pet_asset_key, "evolved_scene", "evolved")

    if pet_state is PetState.SICK:
        return SceneAssetKeys(pet_asset_key, "night_scene", "night")

    requested_mode = selected_scene_mode if selected_scene_mode in {"day", "night"} else "day"
    if requested_mode == "night" and normal_night_available:
        return SceneAssetKeys(pet_asset_key, "night_scene", "night")

    return SceneAssetKeys(pet_asset_key, "daytime_scene", "day")


def load_scene_assets(
    repository: PetRepository,
    pet_state: PetState,
    selected_scene_mode: str | None = None,
) -> SceneAssets:
    try:
        night_background = repository.fetch_active_background_asset("night_scene")
        keys = select_scene_asset_keys(
            pet_state,
            selected_scene_mode,
            normal_night_available=night_background is not None,
        )
        pet_asset = repository.fetch_active_pet_asset(pet_state.value)
        background_asset = _background_for_keys(repository, keys, night_background)
    except RepositoryError as exc:
        return SceneAssets(
            pet_image_url=None,
            background_image_url=None,
            effective_scene_mode=selected_scene_mode or "day",
            error=str(exc),
        )

    missing: list[str] = []
    if pet_asset is None:
        missing.append(keys.pet_asset_key)
    if background_asset is None:
        missing.append(keys.background_scene_type)

    return SceneAssets(
        pet_image_url=pet_asset.url if pet_asset else None,
        background_image_url=background_asset.url if background_asset else None,
        effective_scene_mode=keys.effective_scene_mode,
        background_width=background_asset.width if background_asset else None,
        background_height=background_asset.height if background_asset else None,
        error=f"Missing active image asset(s): {', '.join(missing)}" if missing else None,
    )


def load_pet_sprite_asset(
    repository: PetRepository,
    pet_state: PetState,
) -> PetSpriteAsset:
    try:
        asset = repository.fetch_active_pet_asset(pet_state.value)
    except RepositoryError as exc:
        return PetSpriteAsset(image_url=None, error=str(exc))

    if asset is None:
        return PetSpriteAsset(
            image_url=None,
            error=f"Missing active image asset: {PET_ASSET_BY_STATE[pet_state]}",
        )

    return PetSpriteAsset(image_url=asset.url)


def _background_for_keys(
    repository: PetRepository,
    keys: SceneAssetKeys,
    night_background: AssetRecord | None,
) -> AssetRecord | None:
    if keys.background_scene_type == "night_scene":
        return night_background
    return repository.fetch_active_background_asset(keys.background_scene_type)
