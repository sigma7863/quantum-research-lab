from __future__ import annotations

import argparse
from collections.abc import Callable

from qlab.experiments import EXPERIMENTS
from qlab.models import ExperimentResult
from qlab.storage import save_result


def run_and_save(name: str, experiment: Callable[[], ExperimentResult]) -> None:
    result = experiment()
    path = save_result(result)
    print(f"{name}: saved {path}")
    for metric, value in result.metrics.items():
        print(f"  {metric}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local quantum-research experiments.")
    parser.add_argument("experiment", choices=[*EXPERIMENTS, "all"])
    args = parser.parse_args()

    selected = EXPERIMENTS.items() if args.experiment == "all" else [(args.experiment, EXPERIMENTS[args.experiment])]
    for name, experiment in selected:
        run_and_save(name, experiment)


if __name__ == "__main__":
    main()
