# Research notes

This portfolio deliberately pairs every quantum method with a local baseline or a stated limit.

| Area | Local experiment | What it can tell you | What it cannot establish |
| --- | --- | --- | --- |
| Error correction | Repetition-code decoder under circuit noise | Logical-error trends across small code distances | Fault-tolerant threshold for a real device |
| Chemistry | Two-qubit H2 VQE | Optimization and noise sensitivity | Useful molecular-scale chemistry advantage |
| Optimization | Four-node Max-Cut QAOA | Variational behavior against exact enumeration | Performance on realistic industrial instances |
| QML | Quantum kernel versus RBF SVM | Feature-map behavior on a controlled dataset | A general quantum ML advantage |
| PQC | ML-KEM / ML-DSA local measurements | Key, ciphertext, signature sizes and local latency | Production security or network performance |

The five areas are connected but solve different problems. Error correction makes future large-scale quantum computation possible; chemistry, optimization, and QML are candidate applications; post-quantum cryptography prepares ordinary systems for the security implications of large-scale quantum computers.

Useful primary documentation: [Stim](https://github.com/quantumlib/Stim), [PennyLane chemistry](https://docs.pennylane.ai/en/stable/introduction/chemistry.html), [NIST PQC](https://csrc.nist.gov/Projects/Post-Quantum-Cryptography), and [IBM Quantum](https://www.ibm.com/roadmaps/quantum/2026/).
