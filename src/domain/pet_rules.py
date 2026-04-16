from __future__ import annotations

from datetime import timedelta

from src.domain.pet_types import PetAction, PetState, StatBlock, StatDelta


SUPPORTED_STATES: tuple[PetState, ...] = (
    PetState.NORMAL,
    PetState.SICK,
    PetState.EVOLVED,
)

SUPPORTED_ACTIONS: tuple[PetAction, ...] = (
    PetAction.FEED,
    PetAction.PLAY,
    PetAction.REST,
)

STAT_MIN = 0
STAT_MAX = 100

DEFAULT_STATS = StatBlock(hunger=80, happiness=80, energy=80)
DEFAULT_AGE_TICKS = 0

MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 20

TICK_DURATION = timedelta(minutes=5)
MAX_OFFLINE_TICKS = 72

TICK_DECAY = StatDelta(hunger=-4, happiness=-3, energy=-2)

ACTION_EFFECTS: dict[PetAction, StatDelta] = {
    PetAction.FEED: StatDelta(hunger=18, happiness=4, energy=0),
    PetAction.PLAY: StatDelta(hunger=-4, happiness=16, energy=-8),
    PetAction.REST: StatDelta(hunger=-2, happiness=-3, energy=20),
}

SICK_STAT_THRESHOLD = 25
SICK_STAT_COUNT = 2
SICK_STREAK_THRESHOLD = 2

RECOVERY_STAT_THRESHOLD = 40
RECOVERY_STREAK_THRESHOLD = 2

EVOLUTION_MIN_AGE_TICKS = 12
EVOLUTION_MIN_STAT = 70
EVOLUTION_MIN_CARE_ACTIONS = 6

SNACK_ATTACK_WINDOW = timedelta(minutes=10)
SNACK_ATTACK_FEED_COUNT = 3

ACTION_MESSAGES: dict[PetAction, str] = {
    PetAction.FEED: "Snack time! Tiny belly feels steadier.",
    PetAction.PLAY: "A little play made the room brighter.",
    PetAction.REST: "A quiet rest helped the tiny paws recharge.",
}

SNACK_ATTACK_MESSAGE = "Tiny tummy alert... that was a lot of snacks!"
TIRED_PLAY_MESSAGE = "I'm playing, but I could really use a nap..."
COZY_REST_MESSAGE = "That nap fixed everything. Almost."

STATE_EVENT_MESSAGES = {
    "became_sick": "Your tiny friend is feeling sick and needs balanced care.",
    "recovered_normal": "Your tiny friend is feeling better again.",
    "recovered_evolved": "Your evolved pal is back to glowing health.",
    "evolved": "Something changed... your tiny friend evolved!",
    "future_tick": "The saved clock was ahead, so no time decay was applied.",
}
