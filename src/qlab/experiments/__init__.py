from qlab.experiments.optimization import run_optimization
from qlab.experiments.pqc import run_pqc
from qlab.experiments.qec import run_qec
from qlab.experiments.qml import run_qml
from qlab.experiments.vqe import run_vqe

EXPERIMENTS = {
    "qec": run_qec,
    "vqe": run_vqe,
    "optimization": run_optimization,
    "qml": run_qml,
    "pqc": run_pqc,
}

__all__ = ["EXPERIMENTS", "run_optimization", "run_pqc", "run_qec", "run_qml", "run_vqe"]
