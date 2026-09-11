from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SyntheticWorld:
    name: str
    true_function_present: bool | None
    observed_positive: bool
    complete_coverage: bool
    detection_adequate: bool
    missing_or_failed: bool


def classify(world: SyntheticWorld) -> str:
    if world.missing_or_failed:
        return "unresolved"
    if not world.complete_coverage:
        return "unresolved"
    if not world.detection_adequate:
        return "unresolved"
    if world.observed_positive:
        return "function_present"
    return "function_absent"


def qualification_worlds() -> list[SyntheticWorld]:
    return [
        SyntheticWorld("clear_positive_1", True, True, True, True, False),
        SyntheticWorld("clear_positive_2", True, True, True, True, False),
        SyntheticWorld("clear_positive_3", True, True, True, True, False),
        SyntheticWorld("clear_positive_4", True, True, True, True, False),
        SyntheticWorld("clear_negative_1", False, False, True, True, False),
        SyntheticWorld("clear_negative_2", False, False, True, True, False),
        SyntheticWorld("clear_negative_3", False, False, True, True, False),
        SyntheticWorld("clear_negative_4", False, False, True, True, False),
        SyntheticWorld("sparse_positive_missed", True, False, True, False, False),
        SyntheticWorld("partial_window_zero", None, False, False, True, False),
        SyntheticWorld("device_failure_zero", None, False, True, True, True),
        SyntheticWorld("retrieval_failure", None, False, False, False, True),
    ]


def score(worlds: list[SyntheticWorld]) -> dict[str, float | int | bool]:
    known = [w for w in worlds if w.true_function_present is not None]
    positive = [w for w in known if w.true_function_present]
    negative = [w for w in known if not w.true_function_present]

    tp = sum(classify(w) == "function_present" for w in positive)
    fn = sum(classify(w) == "function_absent" for w in positive)
    tn = sum(classify(w) == "function_absent" for w in negative)
    fp = sum(classify(w) == "function_present" for w in negative)

    sensitivity = tp / len(positive)
    false_negative_rate = fn / len(positive)
    specificity = tn / len(negative)
    unresolved_nonbiological = all(
        classify(w) == "unresolved"
        for w in worlds
        if w.missing_or_failed or not w.complete_coverage or not w.detection_adequate
    )
    return {
        "tp": tp,
        "fn": fn,
        "tn": tn,
        "fp": fp,
        "sensitivity": sensitivity,
        "false_negative_rate": false_negative_rate,
        "specificity": specificity,
        "unavailable_not_negative": unresolved_nonbiological,
        "passes": (
            sensitivity >= 0.8
            and false_negative_rate <= 0.2
            and specificity >= 0.95
            and unresolved_nonbiological
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(score(qualification_worlds()), indent=2, sort_keys=True))
