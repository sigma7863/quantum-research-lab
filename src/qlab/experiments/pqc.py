from __future__ import annotations

from time import perf_counter
from typing import Any

from pqcrypto.kem import ml_kem_512
from pqcrypto.sign import ml_dsa_44

from qlab.models import ExperimentResult


def milliseconds(function: Any, *args: Any) -> tuple[Any, float]:
    start = perf_counter()
    result = function(*args)
    return result, (perf_counter() - start) * 1_000


def run_pqc(*, iterations: int = 25) -> ExperimentResult:
    message = b"Quantum Research Lab benchmark message"
    kem_keypair, kem_keypair_ms = milliseconds(ml_kem_512.keygen)
    kem_public_key, kem_secret_key = kem_keypair
    kem_ciphertext_and_key, kem_encapsulation_ms = milliseconds(ml_kem_512.encaps, kem_public_key)
    kem_ciphertext, shared_key = kem_ciphertext_and_key
    recovered_key, kem_decapsulation_ms = milliseconds(ml_kem_512.decaps, kem_secret_key, kem_ciphertext)

    signing_keypair, signing_keypair_ms = milliseconds(ml_dsa_44.keygen)
    signing_public_key, signing_secret_key = signing_keypair
    signature, signing_ms = milliseconds(ml_dsa_44.sign, signing_secret_key, message)
    _, verify_ms = milliseconds(ml_dsa_44.verify, signing_public_key, message, signature)

    loop_start = perf_counter()
    for _ in range(iterations):
        public_key, secret_key = ml_kem_512.keygen()
        ciphertext, expected_key = ml_kem_512.encaps(public_key)
        assert ml_kem_512.decaps(secret_key, ciphertext) == expected_key
    kem_round_trip_ms = (perf_counter() - loop_start) * 1_000 / iterations

    return ExperimentResult.create(
        module="pqc",
        experiment_id="ml-kem-512-and-ml-dsa-44",
        parameters={"iterations": iterations},
        metrics={
            "kem_keypair_ms": kem_keypair_ms,
            "kem_encapsulation_ms": kem_encapsulation_ms,
            "kem_decapsulation_ms": kem_decapsulation_ms,
            "kem_round_trip_avg_ms": kem_round_trip_ms,
            "signature_keypair_ms": signing_keypair_ms,
            "signature_ms": signing_ms,
            "verify_ms": verify_ms,
            "kem_shared_key_matches": shared_key == recovered_key,
        },
        artifacts={
            "ml_kem_512_public_key_bytes": len(kem_public_key),
            "ml_kem_512_secret_key_bytes": len(kem_secret_key),
            "ml_kem_512_ciphertext_bytes": len(kem_ciphertext),
            "ml_dsa_44_public_key_bytes": len(signing_public_key),
            "ml_dsa_44_secret_key_bytes": len(signing_secret_key),
            "ml_dsa_44_signature_bytes": len(signature),
            "note": "Timing includes local library overhead and is not a production benchmark."},
    )
