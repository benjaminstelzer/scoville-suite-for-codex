import copy
import sys
import unittest
import tempfile
import subprocess
import json
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scoville-workflow-for-codex" / "scripts"))
from check_context_checkpoint import decide as decide_configured, read_thresholds
from inspect_native_context import InspectionError


def decide(sample, identity, role="coordinator"):
    return decide_configured(sample, identity, role, {"coordinator_percent": 33, "worker_percent": 66})


def events(used=33000):
    return [
        {"ordinal": 0, "type": "session_meta", "payload": {"id": "coordinator", "session_id": "parent"}},
        {"ordinal": 1, "type": "turn_context", "payload": {"turn_id": "turn"}},
        {"ordinal": 2, "type": "token_usage_record", "payload": {
            "thread_id": "coordinator", "session_id": "parent", "turn_id": "turn",
            "usage": {"input_tokens": used}}},
        {"ordinal": 3, "type": "event_msg", "payload": {"type": "token_count", "info": {
            "last_token_usage": {"input_tokens": used},
            "total_token_usage": {"input_tokens": 54000000},
            "model_context_window": 100000,
        }}},
    ]


class CoordinatorContextTests(unittest.TestCase):
    def test_cli_never_reports_rollover_for_unusable_agent_samples(self):
        from test_contract import PACKAGE
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'sessions').mkdir()
            rollout = root / 'sessions/rollout-coordinator.jsonl'
            wrong = events(80000)
            wrong[2]['payload']['thread_id'] = 'parent'
            stale = events(80000) + [
                {'ordinal': 4, 'type': 'turn_context', 'payload': {'turn_id': 'next'}}]
            env = {**os.environ, 'CODEX_HOME': folder, 'CODEX_THREAD_ID': 'coordinator'}
            command = [sys.executable, str(PACKAGE / 'scripts/check_context_checkpoint.py'),
                       '--project-root', folder, '--role', 'coordinator', '--boundary', 'W-001/step-1']
            for sample in (wrong, stale, events(80000)[:-1]):
                rollout.write_text('\n'.join(json.dumps(e) for e in sample), encoding='utf-8')
                failed_sample = subprocess.run(command, capture_output=True, text=True, env=env)
                self.assertEqual(failed_sample.returncode, 0, failed_sample.stderr)
                data = json.loads(failed_sample.stdout)
                self.assertEqual(data['telemetry'], 'unavailable')
                self.assertEqual(data['action'], 'continue')
            rollout.write_text('\n'.join(json.dumps(e) for e in events(40000)), encoding='utf-8')
            corrected = subprocess.run(command, capture_output=True, text=True, env=env)
            self.assertEqual(corrected.returncode, 0, corrected.stderr)
            data = json.loads(corrected.stdout)
            self.assertEqual(data['telemetry'], 'fresh')
            self.assertEqual(data['action'], 'rollover')

    def test_boundary_cli_diagnostic_then_corrected_unit_and_legacy_alias(self):
        from test_contract import PACKAGE
        with tempfile.TemporaryDirectory() as folder:
            command = [sys.executable, str(PACKAGE / 'scripts/check_context_checkpoint.py'),
                       '--project-root', folder, '--role', 'coordinator']
            env = {**os.environ, 'CODEX_THREAD_ID': 'missing-test-task'}
            def run(extra):
                return subprocess.run(command + extra, capture_output=True, text=True,
                                      encoding='utf-8', env=env)
            for extra in ([], ['--boundary', ' ']):
                bad = run(extra)
                self.assertEqual(bad.returncode, 2)
                self.assertIn('--boundary W-001/step-3', bad.stderr)
            for option in ('--boundary', '--accepted-unit'):
                good = run([option, 'W-001/step-3'])
                self.assertEqual(good.returncode, 0, good.stderr)
                data = json.loads(good.stdout)
                self.assertEqual(data['boundary'], 'W-001/step-3')
                self.assertEqual(data['action'], 'continue')
                self.assertEqual(data['telemetry'], 'unavailable')
            command[-1] = 'executor'
            bad = run(['--boundary', 'W-001/step-3'])
            self.assertEqual(bad.returncode, 2)
            self.assertIn('remove it', bad.stderr)
            good = run([])
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertNotIn('boundary', json.loads(good.stdout))

    def test_identity_record_is_required_and_matches_current_sample(self):
        cases = [events()]
        del cases[0][2]
        for key, value in (("thread_id", "parent"), ("thread_id", None),
                           ("turn_id", "previous"), ("turn_id", None),
                           ("usage", {"input_tokens": 1})):
            case = events()
            case[2]["payload"][key] = value
            cases.append(case)
        case = events()
        case[0]["payload"].pop("id")
        case[0]["payload"]["session_id"] = "coordinator"
        cases.append(case)
        # A pre-compaction record cannot authenticate a later token_count.
        case = events()
        case.insert(3, {"ordinal": 3, "type": "compacted", "payload": {}})
        case[-1]["ordinal"] = 4
        cases.append(case)
        for case in cases:
            with self.subTest(case=case), self.assertRaises(InspectionError):
                decide(case, "coordinator")

    def test_cli_consumes_agent_sample_and_corrected_invocation(self):
        from test_contract import PACKAGE
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sessions = root / "sessions"
            sessions.mkdir()
            rollout = sessions / "rollout-coordinator.jsonl"
            rollout.write_text("\n".join(json.dumps(e) for e in events(61000)), encoding="utf-8")
            env = {**os.environ, "CODEX_HOME": folder, "CODEX_THREAD_ID": "coordinator"}
            command = [sys.executable, str(PACKAGE / "scripts/check_context_checkpoint.py"),
                       "--project-root", folder, "--role", "executor"]
            bad = subprocess.run(command + ["--boundary", "W-003/step-1"],
                                 capture_output=True, text=True, env=env)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, "")
            self.assertIn("remove it", bad.stderr)
            good = subprocess.run(command, capture_output=True, text=True, env=env)
            self.assertEqual(good.returncode, 0, good.stderr)
            result = json.loads(good.stdout)
            self.assertEqual(result["telemetry"], "fresh")
            self.assertEqual(result["action"], "rollover_pending")
            self.assertEqual(result["thread_id"], "coordinator")
            self.assertEqual(result["input_tokens"], 61000)
            sample = events(99000)
            sample[2]["payload"]["thread_id"] = "parent"
            rollout.write_text("\n".join(json.dumps(e) for e in sample), encoding="utf-8")
            unavailable = subprocess.run(command, capture_output=True, text=True, env=env)
            self.assertEqual(unavailable.returncode, 0, unavailable.stderr)
            result = json.loads(unavailable.stdout)
            self.assertEqual(result["telemetry"], "unavailable")
            self.assertEqual(result["action"], "continue")
            self.assertNotIn("input_tokens", result)
            self.assertIn("another agent", result["diagnostic"])

    def test_imported_defaults_and_fresh_post_compaction_sample(self):
        from test_contract import PACKAGE
        thresholds = read_thresholds(PACKAGE / 'assets/workflow.toml', PACKAGE)
        self.assertEqual(thresholds, {'coordinator_percent': 40, 'worker_percent': 60})
        for role, used, expected in [('coordinator', 39000, 'continue'),
                                    ('coordinator', 40000, 'rollover'),
                                    ('executor', 60000, 'continue'),
                                    ('executor', 61000, 'rollover_pending'),
                                    ('reviewer', 61000, 'rollover_pending'),
                                    ('executor', 61000, 'rollover_pending')]:
            self.assertEqual(expected, decide_configured(events(used), 'coordinator', role, thresholds)['action'])
        sample = events(80000)
        sample.append({'ordinal': 4, 'type': 'compacted', 'payload': {}})
        sample.append(copy.deepcopy(sample[1]) | {'ordinal': 5})
        sample.append(copy.deepcopy(events(10000)[-2]) | {'ordinal': 6})
        sample.append(copy.deepcopy(events(10000)[-1]) | {'ordinal': 7})
        self.assertEqual('continue', decide_configured(sample, 'coordinator', 'executor', thresholds)['action'])

    def test_configured_thresholds_and_invalid_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "workflow.toml"
            path.write_text('schema_version = 1\n[context]\ncoordinator_percent = 40\nworker_percent = 70\n')
            config = read_thresholds(path)
            for role, used, expected in [("coordinator", 39999, "continue"), ("coordinator", 40000, "rollover"), ("executor", 70000, "continue"), ("executor", 70001, "rollover_pending")]:
                self.assertEqual(expected, decide_configured(events(used), "coordinator", role, config)["action"])
            for value in ('true', '0', '100', '33.5', '"33"'):
                path.write_text(f'schema_version = 1\n[context]\ncoordinator_percent = {value}\nworker_percent = 66\n')
                with self.assertRaises(ValueError):
                    read_thresholds(path)
            path.write_text('schema_version = 1\n')
            with self.assertRaises(ValueError):
                read_thresholds(path)

    def test_worker_threshold_is_strict_and_shared_by_roles(self):
        for role in ("executor", "reviewer"):
            for used, expected in [(33000, "continue"), (65999, "continue"), (66000, "continue"), (66001, "rollover_pending")]:
                with self.subTest(role=role, used=used):
                    self.assertEqual(expected, decide(events(used), "coordinator", role)["action"])

    def test_accelerated_cli_schedules_children_and_rolls_manager_at_completed_unit(self):
        from test_contract import PACKAGE
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'sessions').mkdir()
            (root / '.scoville').mkdir()
            (root / '.scoville/config.json').write_text(json.dumps({
                'workflow': {'context': {'coordinator_percent': 15, 'worker_percent': 15}}
            }), encoding='utf-8')
            rollout = root / 'sessions/rollout-coordinator.jsonl'
            env = {**os.environ, 'CODEX_HOME': folder, 'CODEX_THREAD_ID': 'coordinator'}
            for role, used, expected in (
                ('executor', 15000, 'continue'),
                ('executor', 15001, 'rollover_pending'),
                ('reviewer', 15001, 'rollover_pending'),
                ('coordinator', 14999, 'continue'),
                ('coordinator', 15000, 'rollover'),
            ):
                with self.subTest(role=role, used=used):
                    rollout.write_text('\n'.join(json.dumps(e) for e in events(used)), encoding='utf-8')
                    command = [sys.executable, str(PACKAGE / 'scripts/check_context_checkpoint.py'),
                               '--project-root', folder, '--role', role]
                    if role == 'coordinator':
                        command += ['--boundary', 'W-001/steps-1-2']
                    result = subprocess.run(command, capture_output=True, text=True, env=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    data = json.loads(result.stdout)
                    self.assertEqual(data['action'], expected)
                    self.assertEqual(data['telemetry'], 'fresh')
                    self.assertEqual(data['threshold_percent'], 15)
                    self.assertEqual(data['input_tokens'], used)
                    self.assertEqual('boundary' in data, role == 'coordinator')

    def test_threshold_and_cumulative_usage(self):
        for used, expected in [(32999, "continue"), (33000, "rollover"), (40300, "rollover")]:
            with self.subTest(used=used):
                self.assertEqual(expected, decide(events(used), "coordinator")["action"])

    def test_divi_boundary(self):
        sample = events(104121)
        sample[-1]["payload"]["info"]["model_context_window"] = 258400
        self.assertEqual("rollover", decide(sample, "coordinator")["action"])

    def test_missing_wrong_identity_stale_and_invalid(self):
        cases = [events()[:-1], events()]
        cases[1][0]["payload"]["id"] = "worker"
        for kind in ("compacted", "turn_context"):
            case = events()
            case.append({"ordinal": 4, "type": kind, "payload": {"turn_id": "turn"}})
            cases.append(case)
        for value in (None, True, -1, 0, 100001):
            cases.append(events(value))
        terminal = events()
        terminal.append({"ordinal": 4, "type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn"}})
        cases.append(terminal)
        for case in cases:
            with self.subTest(case=case), self.assertRaises(InspectionError):
                decide(copy.deepcopy(case), "coordinator")


if __name__ == "__main__":
    unittest.main()
