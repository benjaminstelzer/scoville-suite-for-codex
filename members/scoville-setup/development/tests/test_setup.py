"""Exercise the shipped Setup helper and the actual configuration consumers."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("setup_builder", ROOT / "development/build_suite.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class SetupTests(unittest.TestCase):
    def test_invalid_stdin_patch_preserves_config_then_actual_consumer(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config = builder.load(ROOT, 'codex', 'suite')
            for name in ('scoville-setup', 'scoville-workflow-for-codex'):
                member = next(m for m in config['members'] if m['name'] == name)
                for relative, data in builder.payload(ROOT, member, config).items():
                    target = base / name / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            project = base / 'project Ä 中文'
            (project / '.scoville').mkdir(parents=True)
            path = project / '.scoville/config.json'
            before = b'{"workflow":{"context":{"coordinator_percent":40}},"unrelated":{"keep":true}}\n'
            path.write_bytes(before)
            script = base / 'scoville-setup/scoville-setup/scripts/setup.py'
            command = [sys.executable, '-B', str(script), 'set', '--project-root', str(project)]
            for invalid in (b'', b'{\n"workflow":', b'\xff'):
                failed = subprocess.run(command, input=invalid, capture_output=True)
                self.assertNotEqual(failed.returncode, 0)
                payload = json.loads(failed.stdout.decode('utf-8'))
                self.assertFalse(payload['ok'])
                self.assertNotIn('effective', payload)
                self.assertIn('stdin', payload['diagnostic'])
                self.assertIn('UTF-8', payload['diagnostic'])
                self.assertEqual(path.read_bytes(), before)
            patch = {'workflow': {'context': {'coordinator_percent': 35}}}
            corrected = subprocess.run(command, input=json.dumps(patch).encode('utf-8'), capture_output=True)
            self.assertEqual(corrected.returncode, 0, corrected.stdout.decode('utf-8'))
            self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['unrelated'], {'keep': True})
            consumer = base / 'scoville-workflow-for-codex/scoville-workflow-for-codex/scripts/check_context_checkpoint.py'
            result = subprocess.run([sys.executable, '-B', str(consumer), '--role', 'coordinator',
                                     '--boundary', 'W-001/step-1',
                                     '--project-root', str(project)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['threshold_percent'], 35)

    def test_saved_manager_pair_reaches_start_and_survives_successor(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config = builder.load(ROOT, 'codex', 'suite')
            for name in ('scoville-setup', 'scoville-workflow-for-codex', 'scoville-plan'):
                member = next(m for m in config['members'] if m['name'] == name)
                for relative, data in builder.payload(ROOT, member, config).items():
                    target = base / name / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            project = base / 'Projekt ä 中文'
            project.mkdir()
            setup = base / 'scoville-setup/scoville-setup/scripts/setup.py'
            scripts = base / 'scoville-workflow-for-codex/scoville-workflow-for-codex/scripts'

            def run(script, *args, patch=None):
                result = subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                    input=json.dumps(patch, ensure_ascii=False), capture_output=True, text=True, encoding='utf-8')
                return result, json.loads(result.stdout) if result.stdout else None

            result, report = run(scripts / 'run_feedback.py', 'create', '--project-root', project)
            self.assertEqual(result.returncode, 0, result.stderr)
            request = project / 'request.txt'
            request.write_text('Start Workflow; internal coordination authorized.', encoding='utf-8')
            common = ['--runner-id', '/root/runner', '--project-name', project.name,
                      '--manager-number', '1', '--report-file', report['report_file']]
            assignments = []

            def start(*overrides):
                assignment = project / f'manager-{len(assignments)}.txt'
                assignments.append(assignment)
                return run(scripts / 'build_manager_handoff.py', *common, '--mode', 'start',
                           '--project-root', project,
                           '--request-file', request, '--assignment-file', assignment, *overrides)

            result, initial = start()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((initial['model'], initial['reasoning_effort']), ('gpt-6.1-sol', 'high'))
            result, saved = run(setup, 'set', '--project-root', project,
                                patch={'workflow': {'manager': {'model': 'gpt-6-luna'}}})
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(saved['effective']['workflow']['manager'], {'model': 'gpt-6-luna', 'reasoning': 'high'})
            result, saved = run(setup, 'set', '--project-root', project,
                                patch={'workflow': {'manager': {'reasoning': 'high'}}})
            self.assertEqual(result.returncode, 0, result.stdout)
            result, launched = start()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((launched['model'], launched['reasoning_effort']), ('gpt-6-luna', 'high'))
            result, explicit = start('--model', 'gpt-6.1-sol', '--thinking', 'medium')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((explicit['model'], explicit['reasoning_effort']), ('gpt-6.1-sol', 'medium'))
            path = project / '.scoville/config.json'
            before = path.read_bytes()
            for pair in ({'model': False}, {'model': '  '}, {'reasoning': 'bad'},
                         {'reasoning': 'ultra'}, {'secret': 'DO_NOT_ECHO'}):
                result, failed = run(setup, 'set', '--project-root', project,
                                     patch={'workflow': {'manager': pair}})
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(failed['ok'])
                self.assertIn('manager', failed['diagnostic'])
                self.assertNotIn('DO_NOT_ECHO', failed['diagnostic'])
                self.assertEqual(path.read_bytes(), before)
            result, saved = run(setup, 'set', '--project-root', project,
                                patch={'workflow': {'manager': {'model': 'gpt-6-astra', 'reasoning': 'medium'}}})
            self.assertEqual(result.returncode, 0, result.stdout)
            successor_assignment = project / 'manager-successor.txt'
            assignments.append(successor_assignment)
            result, successor = run(scripts / 'build_manager_handoff.py', *common, '--mode', 'successor',
                '--predecessor-id', '/root/manager', '--model', launched['model'],
                '--thinking', launched['reasoning_effort'], '--assignment-file', successor_assignment)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((successor['model'], successor['reasoning_effort']), ('gpt-6-luna', 'high'))
            # Same consumer signature as native spawn_agent; no live agent is started.
            def consume(*, task_name, message, fork_turns, model, reasoning_effort):
                self.assertEqual(fork_turns, 'none')
                self.assertTrue(task_name)
                matching = [p for p in assignments if str(p) in message]
                self.assertEqual(len(matching), 1)
                self.assertIn(f'model={model}, reasoning={reasoning_effort}', matching[0].read_text(encoding='utf-8'))
            for arguments in (initial, launched, explicit, successor):
                consume(**arguments)
            path.write_text(json.dumps({'workflow': {'manager': {'model': False}}}), encoding='utf-8')
            result, failed = start()
            self.assertNotEqual(result.returncode, 0)
            self.assertIsNone(failed)
            self.assertIn('workflow.manager', result.stderr)
            path.write_text('{}', encoding='utf-8')
            result, corrected = start()
            self.assertEqual(result.returncode, 0, result.stderr)
            consume(**corrected)

    def test_built_setup_saves_only_valid_explicit_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config = builder.load(ROOT, "codex", "suite")
            for name in ("scoville-setup", "scoville-ask-for-codex", "scoville-workflow-for-codex"):
                member = next(m for m in config["members"] if m["name"] == name)
                for relative, data in builder.payload(ROOT, member, config).items():
                    target = base / name / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            project = base / "Projekt ä 中文"
            project.mkdir()
            helper = base / "scoville-setup/scoville-setup/scripts/setup.py"

            def run(operation, patch=None):
                result = subprocess.run([sys.executable, "-B", str(helper), operation,
                                         "--project-root", str(project)],
                                        input=json.dumps(patch), capture_output=True,
                                        text=True, encoding="utf-8")
                return result, json.loads(result.stdout)

            result, shown = run("show")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(shown["effective"]["ask"]["claude"]["timeout_seconds"], 3600)
            self.assertEqual(shown["effective"]["workflow"]["context"],
                             {"coordinator_percent": 40, "worker_percent": 60})
            self.assertFalse((project / ".scoville").exists())
            self.assertNotIn('pin_threads', shown['effective']['ask'])
            self.assertTrue(shown['effective']['workflow']['pin_threads'])
            result, rejected = run('set', {'ask': {'pin_threads': True}})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('patch.ask.pin_threads is obsolete', rejected['diagnostic'])
            self.assertIn('omit this field', rejected['diagnostic'])
            self.assertFalse((project / '.scoville').exists())
            result, rejected = run('set', {'workflow': {'pin_threads': False}})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('patch.workflow.pin_threads is obsolete', rejected['diagnostic'])
            self.assertIn('omit this field', rejected['diagnostic'])
            self.assertFalse((project / '.scoville').exists())
            result, saved = run('set', {'workflow': {'context': {'worker_percent': 82}}})
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertNotIn('pin_threads', saved['effective']['ask'])
            result, saved = run("set", {"ask": {"claude": {"timeout_seconds": 2400}},
                                        "workflow": {"context": {"worker_percent": 82}}})
            self.assertEqual(result.returncode, 0, result.stderr)
            path = project / ".scoville/config.json"
            values = json.loads(path.read_text(encoding="utf-8"))
            values["other_tool"] = {"keep": [1, 2]}
            # Existing projects remain readable and unrelated saves preserve the old key.
            values["ask"]["pin_threads"] = True
            values["workflow"]["pin_threads"] = False
            path.write_text(json.dumps(values), encoding="utf-8")
            result, saved = run("set", {"ask": {"presets": {"sol": {"effort": "medium"}}}})
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(path.read_text())["other_tool"], {"keep": [1, 2]})
            self.assertEqual(saved["effective"]["ask"]["claude"]["timeout_seconds"], 2400)
            self.assertTrue(json.loads(path.read_text())["ask"]["pin_threads"])
            self.assertFalse(json.loads(path.read_text())["workflow"]["pin_threads"])
            for level in ("none", "minimal", "max", "ultra"):
                result, failed = run("set", {"workflow": {"execute": {"low": {"reasoning": level}}}})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("manually", failed["diagnostic"])
                result, failed = run("set", {"ask": {"presets": {"astra": {"effort": level}}}})
                self.assertNotEqual(result.returncode, 0)
            for level in ("low", "medium", "high", "xhigh"):
                result, saved = run("set", {"workflow": {"execute": {"low": {"reasoning": level}}}})
                self.assertEqual(result.returncode, 0, result.stdout)
            manual = json.loads(path.read_text(encoding="utf-8"))
            manual["workflow"]["execute"]["low"]["reasoning"] = "ultra"
            manual["ask"]["presets"]["astra"] = {"effort": "ultra"}
            path.write_text(json.dumps(manual), encoding="utf-8")
            result, saved = run("set", {"workflow": {"context": {"worker_percent": 82}}})
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(saved["effective"]["workflow"]["execute"]["low"]["reasoning"], "ultra")
            self.assertEqual(saved["effective"]["ask"]["presets"]["astra"]["effort"], "ultra")
            before = path.read_bytes()
            for patch in ({"ask": {"claude": {"timeout_seconds": 0}}},
                          {'ask': {'pin_threads': 'false'}},
                          {'workflow': {'pin_threads': 0}},
                          {"ask": {"presets": {"sol": {"model": False}}}},
                          {"workflow": {"context": {"worker_percent": True}}},
                          {"workflow": {"execute": {"low": {"reasoning": "bad"}}}},
                          {"workflow": {"coordinator": {"title": "unwanted"}}}):
                result, failed = run("set", patch)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(failed["ok"])
                self.assertEqual(path.read_bytes(), before)
            result, failed = run("set", {"ask": {"presets": {"astra": {"effort": "ultra"}}}})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("patch.ask.presets.astra.effort", failed["diagnostic"])
            self.assertIn("choose low, medium, high or xhigh", failed["diagnostic"])
            self.assertEqual(path.read_bytes(), before)
            result, corrected = run("set", {"ask": {"presets": {"astra": {"effort": "high"}}}})
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(corrected["effective"]["ask"]["presets"]["astra"]["effort"], "high")
            ask = base / "scoville-ask-for-codex/scoville-ask-for-codex/scripts/ask.py"
            request = {"operation": "resolve", "project_root": str(project),
                       "overrides": {"advisers": ["fable"]}}
            result = subprocess.run([sys.executable, "-B", str(ask)], input=json.dumps(request),
                                    text=True, encoding="utf-8", capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["config"]["claude"]["timeout_seconds"], 2400)
            self.assertTrue(json.loads(result.stdout)['config']['pin_threads'])
            resolver = base / 'scoville-workflow-for-codex/scoville-workflow-for-codex/scripts/resolve_model_pair.py'
            result = subprocess.run([sys.executable, str(resolver), '--show-config', '--project-root', str(project)],
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(json.loads(result.stdout)['config']['pin_threads'])
            checkpoint = base / "scoville-workflow-for-codex/scoville-workflow-for-codex/scripts/check_context_checkpoint.py"
            result = subprocess.run([sys.executable, "-B", str(checkpoint), "--role", "executor",
                                     "--project-root", str(project)], capture_output=True,
                                    text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["threshold_percent"], 82)

    def test_setup_is_codex_suite_only(self):
        for profile, layout, expected in [("codex", "suite", True), ("codex", "standalone", False),
                                          ("general", "suite", False)]:
            config = builder.load(ROOT, profile, layout)
            self.assertEqual(any(m["name"] == "scoville-setup" for m in config["members"]), expected)


if __name__ == "__main__":
    unittest.main()
