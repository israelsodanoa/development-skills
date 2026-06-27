from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class IntakeWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name)
        self.run_script("init_project_harness.py", "--target", str(self.target), "--skip-sonar")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_script(self, script: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
        )
        if check and result.returncode != 0:
            self.fail(f"{script} failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        return result

    def json_output(self, result: subprocess.CompletedProcess[str]) -> dict:
        return json.loads(result.stdout)

    def create_request(self, title: str = "Interview test") -> str:
        result = self.run_script(
            "request_engine.py",
            "create",
            "--target",
            str(self.target),
            "--title",
            title,
            "--objective",
            "Improve intake before planning.",
        )
        return self.json_output(result)["request_id"]

    def state(self, request_id: str) -> dict:
        path = self.target / ".harness" / "requests" / request_id / "state.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def history(self, request_id: str) -> list[dict]:
        path = self.target / ".harness" / "requests" / request_id / "history.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def record_required_answers(self, request_id: str) -> None:
        answers = {
            "objective": "Improve request creation with a structured intake interview.",
            "task_type": "feature",
            "audience": "Codex agents and human operators using harness-development.",
            "desired_outcome": "Planning is blocked until implementation-ready requirements are captured.",
            "success_criteria": "Request creation creates intake.md\nSpec approval fails until intake is complete",
            "non_goals": "No external dependencies\nNo production integration",
            "constraints": "Use Python standard library only.",
            "permissions": "Always: read and write harness artifacts\nAsk first: Docker or external systems\nNever: commit secrets",
            "verification_expectations": "Run unittest discovery and compileall.",
        }
        for field, answer in answers.items():
            self.run_script(
                "intake_engine.py",
                "record",
                "--target",
                str(self.target),
                "--request-id",
                request_id,
                "--field",
                field,
                "--answer",
                answer,
            )

    def test_request_creation_initializes_intake(self) -> None:
        request_id = self.create_request()

        state = self.state(request_id)
        intake_path = self.target / ".harness" / "requests" / request_id / "intake.md"
        events = [event["type"] for event in self.history(request_id)]

        self.assertTrue(intake_path.exists())
        self.assertEqual(state["intake"]["status"], "incomplete")
        self.assertEqual(state["intake"]["task_type"], "unknown")
        self.assertIn("request.created", events)
        self.assertIn("intake.created", events)

        questions = self.json_output(
            self.run_script("intake_engine.py", "questions", "--target", str(self.target), "--request-id", request_id)
        )
        self.assertEqual(questions["batch"], "common")
        self.assertIn("objective", [question["field"] for question in questions["questions"]])
        self.assertEqual(len(self.state(request_id)["intake"]["question_rounds"]), 1)

    def test_intake_validation_passes_after_answers_or_waivers(self) -> None:
        answered_request = self.create_request("Answered intake")
        initial = self.json_output(
            self.run_script("intake_engine.py", "validate", "--target", str(self.target), "--request-id", answered_request)
        )
        self.assertFalse(initial["valid"])

        self.record_required_answers(answered_request)
        answered = self.json_output(
            self.run_script("intake_engine.py", "validate", "--target", str(self.target), "--request-id", answered_request)
        )
        self.assertTrue(answered["valid"])
        self.assertEqual(answered["status"], "incomplete")

        self.run_script("intake_engine.py", "complete", "--target", str(self.target), "--request-id", answered_request)
        self.assertEqual(self.state(answered_request)["intake"]["status"], "complete")

        waived_request = self.create_request("Waived intake")
        for field in self.state(waived_request)["intake"]["required_fields"]:
            self.run_script(
                "intake_engine.py",
                "record",
                "--target",
                str(self.target),
                "--request-id",
                waived_request,
                "--field",
                field,
                "--waive",
                "--reason",
                "Explicitly waived for this test.",
            )
        waived = self.json_output(
            self.run_script("intake_engine.py", "validate", "--target", str(self.target), "--request-id", waived_request)
        )
        self.assertTrue(waived["valid"])
        self.run_script("intake_engine.py", "complete", "--target", str(self.target), "--request-id", waived_request)
        self.assertEqual(self.state(waived_request)["intake"]["status"], "complete")

    def test_intake_blocks_spec_and_plan_until_complete(self) -> None:
        request_id = self.create_request()
        self.run_script("spec_engine.py", "create", "--target", str(self.target), "--request-id", request_id)

        approve = self.run_script("spec_engine.py", "approve", "--target", str(self.target), "--request-id", request_id, check=False)
        self.assertNotEqual(approve.returncode, 0)
        self.assertIn("intake is incomplete", approve.stderr)

        self.run_script("harness_state.py", "approve", "--target", str(self.target), "--request-id", request_id, "--gate", "spec")
        transition = self.run_script("harness_state.py", "transition", "--target", str(self.target), "--request-id", request_id, "--to", "PLAN", check=False)
        self.assertNotEqual(transition.returncode, 0)
        self.assertIn("intake is incomplete", transition.stderr)

        self.record_required_answers(request_id)
        self.run_script("intake_engine.py", "complete", "--target", str(self.target), "--request-id", request_id)
        self.run_script("harness_state.py", "transition", "--target", str(self.target), "--request-id", request_id, "--to", "PLAN")
        self.run_script("plan_engine.py", "create", "--target", str(self.target), "--request-id", request_id)

        blocked_tasks = self.run_script("task_engine.py", "create", "--target", str(self.target), "--request-id", request_id, check=False)
        self.assertNotEqual(blocked_tasks.returncode, 0)
        self.assertIn("Cannot create tasks.md", blocked_tasks.stderr)
        self.assertIn("plan gate", blocked_tasks.stderr)

        self.run_script("plan_engine.py", "approve", "--target", str(self.target), "--request-id", request_id)
        self.run_script("harness_state.py", "transition", "--target", str(self.target), "--request-id", request_id, "--to", "TASKS")
        self.run_script("task_engine.py", "create", "--target", str(self.target), "--request-id", request_id)

    def test_intake_prompt_phase_includes_required_contract(self) -> None:
        request_id = self.create_request()
        result = self.run_script("prompt_engine.py", "--target", str(self.target), "--request-id", request_id, "--phase", "intake", "--print")

        self.assertIn("Required output contract", result.stdout)
        self.assertIn("adaptive question", result.stdout)
        self.assertIn("Intake:", result.stdout)


if __name__ == "__main__":
    unittest.main()
