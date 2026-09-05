from qlab.experiments.optimization import run_optimization
from qlab.experiments.pqc import run_pqc
from qlab.experiments.qec import run_qec
from qlab.experiments.qml import run_qml
from qlab.experiments.vqe import run_vqe


def test_qec_returns_a_logical_error_series() -> None:
    result = run_qec(shots=100, seed=3)
    assert result.module == "qec"
    assert len(result.artifacts["series"]) == 12
    assert 0.0 <= result.metrics["best_logical_error_rate"] <= 1.0


def test_vqe_tracks_the_exact_energy() -> None:
    result = run_vqe(steps=8, seed=3)
    assert result.module == "vqe"
    assert result.metrics["absolute_error_hartree"] < 1.0


def test_qaoa_beats_the_random_baseline_in_expectation() -> None:
    result = run_optimization(layers=1, steps=5, seed=3)
    assert result.module == "optimization"
    assert result.metrics["qaoa_expected_cut"] > result.metrics["random_baseline_cut"]


def test_quantum_kernel_returns_bounded_accuracy() -> None:
    result = run_qml(sample_count=30, seed=3)
    assert result.module == "qml"
    assert 0.0 <= result.metrics["quantum_kernel_accuracy"] <= 1.0


def test_post_quantum_primitives_round_trip() -> None:
    result = run_pqc(iterations=2)
    assert result.module == "pqc"
    assert result.metrics["kem_shared_key_matches"] is True
    assert result.artifacts["ml_dsa_44_signature_bytes"] > 0
