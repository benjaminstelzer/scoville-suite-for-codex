"""Actual packaged selector output is usable by every relevant dispatch mode."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_contract import PACKAGE, SUITE_ROOT


class StepProgressDispatchTests(unittest.TestCase):
    def test_normal_review_correction_and_continuation_preserve_terminal_scope(self):
        fixture = SUITE_ROOT / "members/scoville-plan/development/tests/fixtures/valid-profile"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            shutil.copytree(fixture, root)
            plan = root / "docs/plans/0001-validate-profile.md"
            plan.write_text(plan.read_text(encoding="utf-8").replace(
                "1. Read the canonical files.\n2. Check the local record shapes.",
                "1. [status: done] Write the approved text.\n2. [status: in_progress] Check the saved document.\n3. Keep older work unknown.").replace("Steps:\n", "Instructions: First write the approved text, then transfer its document check. Preserve the user's original approved wording.\nSteps:\n", 1).replace("Next action: Run the structural validator.\n", ""), encoding="utf-8")
            worker = Path(directory) / "worker.txt"
            worker.write_text("completed: saved the text; document check remains for the manager.", encoding="utf-8")
            finding = Path(directory) / "finding.txt"
            finding.write_text("changes_requested: correct the title in the approved text; preserve the rest.", encoding="utf-8")
            handoff = Path(directory) / "handoff.txt"
            handoff.write_text("Step 1 text is saved and checked. Continue only Step 2 document check; preserve Step 1 effects.", encoding="utf-8")
            facts = Path(directory) / "facts.txt"
            facts.write_text("Preserve the user's original approved wording. Acceptance: saved document must preserve its title.", encoding="utf-8")
            modes = [
                ("executor", "W-001", []),
                ("reviewer", "W-001/step-1", ["--executor-result", str(worker), "--supplemental-context", str(facts)]),
                ("executor", "W-001/step-1", ["--reviewer-result", str(finding)]),
                ("executor", "W-001/steps-1-2", ["--context-handoff", str(handoff), "--supplemental-context", str(facts), "--predecessor-agent-id", "previous-worker"]),
            ]
            for role, unit, extra in modes:
                with self.subTest(role=role, unit=unit, extra=extra):
                    run = subprocess.run([sys.executable, str(PACKAGE / "scripts/build_dispatch_prompt.py"),
                        "--project-root", str(root), "--manager-agent-id", "actual-manager",
                        "--role", role, "--unit", unit, *extra], text=True, encoding="utf-8", capture_output=True)
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                    self.assertIn(unit, run.stdout)
                    self.assertIn("Step 1: done", run.stdout)
                    self.assertIn("explicitly assigned review or correction", run.stdout)
                    self.assertIn("Preserve the user's original approved wording.", run.stdout)
                    if not extra:
                        self.assertIn("Step 3: unknown (unmarked)", run.stdout)
                    if "--context-handoff" not in extra:
                        self.assertIn("1. [status: done] Write the approved text.", run.stdout)
                        self.assertIn("First write the approved text, then transfer its document check.", run.stdout)
                    else:
                        self.assertIn(handoff.read_text(encoding="utf-8"), run.stdout)
                        self.assertIn(facts.read_text(encoding="utf-8"), run.stdout)
                        self.assertNotIn("First write the approved text, then transfer its document check.", run.stdout)
            # Position lookup uses the same installed selector used by dispatch.
            run = subprocess.run([sys.executable, str(PACKAGE / "scripts/select_context.py"),
                "--root", str(root), "--plan", "PLAN-0001", "--position"], text=True, encoding="utf-8", capture_output=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(json.loads(run.stdout)["current_units"], ["W-001/step-2"])
