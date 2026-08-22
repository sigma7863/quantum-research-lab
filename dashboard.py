from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from qlab.experiments import EXPERIMENTS
from qlab.storage import load_results, save_result

PROJECT_ROOT = Path(__file__).resolve().parent
WEB_ROOT = PROJECT_ROOT / "web"

MODULES = {
    "qec": {
        "name": "Error Correction",
        "description": "Repetition-code logical error rates under a circuit-noise model.",
    },
    "vqe": {
        "name": "Chemistry",
        "description": "A noisy H2 variational energy estimate against exact diagonalization.",
    },
    "optimization": {
        "name": "Optimization",
        "description": "A QAOA-style weighted Max-Cut experiment with exact and random baselines.",
    },
    "qml": {
        "name": "Quantum ML",
        "description": "Quantum-kernel classification alongside a classical RBF SVM.",
    },
    "pqc": {
        "name": "Post-Quantum Crypto",
        "description": "ML-KEM-512 and ML-DSA-44 local size and latency measurements.",
    },
}


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/results":
            self.send_json({"results": load_results(), "modules": MODULES})
            return
        if path in {"/", "/index.html"}:
            self.send_file(WEB_ROOT / "index.html", "text/html; charset=utf-8")
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        prefix = "/api/run/"
        if not path.startswith(prefix):
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        name = path.removeprefix(prefix)
        experiment = EXPERIMENTS.get(name)
        if experiment is None:
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown experiment")
            return

        try:
            result = experiment()
            result_path = save_result(result)
        except Exception as error:  # Keep the local UI actionable if a library fails.
            self.send_json({"error": str(error)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self.send_json({"result": result.to_dict(), "path": str(result_path)})

    def log_message(self, format: str, *args: object) -> None:
        print(f"[dashboard] {format % args}")

    def send_json(self, body: dict, *, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        payload = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Quantum Research Lab dashboard.")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DashboardHandler)
    print(f"Quantum Research Lab: http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
