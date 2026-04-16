from src.data.repositories import AssetRecord, InMemoryPetRepository
from src.domain.pet_types import PetState
from src.services.asset_service import (
    load_pet_sprite_asset,
    load_scene_assets,
    select_scene_asset_keys,
)


def test_normal_state_uses_daytime_scene_by_default():
    keys = select_scene_asset_keys(PetState.NORMAL)

    assert keys.pet_asset_key == "normal_pet"
    assert keys.background_scene_type == "daytime_scene"
    assert keys.effective_scene_mode == "day"


def test_normal_state_allows_night_when_available():
    keys = select_scene_asset_keys(PetState.NORMAL, "night")

    assert keys.pet_asset_key == "normal_pet"
    assert keys.background_scene_type == "night_scene"
    assert keys.effective_scene_mode == "night"


def test_normal_state_ignores_night_when_background_is_missing():
    keys = select_scene_asset_keys(
        PetState.NORMAL,
        "night",
        normal_night_available=False,
    )

    assert keys.background_scene_type == "daytime_scene"
    assert keys.effective_scene_mode == "day"


def test_sick_state_forces_night_scene():
    keys = select_scene_asset_keys(PetState.SICK, "day")

    assert keys.pet_asset_key == "sick_pet"
    assert keys.background_scene_type == "night_scene"
    assert keys.effective_scene_mode == "night"


def test_evolved_state_forces_evolved_scene():
    keys = select_scene_asset_keys(PetState.EVOLVED, "night")

    assert keys.pet_asset_key == "evolved_pet"
    assert keys.background_scene_type == "evolved_scene"
    assert keys.effective_scene_mode == "evolved"


def test_load_scene_assets_returns_urls_when_assets_exist():
    repository = InMemoryPetRepository()
    repository.pet_assets["normal"] = AssetRecord(
        asset_key="normal_pet",
        url="https://example.test/normal_pet.png",
    )
    repository.background_assets["night_scene"] = AssetRecord(
        asset_key="night_scene",
        url="https://example.test/night_scene.png",
    )

    assets = load_scene_assets(repository, PetState.NORMAL, "night")

    assert assets.pet_image_url == "https://example.test/normal_pet.png"
    assert assets.background_image_url == "https://example.test/night_scene.png"
    assert assets.effective_scene_mode == "night"
    assert assets.error is None
    assert assets.has_images is True


def test_load_scene_assets_can_find_background_by_asset_key():
    repository = InMemoryPetRepository()
    repository.pet_assets["normal"] = AssetRecord(
        asset_key="normal_pet",
        url="https://example.test/normal_pet.png",
    )
    repository.background_assets["day"] = AssetRecord(
        asset_key="daytime_scene",
        url="https://example.test/daytime_scene.png",
    )
    repository.background_assets["night"] = AssetRecord(
        asset_key="night_scene",
        url="https://example.test/night_scene.png",
    )

    assets = load_scene_assets(repository, PetState.NORMAL, "day")

    assert assets.background_image_url == "https://example.test/daytime_scene.png"
    assert assets.error is None


def test_load_scene_assets_reports_missing_assets_for_fallback():
    repository = InMemoryPetRepository()

    assets = load_scene_assets(repository, PetState.NORMAL, "day")

    assert assets.has_images is False
    assert assets.error == "Missing active image asset(s): normal_pet, daytime_scene"


def test_load_pet_sprite_asset_uses_state_sprite():
    repository = InMemoryPetRepository()
    repository.pet_assets["evolved"] = AssetRecord(
        asset_key="evolved_pet",
        url="https://example.test/evolved_pet.png",
    )

    asset = load_pet_sprite_asset(repository, PetState.EVOLVED)

    assert asset.image_url == "https://example.test/evolved_pet.png"
    assert asset.error is None
    assert asset.has_image is True
