from __future__ import annotations

from src.domain.pet_types import PetState


STATE_LABELS: dict[PetState, str] = {
    PetState.NORMAL: "Normal",
    PetState.SICK: "Sick",
    PetState.EVOLVED: "Evolved",
}

STATE_AVATARS: dict[PetState, str] = {
    PetState.NORMAL: "(=^.^=)",
    PetState.SICK: "(x.x)",
    PetState.EVOLVED: "<(=^o^=)>",
}

STATE_CAPTIONS: dict[PetState, str] = {
    PetState.NORMAL: "Steady paws, bright eyes.",
    PetState.SICK: "Needs balanced care and a gentle pace.",
    PetState.EVOLVED: "A tiny milestone with a big glow.",
}
