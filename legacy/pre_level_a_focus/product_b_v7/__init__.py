"""Product-B v7 independent literature-witness answer-check prototype."""

from .preflight import (
    FIREWALLED_PAIR_IDS,
    FrameDeclaration,
    LiteratureWitness,
    LiteratureWitnessPreflight,
    WitnessFramePreflight,
    evaluate_literature_witness_preflight,
    validate_frame_declaration,
    validate_new_pair_id,
)

__all__ = [
    "FIREWALLED_PAIR_IDS",
    "FrameDeclaration",
    "LiteratureWitness",
    "LiteratureWitnessPreflight",
    "WitnessFramePreflight",
    "evaluate_literature_witness_preflight",
    "validate_frame_declaration",
    "validate_new_pair_id",
]
