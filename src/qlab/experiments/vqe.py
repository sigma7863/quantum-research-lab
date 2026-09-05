from __future__ import annotations

import numpy as np
import pennylane as qml

from qlab.models import ExperimentResult


def hydrogen_hamiltonian() -> qml.Hamiltonian:
    coefficients = [-0.04207898, 0.17771287, 0.17771287, -0.24274281, 0.12293305, 0.16768319]
    observables = [
        qml.Identity(0),
        qml.PauliZ(0),
        qml.PauliZ(1),
        qml.PauliZ(0) @ qml.PauliZ(1),
        qml.PauliY(0) @ qml.PauliY(1),
        qml.PauliX(0) @ qml.PauliX(1),
    ]
    return qml.Hamiltonian(coefficients, observables)


def ansatz(parameters: np.ndarray, *, noisy: bool = False) -> None:
    qml.RY(parameters[0], wires=0)
    qml.RY(parameters[1], wires=1)
    if noisy:
        qml.DepolarizingChannel(0.005, wires=0)
        qml.DepolarizingChannel(0.005, wires=1)
    qml.CNOT(wires=[0, 1])
    if noisy:
        qml.DepolarizingChannel(0.005, wires=0)
        qml.DepolarizingChannel(0.005, wires=1)


def run_vqe(*, steps: int = 80, seed: int = 11) -> ExperimentResult:
    hamiltonian = hydrogen_hamiltonian()
    ideal_device = qml.device("default.qubit", wires=2)
    noisy_device = qml.device("default.mixed", wires=2)

    @qml.qnode(ideal_device, interface="autograd")
    def ideal_energy(parameters: np.ndarray) -> float:
        ansatz(parameters)
        return qml.expval(hamiltonian)

    @qml.qnode(noisy_device)
    def noisy_energy(parameters: np.ndarray) -> float:
        ansatz(parameters, noisy=True)
        return qml.expval(hamiltonian)

    rng = np.random.default_rng(seed)
    parameters = qml.numpy.array(rng.normal(0.0, 0.2, size=2), requires_grad=True)
    optimizer = qml.GradientDescentOptimizer(stepsize=0.25)
    history: list[float] = []
    for _ in range(steps):
        parameters, energy = optimizer.step_and_cost(ideal_energy, parameters)
        history.append(float(energy))

    optimized_energy = float(ideal_energy(parameters))
    exact_energy = float(np.linalg.eigvalsh(qml.matrix(hamiltonian)).min())
    noisy_optimized_energy = float(noisy_energy(parameters))
    return ExperimentResult.create(
        module="vqe",
        experiment_id="h2-minimal-basis-vqe",
        parameters={"steps": steps, "seed": seed, "ansatz_parameters": [float(value) for value in parameters]},
        metrics={
            "ideal_energy_hartree": optimized_energy,
            "exact_energy_hartree": exact_energy,
            "absolute_error_hartree": abs(optimized_energy - exact_energy),
            "noisy_energy_hartree": noisy_optimized_energy,
            "noise_penalty_hartree": noisy_optimized_energy - optimized_energy,
        },
        artifacts={"energy_history_hartree": history, "note": "A two-qubit pedagogical H2 Hamiltonian, not a production chemistry workflow."},
    )
