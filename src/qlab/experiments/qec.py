from __future__ import annotations

import numpy as np
import pymatching
import stim

from qlab.models import ExperimentResult


def logical_error_rate(*, distance: int, physical_error_rate: float, shots: int, seed: int) -> float:
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        distance=distance,
        rounds=distance,
        after_clifford_depolarization=physical_error_rate,
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matching = pymatching.Matching.from_detector_error_model(detector_error_model)
    sampler = circuit.compile_detector_sampler(seed=seed)
    detections, observables = sampler.sample(shots=shots, separate_observables=True)
    predictions = matching.decode_batch(detections)
    return float(np.mean(np.any(predictions != observables, axis=1)))


def run_qec(*, shots: int = 2_000, seed: int = 7) -> ExperimentResult:
    physical_error_rates = [0.001, 0.003, 0.01, 0.03]
    distances = [3, 5, 7]
    series: list[dict[str, float | int]] = []

    for distance in distances:
        for physical_error_rate in physical_error_rates:
            rate = logical_error_rate(
                distance=distance,
                physical_error_rate=physical_error_rate,
                shots=shots,
                seed=seed + distance,
            )
            series.append(
                {
                    "distance": distance,
                    "physical_error_rate": physical_error_rate,
                    "logical_error_rate": rate,
                }
            )

    low_noise_rows = [row for row in series if row["physical_error_rate"] == physical_error_rates[0]]
    return ExperimentResult.create(
        module="qec",
        experiment_id="repetition-code-memory",
        parameters={"distances": distances, "physical_error_rates": physical_error_rates, "shots": shots, "seed": seed},
        metrics={
            "best_logical_error_rate": min(float(row["logical_error_rate"]) for row in series),
            "distance_3_low_noise_error_rate": float(low_noise_rows[0]["logical_error_rate"]),
            "distance_7_low_noise_error_rate": float(low_noise_rows[-1]["logical_error_rate"]),
        },
        artifacts={"series": series, "note": "Repetition code corrects bit-flip-style errors; it is not a full surface-code experiment."},
    )
