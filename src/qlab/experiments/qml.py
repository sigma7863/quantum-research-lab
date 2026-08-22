from __future__ import annotations

import numpy as np
import pennylane as qml
from sklearn.datasets import make_moons
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

from qlab.models import ExperimentResult


def run_qml(*, sample_count: int = 80, seed: int = 23) -> ExperimentResult:
    features, labels = make_moons(n_samples=sample_count, noise=0.17, random_state=seed)
    scaled_features = MinMaxScaler(feature_range=(0.0, np.pi)).fit_transform(features)
    train_x, test_x, train_y, test_y = train_test_split(
        scaled_features, labels, test_size=0.3, random_state=seed, stratify=labels
    )
    device = qml.device("default.qubit", wires=2)

    def embedding(vector: np.ndarray) -> None:
        qml.AngleEmbedding(vector, wires=range(2), rotation="Y")
        qml.CNOT(wires=[0, 1])
        qml.RZ(vector[0] * vector[1], wires=1)

    @qml.qnode(device)
    def kernel_circuit(left: np.ndarray, right: np.ndarray) -> float:
        embedding(left)
        qml.adjoint(embedding)(right)
        return qml.probs(wires=range(2))

    def quantum_kernel(left: np.ndarray, right: np.ndarray) -> float:
        return float(kernel_circuit(left, right)[0])

    train_kernel = np.array([[quantum_kernel(left, right) for right in train_x] for left in train_x])
    test_kernel = np.array([[quantum_kernel(left, right) for right in train_x] for left in test_x])
    quantum_model = SVC(kernel="precomputed").fit(train_kernel, train_y)
    quantum_predictions = quantum_model.predict(test_kernel)

    classical_model = SVC(kernel="rbf", gamma="scale").fit(train_x, train_y)
    classical_predictions = classical_model.predict(test_x)
    return ExperimentResult.create(
        module="qml",
        experiment_id="quantum-kernel-two-moons",
        parameters={"sample_count": sample_count, "train_count": len(train_x), "test_count": len(test_x), "seed": seed},
        metrics={
            "quantum_kernel_accuracy": float(accuracy_score(test_y, quantum_predictions)),
            "classical_rbf_svm_accuracy": float(accuracy_score(test_y, classical_predictions)),
            "accuracy_delta": float(accuracy_score(test_y, quantum_predictions) - accuracy_score(test_y, classical_predictions)),
        },
        artifacts={"note": "A small synthetic data test; accuracy is a comparison, not evidence of quantum advantage."},
    )
