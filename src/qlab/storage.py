from __future__ import annotations

import json
from pathlib import Path

from qlab.models import ExperimentResult

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results"


def save_result(result: ExperimentResult) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = result.created_at.replace(":", "-").replace("+", "_")
    path = RESULTS_DIR / f"{timestamp}_{result.module}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_results() -> list[dict]:
    if not RESULTS_DIR.exists():
        return []

    loaded: list[dict] = []
    for path in sorted(RESULTS_DIR.glob("*.json"), reverse=True):
        try:
            loaded.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return loaded
