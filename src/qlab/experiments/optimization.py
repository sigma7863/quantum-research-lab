from __future__ import annotations

from itertools import product

import numpy as np
import pennylane as qml

from qlab.models import ExperimentResult

EDGES = [(0, 1, 1.0), (0, 2, 1.0), (1, 2, 1.0), (1, 3, 1.0), (2, 3, 1.0)]


def cut_value(bits: tuple[int, ...]) -> float:
    return sum(weight for left, right, weight in EDGES if bits[left] != bits[right])


def run_optimization(*, layers: int = 2, steps: int = 30, seed: int = 17) -> ExperimentResult:
    wire_count = 4
    all_solutions = list(product((0, 1), repeat=wire_count))
    exact_solution = max(all_solutions, key=cut_value)
    exact_value = cut_value(exact_solution)
    random_baseline = float(np.mean([cut_value(bits) for bits in all_solutions]))

    cost_coefficients: list[float] = []
    cost_observables: list[qml.operation.Operator] = []
    for left, right, weight in EDGES:
        # Write each (I - ZiZj) term explicitly: qaoa.cost_layer only accepts
        # diagonal Pauli/identity terms, not a symbolic subtraction operator.
        cost_coefficients.extend([0.5 * weight, -0.5 * weight])
        cost_observables.extend([qml.Identity(0), qml.PauliZ(left) @ qml.PauliZ(right)])
    cost_hamiltonian = qml.Hamiltonian(cost_coefficients, cost_observables)
    mixer_hamiltonian = qml.Hamiltonian([1.0] * wire_count, [qml.PauliX(wire) for wire in range(wire_count)])
    device = qml.device("default.qubit", wires=wire_count)

    @qml.qnode(device, interface="autograd")
    def expectation(parameters: np.ndarray) -> float:
        for wire in range(wire_count):
            qml.Hadamard(wires=wire)
        for layer in range(layers):
            qml.qaoa.cost_layer(parameters[layer, 0], cost_hamiltonian)
            qml.qaoa.mixer_layer(parameters[layer, 1], mixer_hamiltonian)
        return qml.expval(cost_hamiltonian)

    @qml.qnode(device)
    def probabilities(parameters: np.ndarray) -> np.ndarray:
        for wire in range(wire_count):
            qml.Hadamard(wires=wire)
        for layer in range(layers):
            qml.qaoa.cost_layer(parameters[layer, 0], cost_hamiltonian)
            qml.qaoa.mixer_layer(parameters[layer, 1], mixer_hamiltonian)
        return qml.probs(wires=range(wire_count))

    rng = np.random.default_rng(seed)
    parameters = qml.numpy.array(rng.uniform(0.0, np.pi, size=(layers, 2)), requires_grad=True)
    optimizer = qml.AdamOptimizer(stepsize=0.12)
    history: list[float] = []
    for _ in range(steps):
        parameters, value = optimizer.step_and_cost(lambda values: -expectation(values), parameters)
        history.append(float(-value))

    optimized_expectation = float(expectation(parameters))
    probability_vector = probabilities(parameters)
    measured_index = int(np.argmax(probability_vector))
    measured_solution = tuple(int(bit) for bit in format(measured_index, "04b"))
    measured_value = cut_value(measured_solution)
    return ExperimentResult.create(
        module="optimization",
        experiment_id="weighted-max-cut-qaoa",
        parameters={"layers": layers, "steps": steps, "seed": seed, "edge_count": len(EDGES)},
        metrics={
            "qaoa_expected_cut": optimized_expectation,
            "best_sample_cut": measured_value,
            "exact_cut": exact_value,
            "random_baseline_cut": random_baseline,
            "approximation_ratio": measured_value / exact_value,
        },
        artifacts={
            "edges": [{"left": left, "right": right, "weight": weight} for left, right, weight in EDGES],
            "best_sample_bits": list(measured_solution),
            "exact_bits": list(exact_solution),
            "expectation_history": history,
            "note": "Exact enumeration is feasible only because this instance has four vertices."},
    )
