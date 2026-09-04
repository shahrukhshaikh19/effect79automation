"""Phase G certification framework tests."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
VALIDATION = REPO / "validation"


class CertificationFrameworkTests(unittest.TestCase):
    def test_contract_exists(self) -> None:
        path = REPO / "registry" / "FOUNDATION_CERTIFICATION.yaml"
        self.assertTrue(path.is_file())

    def test_evidence_index_exists(self) -> None:
        path = VALIDATION / "FOUNDATION_EVIDENCE_INDEX.yaml"
        self.assertTrue(path.is_file())

    def test_adversarial_validator_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VALIDATION / "validate_foundation_adversarial.py")],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)

    def _load_adversarial_json(self, stdout: str) -> dict:
        decoder = json.JSONDecoder()
        payload, _ = decoder.raw_decode(stdout.strip())
        return payload

    def test_adversarial_reports_twenty_core_scenarios(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VALIDATION / "validate_foundation_adversarial.py")],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
        payload = self._load_adversarial_json(proc.stdout)
        core = [s for s in payload["scenarios"] if re.fullmatch(r"G-A\d{2}", s["id"])]
        self.assertEqual(len(core), 20)

    def test_certify_runner_importable(self) -> None:
        runner = VALIDATION / "certify_foundation.py"
        self.assertTrue(runner.is_file())
        proc = subprocess.run(
            [sys.executable, str(runner), "--help"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--write-result", proc.stdout)


if __name__ == "__main__":
    unittest.main()
