# Tiny Tamagotchi MVP

## Supabase Image Assets

The status page keeps the existing Tamagotchi-style device layout, but the scene image layer is now driven by Supabase metadata:

- `src/data/repositories.py` reads active rows from `pet_assets` and `background_assets`.
- `asset_from_record()` resolves an asset URL by preferring `public_url`; if that is empty and `file_path` includes a bucket prefix, it asks the Supabase storage client for a public URL.
- `src/services/asset_service.py` owns the pure state-to-asset selection rules.
- `pages/1_Status.py` only renders the resolved URLs and falls back to the CSS placeholder scene if asset lookup fails.

State mapping:

- `normal` pet state uses `normal_pet`.
- `sick` pet state uses `sick_pet`.
- `evolved` pet state uses `evolved_pet`.

Background mapping:

- `normal` uses `daytime_scene` by default.
- `normal` may use `night_scene` when the scene selector is set to night and that asset exists.
- `sick` always uses `night_scene`.
- `evolved` always uses `evolved_scene`.
