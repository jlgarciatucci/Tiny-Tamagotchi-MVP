from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from typing import Any


class PetState(str, Enum):
    NORMAL = "normal"
    SICK = "sick"
    EVOLVED = "evolved"


class PetCharacter(str, Enum):
    ORIGINAL = "original"
    BEAGLE = "beagle"


class PetAction(str, Enum):
    FEED = "feed"
    PLAY = "play"
    REST = "rest"


class EventType(str, Enum):
    ACTION = "action"
    BECAME_SICK = "became_sick"
    RECOVERED = "recovered"
    EVOLVED = "evolved"
    TIME_ANOMALY = "time_anomaly"


class EvaluationSource(str, Enum):
    ACTION = "action"
    ELAPSED_TICK = "elapsed_tick"


@dataclass(frozen=True)
class StatBlock:
    hunger: int
    happiness: int
    energy: int

    def as_dict(self) -> dict[str, int]:
        return {
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
        }


@dataclass(frozen=True)
class StatDelta:
    hunger: int = 0
    happiness: int = 0
    energy: int = 0


@dataclass(frozen=True)
class Pet:
    id: str
    name: str
    state: PetState
    stats: StatBlock
    age_ticks: int
    is_evolved: bool
    evolved_at: datetime | None
    last_tick_at: datetime
    created_at: datetime
    updated_at: datetime
    sick_streak: int = 0
    recovery_streak: int = 0
    care_action_count: int = 0
    character: PetCharacter = PetCharacter.ORIGINAL

    @property
    def hunger(self) -> int:
        return self.stats.hunger

    @property
    def happiness(self) -> int:
        return self.stats.happiness

    @property
    def energy(self) -> int:
        return self.stats.energy

    def with_changes(self, **changes: Any) -> "Pet":
        return replace(self, **changes)

    def with_stats(self, stats: StatBlock, **changes: Any) -> "Pet":
        return replace(self, stats=stats, **changes)


@dataclass(frozen=True)
class PetEvent:
    event_type: EventType
    message: str
    created_at: datetime
    pet_id: str | None = None
    action: PetAction | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionResult:
    pet: Pet
    message: str
    events: tuple[PetEvent, ...]


@dataclass(frozen=True)
class TickResult:
    pet: Pet
    applied_ticks: int
    events: tuple[PetEvent, ...]


@dataclass(frozen=True)
class StateEvaluationResult:
    pet: Pet
    events: tuple[PetEvent, ...]
