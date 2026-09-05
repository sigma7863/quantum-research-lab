# Quantum Research Lab

Local, reproducible experiments across five practical quantum-computing research areas:

- Quantum error correction: repetition-code logical error rates with `stim` and `pymatching`
- Quantum chemistry: noisy and ideal H2 VQE energy estimation
- Quantum optimization: QAOA-style weighted Max-Cut against exact and random baselines
- Quantum machine learning: quantum kernel classification against a classical SVM
- Post-quantum cryptography: ML-KEM-512 and ML-DSA-44 key, signature, and latency measurements

The goal is not to claim quantum advantage. It is to make the assumptions, scale limits,
and classical baselines visible in a small research portfolio you can run locally.

## Setup

This project supports Python 3.11 and 3.12. `uv` creates an isolated environment and locks the
resolved dependency versions in `uv.lock`.

```bash
cd /Users/sigma7863/Documents/Codex/2026-08-15/record-and-replay-plugin-record-and/quantum-research-lab
uv sync --extra dev
```

## Run experiments

```bash
uv run quantum-lab all
uv run quantum-lab qec
uv run quantum-lab vqe
uv run quantum-lab optimization
uv run quantum-lab qml
uv run quantum-lab pqc
```

Each run writes one JSON record under `results/`. The schema is shared across modules:
`module`, `experiment_id`, `parameters`, `metrics`, `artifacts`, and `created_at`.

## Dashboard

```bash
uv run python dashboard.py
```

Open `http://127.0.0.1:8787` in a browser. The dashboard runs experiments, compares stored
results, and displays the assumptions behind each area. It is local-only and does not submit
jobs to a cloud quantum computer.

## Project layout

```
src/qlab/          Experiment modules, result schema, storage, and CLI
tests/             Fast deterministic smoke tests
web/               Dependency-free local dashboard
docs/              Research scope and interpretation notes
results/           Local run records (JSON is intentionally ignored by Git)
.github/workflows/ Continuous integration
```

## Verification

```bash
uv run pytest
```

## Research grounding

- [Google Quantum AI, error correction below threshold](https://www.nature.com/articles/s41586-024-08449-y)
- [IBM Quantum roadmap](https://www.ibm.com/roadmaps/quantum/2026/)
- [PennyLane quantum chemistry documentation](https://docs.pennylane.ai/en/stable/introduction/chemistry.html)
- [Qiskit Optimization documentation](https://qiskit-community.github.io/qiskit-optimization/)
- [NIST post-quantum cryptography project](https://csrc.nist.gov/Projects/Post-Quantum-Cryptography)
- [Stim stabilizer simulator](https://github.com/quantumlib/Stim)
