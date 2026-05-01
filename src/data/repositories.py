from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

from src.domain.pet_engine import clamp_stats
from src.domain.pet_types import (
    EventType,
    Pet,
    PetAction,
    PetCharacter,
    PetEvent,
    PetState,
    StatBlock,
)


ACTIVE_PET_ID = "active-pet"


class RepositoryError(RuntimeError):
    pass


class InvalidPetRecordError(ValueError):
    pass


@dataclass(frozen=True)
class AssetRecord:
    asset_key: str
    url: str
    file_path: str | None = None
    width: int | None = None
    height: int | None = None


class PetRepository(Protocol):
    def fetch_active_pet(self) -> Pet | None:
        ...

    def upsert_pet(self, pet: Pet) -> None:
        ...

    def append_events(self, events: tuple[PetEvent, ...]) -> None:
        ...

    def delete_events_for_pet(self, pet_id: str) -> None:
        ...

    def list_recent_events(self, pet_id: str, *, limit: int = 20) -> tuple[PetEvent, ...]:
        ...

    def fetch_active_pet_asset(
        self,
        state: str,
        character: str = PetCharacter.ORIGINAL.value,
    ) -> AssetRecord | None:
        ...

    def fetch_active_background_asset(self, scene_type: str) -> AssetRecord | None:
        ...


class SupabasePetRepository:
    def __init__(self, client: Any) -> None:
        self._client = client

    def fetch_active_pet(self) -> Pet | None:
        try:
            response = (
                self._client.table("pets")
                .select("*")
                .eq("id", ACTIVE_PET_ID)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError(
                f"Could not load pet from Supabase. {_format_supabase_error(exc)}"
            ) from exc

        rows = response.data or []
        if not rows:
            return None
        return pet_from_record(rows[0])

    def upsert_pet(self, pet: Pet) -> None:
        try:
            self._client.table("pets").upsert(pet_to_record(pet)).execute()
        except Exception as exc:
            raise RepositoryError(
                f"Could not save pet to Supabase. {_format_supabase_error(exc)}"
            ) from exc

    def append_events(self, events: tuple[PetEvent, ...]) -> None:
        if not events:
            return
        try:
            self._client.table("pet_events").insert(
                [event_to_record(event) for event in events]
            ).execute()
        except Exception as exc:
            raise RepositoryError(
                f"Could not append pet events to Supabase. {_format_supabase_error(exc)}"
            ) from exc

    def delete_events_for_pet(self, pet_id: str) -> None:
        try:
            self._client.table("pet_events").delete().eq("pet_id", pet_id).execute()
        except Exception as exc:
            raise RepositoryError(
                f"Could not clear pet events from Supabase. {_format_supabase_error(exc)}"
            ) from exc

    def list_recent_events(self, pet_id: str, *, limit: int = 20) -> tuple[PetEvent, ...]:
        try:
            response = (
                self._client.table("pet_events")
                .select("*")
                .eq("pet_id", pet_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError(
                f"Could not load pet events from Supabase. {_format_supabase_error(exc)}"
            ) from exc

        events = tuple(event_from_record(row) for row in response.data or [])
        return tuple(reversed(events))

    def fetch_active_pet_asset(
        self,
        state: str,
        character: str = PetCharacter.ORIGINAL.value,
    ) -> AssetRecord | None:
        try:
            response = (
                self._client.table("pet_assets")
                .select("*")
                .eq("state", state)
                .eq("is_active", True)
                .execute()
            )
        except Exception as exc:
            raise RepositoryError(
                f"Could not load pet asset from Supabase. {_format_supabase_error(exc)}"
            ) from exc

        rows = response.data or []
        if not rows:
            return None
        selected = _select_pet_asset_record(rows, state, character)
        if selected is None:
            base_row = _select_pet_asset_record(
                rows,
                state,
                PetCharacter.ORIGINAL.value,
            )
            selected = _infer_pet_asset_record(base_row or rows[0], state, character)
        if selected is None:
            return None
        return asset_from_record(selected, self._client)

    def fetch_active_background_asset(self, scene_type: str) -> AssetRecord | None:
        try:
            response = self._fetch_background_asset_response("scene_type", scene_type)
            rows = response.data or []
            if not rows:
                response = self._fetch_background_asset_response("asset_key", scene_type)
        except Exception as exc:
            raise RepositoryError(
                f"Could not load background asset from Supabase. {_format_supabase_error(exc)}"
            ) from exc

        rows = response.data or []
        if not rows:
            return None
        return asset_from_record(rows[0], self._client)

    def _fetch_background_asset_response(self, field: str, value: str) -> Any:
        return (
            self._client.table("background_assets")
            .select("*")
            .eq(field, value)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )


class InMemoryPetRepository:
    def __init__(self) -> None:
        self.pet: Pet | None = None
        self.events: list[PetEvent] = []
        self.pet_assets: dict[str, AssetRecord] = {}
        self.background_assets: dict[str, AssetRecord] = {}

    def fetch_active_pet(self) -> Pet | None:
        return self.pet

    def upsert_pet(self, pet: Pet) -> None:
        self.pet = pet

    def append_events(self, events: tuple[PetEvent, ...]) -> None:
        self.events.extend(events)

    def delete_events_for_pet(self, pet_id: str) -> None:
        self.events = [event for event in self.events if event.pet_id != pet_id]

    def list_recent_events(self, pet_id: str, *, limit: int = 20) -> tuple[PetEvent, ...]:
        matching = [event for event in self.events if event.pet_id == pet_id]
        return tuple(matching[-limit:])

    def fetch_active_pet_asset(
        self,
        state: str,
        character: str = PetCharacter.ORIGINAL.value,
    ) -> AssetRecord | None:
        character_key = _normalize_pet_character_value(character)
        return self.pet_assets.get(f"{character_key}:{state}") or (
            self.pet_assets.get(state)
            if character_key == PetCharacter.ORIGINAL.value
            else None
        )

    def fetch_active_background_asset(self, scene_type: str) -> AssetRecord | None:
        for asset in self.background_assets.values():
            if asset.asset_key == scene_type:
                return asset
        return self.background_assets.get(scene_type)


def pet_to_record(pet: Pet) -> dict[str, Any]:
    return {
        "id": pet.id,
        "name": pet.name,
        "state": pet.state.value,
        "hunger": pet.hunger,
        "happiness": pet.happiness,
        "energy": pet.energy,
        "age_ticks": pet.age_ticks,
        "is_evolved": pet.is_evolved,
        "evolved_at": _format_datetime(pet.evolved_at),
        "last_tick_at": _format_datetime(pet.last_tick_at),
        "created_at": _format_datetime(pet.created_at),
        "updated_at": _format_datetime(pet.updated_at),
        "sick_streak": pet.sick_streak,
        "recovery_streak": pet.recovery_streak,
        "care_action_count": pet.care_action_count,
    }


def pet_from_record(record: dict[str, Any]) -> Pet:
    required = (
        "id",
        "name",
        "state",
        "hunger",
        "happiness",
        "energy",
        "age_ticks",
        "is_evolved",
        "last_tick_at",
        "created_at",
        "updated_at",
    )
    missing = [field for field in required if field not in record]
    if missing:
        raise InvalidPetRecordError(f"Pet record is missing required fields: {missing}")

    state = _parse_pet_state(record["state"])
    stats = clamp_stats(
        StatBlock(
            hunger=_parse_int_field(record, "hunger"),
            happiness=_parse_int_field(record, "happiness"),
            energy=_parse_int_field(record, "energy"),
        )
    )
    return Pet(
        id=str(record["id"]),
        name=str(record["name"]),
        character=PetCharacter.ORIGINAL,
        state=state,
        stats=stats,
        age_ticks=max(0, _parse_int_field(record, "age_ticks")),
        is_evolved=_parse_bool_field(record, "is_evolved"),
        evolved_at=_parse_optional_datetime_field(record, "evolved_at"),
        last_tick_at=_parse_datetime_field(record, "last_tick_at"),
        created_at=_parse_datetime_field(record, "created_at"),
        updated_at=_parse_datetime_field(record, "updated_at"),
        sick_streak=max(0, _parse_optional_int_field(record, "sick_streak")),
        recovery_streak=max(0, _parse_optional_int_field(record, "recovery_streak")),
        care_action_count=max(0, _parse_optional_int_field(record, "care_action_count")),
    )


def event_to_record(event: PetEvent) -> dict[str, Any]:
    return {
        "pet_id": event.pet_id,
        "event_type": event.event_type.value,
        "event_message": event.message,
        "action": event.action.value if event.action else None,
        "payload_json": event.payload,
        "created_at": _format_datetime(event.created_at),
    }


def event_from_record(record: dict[str, Any]) -> PetEvent:
    try:
        action = record.get("action")
        return PetEvent(
            event_type=EventType(record["event_type"]),
            pet_id=record.get("pet_id"),
            action=PetAction(action) if action else None,
            message=str(record.get("event_message") or ""),
            payload=dict(record.get("payload_json") or {}),
            created_at=_parse_datetime(record["created_at"]),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise InvalidPetRecordError("Pet event record contains invalid values.") from exc


def asset_from_record(record: dict[str, Any], client: Any | None = None) -> AssetRecord:
    asset_key = str(record.get("asset_key") or "")
    file_path = record.get("file_path")
    url = _resolve_asset_url(record, client)
    if not asset_key:
        raise InvalidPetRecordError("Asset record is missing asset_key.")
    if not url:
        raise InvalidPetRecordError(f"Asset record has no usable URL: {asset_key}")

    return AssetRecord(
        asset_key=asset_key,
        url=url,
        file_path=str(file_path) if file_path else None,
        width=_parse_optional_int_value(record.get("width")),
        height=_parse_optional_int_value(record.get("height")),
    )


def _parse_pet_state(value: Any) -> PetState:
    try:
        return PetState(value)
    except ValueError as exc:
        raise InvalidPetRecordError(f"Invalid pet state value: {value!r}") from exc


def _parse_int_field(record: dict[str, Any], field: str) -> int:
    try:
        return int(record[field])
    except (TypeError, ValueError) as exc:
        raise InvalidPetRecordError(
            f"Invalid integer value for pets.{field}: {record.get(field)!r}"
        ) from exc


def _parse_optional_int_field(record: dict[str, Any], field: str) -> int:
    value = record.get(field)
    if value in (None, ""):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidPetRecordError(
            f"Invalid integer value for pets.{field}: {value!r}"
        ) from exc


def _parse_optional_int_value(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidPetRecordError(f"Invalid asset dimension value: {value!r}") from exc


def _parse_bool_field(record: dict[str, Any], field: str) -> bool:
    value = record[field]
    try:
        return _parse_bool(value)
    except ValueError as exc:
        raise InvalidPetRecordError(
            f"Invalid boolean value for pets.{field}: {value!r}"
        ) from exc


def _parse_datetime_field(record: dict[str, Any], field: str) -> datetime:
    value = record[field]
    try:
        return _parse_datetime(value)
    except ValueError as exc:
        raise InvalidPetRecordError(
            f"Invalid timestamp value for pets.{field}: {value!r}"
        ) from exc


def _parse_optional_datetime_field(record: dict[str, Any], field: str) -> datetime | None:
    value = record.get(field)
    try:
        return _parse_optional_datetime(value)
    except ValueError as exc:
        raise InvalidPetRecordError(
            f"Invalid timestamp value for pets.{field}: {value!r}"
        ) from exc


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat()


def _parse_optional_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    return _parse_datetime(value)


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(_normalize_iso_timestamp(value))
    else:
        raise ValueError("Expected datetime or ISO timestamp.")

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    raise ValueError("Expected boolean value.")


def _format_supabase_error(exc: Exception) -> str:
    details: list[str] = []
    for attr in ("message", "details", "hint", "code"):
        value = getattr(exc, attr, None)
        if value:
            details.append(str(value))

    if details:
        return " ".join(details)

    text = str(exc).strip()
    return text or exc.__class__.__name__


def _normalize_iso_timestamp(value: str) -> str:
    normalized = value.strip().replace("Z", "+00:00")
    return re.sub(
        r"\.(\d{1,9})([+-]\d{2}:\d{2})$",
        _normalize_fractional_seconds,
        normalized,
    )


def _normalize_fractional_seconds(match: re.Match[str]) -> str:
    fraction = match.group(1)[:6].ljust(6, "0")
    offset = match.group(2)
    return f".{fraction}{offset}"


def _resolve_asset_url(record: dict[str, Any], client: Any | None = None) -> str | None:
    public_url = record.get("public_url")
    if public_url:
        return str(public_url)

    file_path = record.get("file_path")
    if not file_path:
        return None

    path = str(file_path)
    if path.startswith(("http://", "https://")):
        return path

    if client is None or "/" not in path:
        return None

    bucket, object_path = path.split("/", 1)
    try:
        return str(client.storage.from_(bucket).get_public_url(object_path))
    except Exception:
        return None


def _select_pet_asset_record(
    rows: list[dict[str, Any]],
    state: str,
    character: str,
) -> dict[str, Any] | None:
    normalized_character = _normalize_pet_character_value(character)
    candidates = _pet_asset_candidates(state, normalized_character)
    for row in rows:
        searchable = " ".join(
            str(row.get(field) or "").lower()
            for field in ("asset_key", "file_path", "public_url")
        )
        if any(candidate in searchable for candidate in candidates):
            return row

    if normalized_character == PetCharacter.ORIGINAL.value:
        return rows[0]
    return None


def _infer_pet_asset_record(
    base_row: dict[str, Any],
    state: str,
    character: str,
) -> dict[str, Any] | None:
    normalized_character = _normalize_pet_character_value(character)
    if normalized_character != PetCharacter.BEAGLE.value:
        return None

    filename = f"beagle_{state}.png"
    asset_key = f"beagle_{state}"
    record = dict(base_row)
    record["asset_key"] = asset_key

    public_url = record.get("public_url")
    file_path = record.get("file_path")
    if public_url:
        updated_url = _replace_asset_filename(str(public_url), filename)
        if updated_url:
            record["public_url"] = updated_url
            return record

    if file_path:
        updated_path = _replace_asset_filename(str(file_path), filename)
        if updated_path:
            record["file_path"] = updated_path
            record["public_url"] = None
            return record

    return None


def _pet_asset_candidates(state: str, character: str) -> tuple[str, ...]:
    if character == PetCharacter.BEAGLE.value:
        file_stem = f"beagle_{state}"
        if state == PetState.EVOLVED.value:
            return (
                file_stem,
                f"{file_stem}.png",
                f"{file_stem}.ppng",
            )
        return (
            file_stem,
            f"{file_stem}.png",
        )

    return (
        f"{state}_pet",
        f"{state}_pet.png",
    )


def _normalize_pet_character_value(value: Any) -> str:
    try:
        return PetCharacter(value or PetCharacter.ORIGINAL.value).value
    except ValueError:
        return PetCharacter.ORIGINAL.value


def _replace_asset_filename(path: str, filename: str) -> str | None:
    cleaned = path.strip()
    if "/" not in cleaned:
        return None
    prefix, _ = cleaned.rsplit("/", 1)
    return f"{prefix}/{filename}"
