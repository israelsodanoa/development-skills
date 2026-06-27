from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


VALID_TASKS = """# Tasks: request

## Task T001: Add Plan Quality Constants

- Task: Add the shared constants used by plan validation.
- Outcome: Plan validation has stable required section and framework names.
- Exact Scope: Update only the common validator constants.
- Non-Scope: Engine approval logic and documentation updates.
- Size: XS
- Acceptance:
  - Required plan sections are represented by constants.
  - Framework IDs are represented by constants.
- Scenario:
  - Given a plan artifact with all required sections
  - When validation runs
  - Then framework coverage can be evaluated
- Verify: Run `python3 -m unittest discover tests` and inspect validation evidence.
- Dependencies: None.
- Files: `scripts/harness_common.py`
- Risk Notes: Constant names can drift from templates.
- Rollback/Repair: Revert the constant change or update template headings to match.
- Parallelization: Sequential.

## Task T002: Document Strict Task Gate

- Task: Document the strict task gate fields.
- Outcome: Agents can produce tasks that pass validation without trial and error.
- Exact Scope: Update the planning reference documentation.
- Non-Scope: Runtime validator behavior.
- Size: S
- Acceptance:
  - Required task fields are listed.
  - XS/S size expectations are explicit.
- Scenario:
  - Given an agent reads the planning reference
  - When it writes tasks.md
  - Then each task includes required validation fields
- Verify: Run `python3 -m unittest discover tests` and review documentation output.
- Dependencies: Task T001.
- Files: `references/planning-task-breakdown.md`
- Risk Notes: Docs can drift from validator constants.
- Rollback/Repair: Revert the doc change or update the validator/test contract.
- Parallelization: Parallel after validator field names are stable.
"""


class PlanningQualityWorkflowTest(unittest.TestCase):
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

    def request_path(self, request_id: str, filename: str) -> Path:
        return self.target / ".harness" / "requests" / request_id / filename

    def state(self, request_id: str) -> dict:
        return json.loads(self.request_path(request_id, "state.json").read_text(encoding="utf-8"))

    def create_request(self, title: str = "Planning quality") -> str:
        result = self.run_script(
            "request_engine.py",
            "create",
            "--target",
            str(self.target),
            "--title",
            title,
            "--objective",
            "Improve strict planning and task quality gates.",
        )
        return self.json_output(result)["request_id"]

    def record_required_answers(self, request_id: str) -> None:
        answers = {
            "objective": "Improve strict planning and task quality gates.",
            "task_type": "harness_improvement",
            "audience": "Harness agents and human operators.",
            "desired_outcome": "Planning and task artifacts block downstream work until detailed enough.",
            "success_criteria": "Plan quality validation passes\nTask quality validation passes",
            "non_goals": "No external dependencies",
            "constraints": "Use Python standard library only.",
            "permissions": "Always: edit harness scripts and docs\nAsk first: dependency additions\nNever: commit secrets",
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
        self.run_script("intake_engine.py", "complete", "--target", str(self.target), "--request-id", request_id)

    def prepare_spec_approved_request(self, title: str = "Planning quality") -> str:
        request_id = self.create_request(title)
        self.record_required_answers(request_id)
        self.run_script("spec_engine.py", "create", "--target", str(self.target), "--request-id", request_id)
        self.run_script("spec_engine.py", "approve", "--target", str(self.target), "--request-id", request_id)
        self.run_script("harness_state.py", "transition", "--target", str(self.target), "--request-id", request_id, "--to", "PLAN")
        return request_id

    def prepare_plan_approved_request(self, title: str = "Task quality") -> str:
        request_id = self.prepare_spec_approved_request(title)
        self.run_script("plan_engine.py", "create", "--target", str(self.target), "--request-id", request_id)
        self.run_script("plan_engine.py", "approve", "--target", str(self.target), "--request-id", request_id)
        self.run_script("harness_state.py", "transition", "--target", str(self.target), "--request-id", request_id, "--to", "TASKS")
        return request_id

    def test_plan_creation_includes_research_backed_sections(self) -> None:
        request_id = self.prepare_spec_approved_request()
        self.run_script("plan_engine.py", "create", "--target", str(self.target), "--request-id", request_id)

        plan = self.request_path(request_id, "plan.md").read_text(encoding="utf-8")
        self.assertIn("## Decomposition Map", plan)
        self.assertIn("## Dependency Graph", plan)
        self.assertIn("## Verification Matrix", plan)
        self.assertIn("## Premortem Risks", plan)
        self.assertIn("`wbs`", plan)
        self.assertIn("`cynefin`", plan)

    def test_plan_validation_and_approval_record_quality(self) -> None:
        request_id = self.prepare_spec_approved_request("Plan validation")
        self.run_script("plan_engine.py", "create", "--target", str(self.target), "--request-id", request_id)

        self.request_path(request_id, "plan.md").write_text(
            "# Plan: invalid\n\n## Overview\n\nOnly an overview.\n",
            encoding="utf-8",
        )
        invalid = self.json_output(
            self.run_script("plan_engine.py", "validate", "--target", str(self.target), "--request-id", request_id)
        )
        self.assertFalse(invalid["valid"])
        self.assertIn("Decomposition Map", invalid["missing_sections"])
        self.assertIn("Dependency Graph", invalid["missing_sections"])
        self.assertIn("Decision Records", invalid["missing_sections"])
        self.assertIn("Verification Matrix", invalid["missing_sections"])
        self.assertIn("Premortem Risks", invalid["missing_sections"])

        self.run_script("plan_engine.py", "create", "--target", str(self.target), "--request-id", request_id, "--force")
        valid = self.json_output(
            self.run_script("plan_engine.py", "validate", "--target", str(self.target), "--request-id", request_id)
        )
        self.assertTrue(valid["valid"])
        self.run_script("plan_engine.py", "approve", "--target", str(self.target), "--request-id", request_id)

        plan_quality = self.state(request_id)["planning_quality"]["plan"]
        self.assertEqual(plan_quality["status"], "valid")
        self.assertIn("wbs", plan_quality["frameworks"])
        self.assertIn("premortem", plan_quality["frameworks"])

    def test_task_validation_rejects_placeholder_oversized_and_missing_fields(self) -> None:
        request_id = self.prepare_plan_approved_request("Task invalid")
        tasks_path = self.request_path(request_id, "tasks.md")

        tasks_path.write_text(
            "# Tasks: invalid\n\n## Task T001: Replace Placeholder\n\n- Task: Replace with first implementation slice\n",
            encoding="utf-8",
        )
        placeholder = self.json_output(
            self.run_script("task_engine.py", "validate", "--target", str(self.target), "--request-id", request_id)
        )
        self.assertFalse(placeholder["valid"])
        self.assertTrue(any("placeholder" in problem for problem in placeholder["quality_problems"]))

        oversized = VALID_TASKS.replace("- Size: XS", "- Size: M", 1)
        tasks_path.write_text(oversized, encoding="utf-8")
        oversized_result = self.json_output(
            self.run_script("task_engine.py", "validate", "--target", str(self.target), "--request-id", request_id)
        )
        self.assertFalse(oversized_result["valid"])
        self.assertTrue(any("size must be XS or S" in problem for problem in oversized_result["quality_problems"]))

        missing = VALID_TASKS.replace("- Rollback/Repair: Revert the constant change or update template headings to match.\n", "", 1)
        tasks_path.write_text(missing, encoding="utf-8")
        missing_result = self.json_output(
            self.run_script("task_engine.py", "validate", "--target", str(self.target), "--request-id", request_id)
        )
        self.assertFalse(missing_result["valid"])
        self.assertTrue(any("Rollback/Repair" in problem for problem in missing_result["quality_problems"]))

    def test_valid_tasks_approval_records_quality(self) -> None:
        request_id = self.prepare_plan_approved_request("Task approval")
        self.request_path(request_id, "tasks.md").write_text(VALID_TASKS, encoding="utf-8")

        valid = self.json_output(
            self.run_script("task_engine.py", "validate", "--target", str(self.target), "--request-id", request_id)
        )
        self.assertTrue(valid["valid"])
        self.assertEqual(valid["task_count"], 2)

        self.run_script("task_engine.py", "approve", "--target", str(self.target), "--request-id", request_id)
        task_quality = self.state(request_id)["planning_quality"]["tasks"]
        self.assertEqual(task_quality["status"], "valid")
        self.assertEqual(task_quality["minimum_size"], "XS/S")
        self.assertEqual(task_quality["task_count"], 2)

    def test_transition_gates_reject_invalid_plan_and_tasks(self) -> None:
        plan_request = self.prepare_spec_approved_request("Invalid plan transition")
        self.request_path(plan_request, "plan.md").write_text(
            "# Plan: invalid\n\n## Overview\n\nMissing strict sections.\n",
            encoding="utf-8",
        )
        self.run_script("harness_state.py", "approve", "--target", str(self.target), "--request-id", plan_request, "--gate", "plan")
        blocked_tasks = self.run_script(
            "harness_state.py",
            "transition",
            "--target",
            str(self.target),
            "--request-id",
            plan_request,
            "--to",
            "TASKS",
            check=False,
        )
        self.assertNotEqual(blocked_tasks.returncode, 0)
        self.assertIn("plan.md is invalid", blocked_tasks.stderr)

        task_request = self.prepare_plan_approved_request("Invalid task transition")
        self.request_path(task_request, "tasks.md").write_text(
            "# Tasks: invalid\n\n## Task T001: Missing Fields\n\n- Task: This task omits strict fields.\n",
            encoding="utf-8",
        )
        self.run_script("harness_state.py", "approve", "--target", str(self.target), "--request-id", task_request, "--gate", "tasks")
        blocked_implement = self.run_script(
            "harness_state.py",
            "transition",
            "--target",
            str(self.target),
            "--request-id",
            task_request,
            "--to",
            "IMPLEMENT",
            check=False,
        )
        self.assertNotEqual(blocked_implement.returncode, 0)
        self.assertIn("tasks.md is invalid", blocked_implement.stderr)

    def test_plan_and_tasks_prompt_packets_include_quality_contracts(self) -> None:
        request_id = self.prepare_spec_approved_request("Prompt quality")
        plan_prompt = self.run_script("prompt_engine.py", "--target", str(self.target), "--request-id", request_id, "--phase", "plan", "--print")
        self.assertIn("WBS", plan_prompt.stdout)
        self.assertIn("Dependency graph", plan_prompt.stdout)
        self.assertIn("Decision records", plan_prompt.stdout)
        self.assertIn("Premortem", plan_prompt.stdout)
        self.assertIn("Cynefin", plan_prompt.stdout)
        self.assertIn("Verification Matrix", plan_prompt.stdout)

        tasks_prompt = self.run_script("prompt_engine.py", "--target", str(self.target), "--request-id", request_id, "--phase", "tasks", "--print")
        self.assertIn("XS/S", tasks_prompt.stdout)
        self.assertIn("atomic", tasks_prompt.stdout)
        self.assertIn("Acceptance", tasks_prompt.stdout)
        self.assertIn("Dependencies", tasks_prompt.stdout)
        self.assertIn("likely files", tasks_prompt.stdout)
        self.assertIn("Parallelization", tasks_prompt.stdout)


if __name__ == "__main__":
    unittest.main()
