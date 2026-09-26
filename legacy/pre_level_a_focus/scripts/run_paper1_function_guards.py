#!/usr/bin/env python3
"""Run the no-argument function-style Paper-1 guard tests without pytest.

The repository's historical CI uses unittest discovery. Several newer manuscript
boundary tests were written as top-level ``test_*`` functions, which unittest
correctly ignores. This runner makes those guards executable using only the
standard library, without changing the scientific state or requiring pytest.
"""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = [
    ROOT / "tests" / "test_paper1_v09_candidate_boundaries.py",
    ROOT / "tests" / "test_paper1_v09_display_sync.py",
    ROOT / "tests" / "test_paper1_v09_submission_hygiene.py",
    ROOT / "tests" / "test_paper1_v10_compression.py",
    ROOT / "tests" / "test_paper1_v10_final_submission.py",
]


def load_module(path: Path):
    name = f"paper1_guard_{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_file(path: Path) -> tuple[int, int]:
    if not path.exists():
        raise FileNotFoundError(path)
    mod = load_module(path)
    tests = []
    for name, obj in vars(mod).items():
        if not name.startswith("test_") or not callable(obj):
            continue
        sig = inspect.signature(obj)
        if len(sig.parameters) != 0:
            raise RuntimeError(f"Paper-1 guard requires arguments and cannot be run without pytest: {path}:{name}{sig}")
        tests.append((name, obj))

    if not tests:
        raise RuntimeError(f"no executable function guards found in {path}")

    passed = 0
    for name, func in sorted(tests):
        label = f"{path.name}::{name}"
        try:
            func()
        except Exception:
            print(f"FAIL {label}")
            traceback.print_exc()
        else:
            passed += 1
            print(f"PASS {label}")
    return passed, len(tests)


def main(argv: list[str]) -> int:
    paths = [Path(x).resolve() for x in argv] if argv else DEFAULT_FILES
    total_passed = 0
    total = 0
    for path in paths:
        passed, count = run_file(path)
        total_passed += passed
        total += count
    print(f"Paper-1 function guards: {total_passed}/{total} passed")
    return 0 if total_passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
