from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class ExperimentResult:
    module: str
    experiment_id: str
    parameters: dict[str, Any]
    metrics: dict[str, Any]
    artifacts: dict[str, Any]
    created_at: str

    @classmethod
    def create(
        cls,
        *,
        module: str,
        experiment_id: str,
        parameters: dict[str, Any],
        metrics: dict[str, Any],
        artifacts: dict[str, Any],
    ) -> "ExperimentResult":
        return cls(
            module=module,
            experiment_id=experiment_id,
            parameters=parameters,
            metrics=metrics,
            artifacts=artifacts,
            created_at=datetime.now(UTC).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
