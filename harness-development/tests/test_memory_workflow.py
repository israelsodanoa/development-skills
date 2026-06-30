from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class MemoryWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name)
        self.run_script("init_project_harness.py", "--target", str(self.target), "--skip-sonar")
        self.request_id = self.create_request()

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

    def create_request(self) -> str:
        result = self.run_script(
            "request_engine.py",
            "create",
            "--target",
            str(self.target),
            "--title",
            "Memory workflow",
            "--objective",
            "Improve memory lifecycle controls.",
        )
        return self.json_output(result)["request_id"]

    def state(self) -> dict:
        path = self.target / ".harness" / "requests" / self.request_id / "state.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def history(self) -> list[dict]:
        path = self.target / ".harness" / "requests" / self.request_id / "history.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def memory_index(self) -> dict:
        path = self.target / ".harness" / "memory" / "memory-index.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_request_state_and_scaffold_define_memory_lifecycle(self) -> None:
        state = self.state()
        index = self.memory_index()

        self.assertIn("memory", state)
        self.assertIn("retrieved_sources", state["memory"]["working"])
        self.assertIn("reflections", state["memory"]["episodic"])
        self.assertIn("promotions", state["memory"]["long_term"])
        self.assertTrue(state["memory"]["policy"]["promotion_requires_evidence"])
        self.assertIn("context_budget", state["memory"]["working"])
        self.assertIn("context_ledger", state["memory"]["working"])
        self.assertEqual(state["memory"]["working"]["context_budget"]["estimator"], "approx_chars_div_4")
        self.assertTrue(state["memory"]["policy"]["context_economy"]["prefer_paths_and_summaries"])

        model = index["memory_model"]
        self.assertEqual(model["working_memory"], ".harness/requests/<request_id>/state.json")
        self.assertEqual(model["episodic_memory"], ".harness/requests/<request_id>/history.jsonl")
        self.assertIn("architecture", model["semantic_memory"])
        self.assertIn(".harness/memory/known-failures.json", model["procedural_memory"])
        self.assertTrue(model["policy"]["context_economy"]["record_token_estimates"])
        self.assertEqual(index["context_economy"]["default_budget"]["estimator"], "approx_chars_div_4")
        self.assertIsInstance(index["promotion_log"], list)
        self.assertIsInstance(index["pruning_log"], list)

    def test_memory_lifecycle_commands_record_auditable_state(self) -> None:
        self.run_script(
            "memory_engine.py",
            "retrieve",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--source",
            ".harness/memory/memory-index.json",
            "--reason",
            "Project memory before implementation.",
            "--memory-type",
            "semantic",
            "--priority",
            "high",
            "--inclusion",
            "summary",
            "--placement",
            "stable-prefix",
            "--cache-scope",
            "stable",
            "--summary",
            "Compact project memory map.",
        )
        self.run_script(
            "memory_engine.py",
            "retrieve",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--source",
            "docs/obsolete.md",
            "--reason",
            "Out of scope for this request.",
            "--status",
            "skipped",
            "--memory-type",
            "semantic",
        )
        self.run_script(
            "memory_engine.py",
            "reflect",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--summary",
            "Record selected and skipped sources before implementation.",
            "--lesson-type",
            "procedural",
            "--evidence",
            "memory_engine retrieve output",
            "--confidence",
            "high",
        )
        self.run_script(
            "memory_engine.py",
            "promote",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--kind",
            "semantic",
            "--section",
            "decisions",
            "--summary",
            "Use file-backed memory lifecycle records.",
            "--source",
            "state-memory reference",
            "--evidence",
            "memory workflow test",
            "--confidence",
            "high",
        )
        self.run_script(
            "memory_engine.py",
            "promote",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--kind",
            "control-gap",
            "--gap-type",
            "memory-control",
            "--summary",
            "Missing memory retrieval evidence can mislead future agents.",
            "--source",
            "workflow review",
            "--evidence",
            "memory workflow test",
        )
        self.run_script(
            "memory_engine.py",
            "prune",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--artifact",
            "index",
            "--entry-id",
            "decisions:old-note",
            "--reason",
            "Superseded by evidence-backed memory lifecycle records.",
            "--replacement",
            "decisions:Use file-backed memory lifecycle records.",
        )

        state = self.state()
        memory = state["memory"]
        self.assertEqual(len(memory["working"]["retrieved_sources"]), 1)
        self.assertEqual(len(memory["working"]["skipped_sources"]), 1)
        self.assertEqual(len(memory["episodic"]["reflections"]), 1)
        self.assertEqual(len(memory["long_term"]["promotions"]), 2)
        self.assertEqual(len(memory["long_term"]["pruning_log"]), 1)
        self.assertEqual(state["context_sources"][0]["path"], ".harness/memory/memory-index.json")
        self.assertEqual(state["context_sources"][0]["priority"], "high")
        self.assertGreater(state["context_sources"][0]["token_estimate"], 0)
        self.assertEqual(memory["working"]["context_ledger"]["selected"][0]["inclusion"], "summary")
        self.assertEqual(memory["working"]["context_ledger"]["selected"][0]["placement"], "stable-prefix")
        self.assertEqual(memory["working"]["context_ledger"]["selected"][0]["cache_scope"], "stable")
        self.assertGreater(memory["working"]["context_budget"]["current_selected_tokens"], 0)

        index = self.memory_index()
        self.assertTrue(any(item.get("summary") == "Use file-backed memory lifecycle records." for item in index["decisions"]))
        self.assertEqual(index["pruning_log"][0]["entry_id"], "decisions:old-note")

        gaps = json.loads((self.target / ".harness" / "memory" / "control-gaps.json").read_text(encoding="utf-8"))
        self.assertEqual(gaps["gaps"][0]["type"], "memory-control")

        event_types = [event["type"] for event in self.history()]
        self.assertIn("memory.retrieve.selected", event_types)
        self.assertIn("memory.retrieve.skipped", event_types)
        self.assertIn("memory.reflected", event_types)
        self.assertIn("memory.promoted", event_types)
        self.assertIn("memory.pruned", event_types)

    def test_prompt_packet_includes_memory_guardrails(self) -> None:
        self.run_script(
            "memory_engine.py",
            "retrieve",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--source",
            ".harness/memory/memory-index.json",
            "--reason",
            "Prompt packet should expose selected context.",
            "--memory-type",
            "semantic",
            "--priority",
            "high",
            "--summary",
            "Project map.",
        )
        result = self.run_script(
            "prompt_engine.py",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--phase",
            "implement",
            "--print",
        )

        self.assertIn("Cache-Stable Contract", result.stdout)
        self.assertIn("Context Economy Rules", result.stdout)
        self.assertIn("Context Budget", result.stdout)
        self.assertIn("Selected Context", result.stdout)
        self.assertIn(".harness/memory/memory-index.json", result.stdout)
        self.assertIn("Memory Guardrails", result.stdout)
        self.assertIn("memory_engine.py retrieve", result.stdout)
        self.assertIn("memory_engine.py reflect", result.stdout)
        self.assertIn("memory_engine.py promote", result.stdout)
        self.assertIn("memory_engine.py prune", result.stdout)

    def test_continuation_handoff_includes_context_budget(self) -> None:
        self.run_script(
            "memory_engine.py",
            "retrieve",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--source",
            ".harness/memory/memory-index.json",
            "--reason",
            "Continuation should carry compact selected context.",
            "--memory-type",
            "semantic",
        )

        result = self.run_script(
            "handoff_engine.py",
            "--target",
            str(self.target),
            "--request-id",
            self.request_id,
            "--specialist",
            "continuation",
            "--stable",
        )
        handoff_path = Path(self.json_output(result)["path"])
        handoff = handoff_path.read_text(encoding="utf-8")

        self.assertIn("Context Budget", handoff)
        self.assertIn("Selected Context", handoff)
        self.assertIn(".harness/memory/memory-index.json", handoff)

    def test_references_describe_memory_classes_and_lifecycle(self) -> None:
        state_memory = (ROOT / "references" / "state-memory.md").read_text(encoding="utf-8")
        prompting = (ROOT / "references" / "prompting.md").read_text(encoding="utf-8")

        for phrase in ["Working memory", "Episodic memory", "Semantic memory", "Procedural memory", "Memory lifecycle"]:
            self.assertIn(phrase, state_memory)
        for phrase in ["Context economy", "token estimate", "compression trigger"]:
            self.assertIn(phrase, state_memory)
        self.assertIn("stable prefix", prompting)
        self.assertIn("Context economy rules", prompting)
        self.assertIn("memory_engine.py retrieve", prompting)
        self.assertIn("memory_engine.py promote", prompting)


if __name__ == "__main__":
    unittest.main()
