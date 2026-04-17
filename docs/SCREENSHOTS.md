# Screenshot Checklist

Use these files for the README images.

## 1. Supabase table relationship view

Save as:

```text
docs/images/supabase-table-relationships.png
```

Capture this in Supabase:

1. Open your Supabase project.
2. Go to `Database` -> `Schema Visualizer` or `Table Editor`.
3. Make sure these tables are visible:
   - `pets`
   - `pet_events`
   - `pet_assets`
   - `background_assets`
4. Make sure the relationship from `pet_events.pet_id` to `pets.id` is visible if using the visualizer.
5. Take the screenshot.

What the screenshot should prove:

- The four tables exist.
- `pets.id` is the primary key.
- `pet_events.pet_id` references `pets.id`.
- Asset metadata tables exist for pet sprites and background scenes.

## 2. Supabase Storage bucket view

Save as:

```text
docs/images/supabase-storage-assets.png
```

Capture this in Supabase:

1. Open `Storage`.
2. Show the bucket or buckets containing the uploaded PNGs.
3. Include these pet sprites in the view if possible:
   - `normal_pet.png`
   - `sick_pet.png`
   - `evolved_pet.png`
4. Include these backgrounds in the view if possible:
   - `daytime_scene.png`
   - `night_scene.png`
   - `evolved_scene.png`

What the screenshot should prove:

- The images are uploaded.
- The names match the asset metadata rows.
- The files are in the bucket paths used by `file_path`, or public URLs are available.

## 3. Running Streamlit status page

Save as:

```text
docs/images/streamlit-status-page.png
```

Capture this in the browser:

1. Run the app:

   ```powershell
   streamlit run app.py
   ```

2. Start or load a pet.
3. Go to the status page.
4. Wait until the real Supabase background and pet sprite are visible.
5. Capture the Tamagotchi device frame, speech bubble, stat panel, and action buttons.

What the screenshot should prove:

- The app is rendering a real background image from Supabase.
- The pet sprite is overlaid on top of the background.
- The existing UI style is preserved.
- Stats and action buttons are visible.

## 4. Architecture diagram

Already provided as:

```text
docs/images/app-backend-frontend-flow.svg
```

This diagram shows:

- Streamlit pages.
- Service layer.
- Domain engine and state machine.
- Repository layer.
- Supabase database and storage.

## 5. Schema diagram

Already provided as:

```text
docs/images/supabase-schema-diagram.svg
```

This diagram can be used when you want a clean repo-native schema graphic instead of a Supabase UI screenshot.
