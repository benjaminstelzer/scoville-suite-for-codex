"""Functional Ask contract checks with simulated host and CLI boundaries."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SUITE = Path(__file__).resolve().parents[4]
_build_spec = importlib.util.spec_from_file_location('ask_behavior_build', SUITE / 'development/build_suite.py')
_builder = importlib.util.module_from_spec(_build_spec)
_build_spec.loader.exec_module(_builder)
_package_temp = tempfile.TemporaryDirectory(prefix='ask-behavior-', ignore_cleanup_errors=True)
_config = _builder.load(SUITE, 'codex')
_member = next(m for m in _config['members'] if m['name'] == 'scoville-ask-for-codex')
for _name, _data in _builder.payload(SUITE, _member, _config).items():
    _target = Path(_package_temp.name) / _name
    _target.parent.mkdir(parents=True, exist_ok=True)
    _target.write_bytes(_data)
PACKAGE = Path(_package_temp.name) / 'scoville-ask-for-codex'
SCRIPTS = PACKAGE / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("ask_under_test", SCRIPTS / "ask.py")
assert SPEC and SPEC.loader
ask = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ask)

CATALOG = {"source": "model/list", "models": [
    {"model": "gpt-5.6-sol", "efforts": ["low", "medium", "high", "xhigh"]},
    {"model": "gpt-6-astra", "efforts": ["medium", "high"]},
    {"model": "gpt-6-sol", "efforts": ["low", "medium", "high"]},
]}
ADVISERS = [
    {"id": "astra", "route": "native", "model": "gpt-6-astra", "effort": "high"},
    {"id": "claude", "name": "Second reader", "route": "claude-cli", "model": "claude-fable-5-1", "effort": "high"},
    {"id": "sol", "route": "native", "model": "gpt-6-sol", "effort": "medium"},
]


def prepare_request(advisers=ADVISERS, **extra):
    return {"mode": "review", "question": "Could this patch lose data?", "scope": "patch A",
            "reference": "round-1", "caller_id": "caller-17", "caller_title": "Review patch",
            "projectId": "project-1",
            "prior_state": "not_started", "prior_task_ids": ["older-task"],
            "cwd": str(PACKAGE), "catalog": CATALOG,
            "overrides": {"advisers": advisers}, **extra}


class AskBehaviorTests(unittest.TestCase):
    def test_shared_writing_contract_preserves_question_in_claude_consumer(self):
        question = 'Exact question: A/B; "quoted"\nKeep this unchanged.\n'
        request = ask.prepare(prepare_request([ADVISERS[1]], question=question))['entries'][0]['request']
        writing = (PACKAGE / 'references/writing.md').read_text(encoding='utf-8')
        self.assertEqual(1, request['prompt'].count(writing))
        self.assertTrue(request['prompt'].endswith(question))
        completed = subprocess.CompletedProcess([], 0, json.dumps({'result':'review complete','session_id':'fixture'}), '')
        with mock.patch.object(ask.ask_claude, 'resolve_claude_command', return_value=['claude']), \
             mock.patch.object(ask.ask_claude, 'run_command', return_value=completed) as consumer:
            answer = ask.claude(request)
        self.assertEqual('review complete', answer['answer'])
        self.assertEqual(request['prompt'], consumer.call_args.args[2])

    def test_missing_writing_contract_is_named_and_corrected_prepare_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'references').mkdir()
            for name in ('config.default.json', 'references/adviser.md'):
                (root / name).write_bytes((PACKAGE / name).read_bytes())
            with mock.patch.object(ask, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'packaged writing rules.*writing.md.*readable UTF-8'):
                    ask.prepare(prepare_request([ADVISERS[1]]))
                (root / 'references/writing.md').write_bytes((PACKAGE / 'references/writing.md').read_bytes())
                self.assertEqual('claude', ask.prepare(prepare_request([ADVISERS[1]]))['entries'][0]['request']['operation'])

    def test_invalid_nested_timeout_does_not_echo_private_value(self):
        marker = 'TEST_PRIVATE_VALUE_NOT_FOR_DIAGNOSTICS'
        request = {'operation': 'resolve', 'overrides': {'claude': {'timeout_seconds': {'api_key': marker}}}}
        result = subprocess.run([sys.executable, str(SCRIPTS / 'ask.py')], input=json.dumps(request),
                                text=True, encoding='utf-8', capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(marker, result.stdout + result.stderr)
        self.assertIn('timeout_seconds', result.stdout)
        request['overrides']['claude']['timeout_seconds'] = 30
        result = subprocess.run([sys.executable, str(SCRIPTS / 'ask.py')], input=json.dumps(request),
                                text=True, encoding='utf-8', capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_adviser_fields_name_the_path_and_corrected_resolve_works(self):
        with self.assertRaisesRegex(ValueError, r"request\.overrides\.advisers\[0\]\.route \(adviser sol\)='cloud' .*'native' or 'claude-cli'"):
            ask.resolve({"overrides": {"advisers": [{
                "id": "sol", "route": "cloud", "model": "gpt-6-sol", "effort": "medium"
            }]}})
        result = ask.resolve({"overrides": {"advisers": [{
            "id": "sol", "route": "native", "model": "gpt-6-sol", "effort": "medium"
        }]}})
        self.assertEqual(result["config"]["advisers"][0]["route"], "native")

    def test_bad_claude_timeout_names_field_and_corrected_resolve_works(self):
        with self.assertRaisesRegex(ValueError, r"request\.overrides\.claude\.timeout_seconds=0 .*positive finite number"):
            ask.resolve({"overrides": {"claude": {"timeout_seconds": 0}}})
        result = ask.resolve({"overrides": {"claude": {"timeout_seconds": 2400}}})
        self.assertEqual(result["config"]["claude"]["timeout_seconds"], 2400)

    def test_prepare_mode_diagnostic_and_corrected_claude_request(self):
        request = prepare_request([ADVISERS[1]])
        with self.assertRaisesRegex(ValueError, r"request\.mode=None .*'review' or 'consultation'"):
            ask.prepare({**request, "mode": None})
        prepared = ask.prepare({**request, "mode": "consultation"})
        self.assertEqual(prepared["entries"][0]["request"]["operation"], "claude")

    def test_configuration_reference_has_no_legacy_migration_instructions(self):
        text = (PACKAGE / "references/configuration.md").read_text(encoding="utf-8")
        self.assertNotIn("Migrate existing settings", text)
        self.assertNotIn("Keep original personal configuration files", text)
        self.assertNotIn("Map each old `astra` or `sol` object", text)

    def test_file_defaults_and_request_precedence_without_personal_layer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config.default.json").write_bytes((PACKAGE / "config.default.json").read_bytes())
            legacy = root / "config.json"
            legacy.write_text('{"advisers":["sol"]}', encoding="utf-8")
            request = {"catalog": CATALOG, "project_root": str(root)}
            with mock.patch.object(ask, "ROOT", root):
                self.assertEqual(ask.resolve(request)["config"]["advisers"][0]["id"], "astra")
                self.assertFalse((root / ".scoville").exists())
                (root / ".scoville").mkdir()
                config = root / ".scoville/config.json"
                saved = {"ask": {"advisers": [{"id": "sol", "effort": "medium"}]}}
                config.write_text(json.dumps(saved), encoding="utf-8")
                self.assertEqual(ask.resolve(request)["config"]["advisers"][0]["effort"], "medium")
                result = ask.resolve({**request, "overrides": {"presets": {"sol": {"effort": "high"}}}})
                self.assertEqual(result["config"]["advisers"][0]["effort"], "high")
                self.assertEqual(json.loads(config.read_text()), saved)
                saved["ask"]["presets"] = {"sol": {"effort": "high"}}
                config.write_text(json.dumps(saved), encoding="utf-8")
                self.assertEqual(ask.resolve(request)["config"]["advisers"][0]["effort"], "medium")
                self.assertTrue(legacy.exists())
                for bad in ['[]', '{', '{"ask":null}', '{"ask":{"claude":{"timeout_seconds":false}}}']:
                    config.write_text(bad, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        ask.resolve(request)

    def test_native_resolution_preserves_settings_without_catalog_or_dispatch(self):
        for level in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'):
            with mock.patch('subprocess.Popen', side_effect=AssertionError('resolution must stay local')):
                result = ask.resolve({'overrides': {'advisers': [{
                    'id': 'sol', 'model': 'gpt-6-sol', 'effort': level}]}})
            self.assertEqual(result['config']['advisers'][0]['model'], 'gpt-6-sol')
            self.assertEqual(result['config']['advisers'][0]['effort'], level)

    def test_claude_defaults_and_explicit_adviser_override_are_distinct(self):
        selected = ask.resolve({"catalog": CATALOG,
            "overrides": {"advisers": ["sol", "claude", "fable"]}})["config"]["advisers"]
        self.assertEqual([(a["id"], a["model"], a["effort"]) for a in selected], [
            ("sol", "gpt-5.6-sol", "high"),
            ("claude", "claude-opus-5-5", "high"),
            ("fable", "claude-fable-5-1", "medium"),
        ])
        explicit = ask.resolve({"overrides": {"advisers": [
            {"id": "fable", "effort": "high"}]}})["config"]["advisers"]
        self.assertEqual([(a["id"], a["model"], a["effort"]) for a in explicit],
                         [("fable", "claude-fable-5-1", "high")])



    def test_json_cli_uses_utf8_for_unicode_question_without_environment_override(self):
        request = prepare_request([ADVISERS[1]], question="Prüfe Änderung äöü 😀")
        request["operation"] = "prepare"
        completed = subprocess.run([sys.executable, str(SCRIPTS / "ask.py")],
            input=json.dumps(request), text=True, encoding="utf-8",
            capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertTrue(output["ok"])
        self.assertIn("Prüfe Änderung äöü 😀", output["entries"][0]["request"]["prompt"])

    def test_resolution_selects_one_two_and_three_without_extra_dispatch(self):
        for count in (1, 2, 3):
            with self.subTest(count=count):
                selected = ADVISERS[:count]
                result = ask.resolve({"catalog": CATALOG, "overrides": {"advisers": selected}})
                self.assertEqual(result["config"]["advisers"], selected)

    def test_native_prepare_is_removed_without_fallback(self):
        for adviser in (ADVISERS[0], ADVISERS[2]):
            with self.assertRaisesRegex(ValueError, r'build_adviser_prompt.py and collaboration.spawn_agent'):
                ask.prepare(prepare_request([adviser]))
        self.assertNotIn('followup', ask.OPERATIONS)

    def test_claude_prepare_keeps_question_without_separate_authority_fields(self):
        request = prepare_request([ADVISERS[1]])
        result = ask.prepare(request)['entries'][0]
        self.assertEqual(result['request']['operation'], 'claude')
        self.assertIn(request['question'], result['request']['prompt'])
        self.assertNotIn('authorized', result['request'])
        self.assertNotIn('creation_authorized', result['request'])
        with self.assertRaisesRegex(ValueError, 'clarify ambiguous intent'):
            ask.prepare({**request, 'mode': None})

    def test_resolve_cli_flags_return_direct_technical_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            completed = subprocess.run([sys.executable, str(SCRIPTS / 'ask.py'),
                '--project-root', temporary, '--adviser', 'sol'],
                text=True, encoding='utf-8', capture_output=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(len(payload['config']['advisers']), 1)
            self.assertEqual(payload['config']['advisers'][0]['id'], 'sol')
            self.assertFalse((Path(temporary) / '.scoville').exists())

    def test_input_file_json_diagnostic_then_corrected_actual_cli_call(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "request.json"
            path.write_text("{", encoding="utf-8")
            command = [sys.executable, str(SCRIPTS / "ask.py"), "--input-file", str(path)]
            failed = subprocess.run(command, text=True, encoding="utf-8", capture_output=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn(str(path), json.loads(failed.stdout)["error"])
            self.assertIn("line 1, column", json.loads(failed.stdout)["error"])
            path.write_text(json.dumps({"operation": "resolve"}), encoding="utf-8")
            corrected = subprocess.run(command, text=True, encoding="utf-8", capture_output=True)
            self.assertEqual(corrected.returncode, 0, corrected.stdout)
            self.assertTrue(json.loads(corrected.stdout)["ok"])

    def test_sidebar_operation_is_unavailable(self):
        self.assertNotIn('sidebar', ask.OPERATIONS)

    def test_claude_executes_only_adapter_command_and_preserves_session(self):
        cli_request = ask.prepare(prepare_request([ADVISERS[1]]))["entries"][0]["request"]
        completed = subprocess.CompletedProcess(["claude"], 0,
            json.dumps({"result": "  Independent answer\n", "session_id": "sid-1",
                        "model": "claude-fable-5-1", "permission_denials": ["Read secret"]}), "")
        with mock.patch.object(ask.ask_claude, "resolve_claude_command", return_value=["claude"]), \
             mock.patch.object(ask.ask_claude, "run_command", return_value=completed) as run:
            result = ask.claude(cli_request)
        command = run.call_args.args[0]
        self.assertIn('-p', command)
        self.assertNotIn('--bg', command)
        self.assertEqual(command[command.index("--tools") + 1],
                         "Read,Grep,Glob")
        self.assertIn("--safe-mode", command)
        self.assertNotIn("--resume", command)
        self.assertEqual(result["answer"], "  Independent answer\n")
        self.assertEqual(result["session_id"], "sid-1")
        self.assertTrue(result["continuation_available"])
        self.assertEqual(result["permission_denials"], ["Read secret"])
        with mock.patch.object(ask.ask_claude, "resolve_claude_command", return_value=["claude"]), \
             mock.patch.object(ask.ask_claude, "run_command", return_value=completed) as resumed:
            next_result = ask.claude({**cli_request, "session_id": "sid-1"})
        self.assertEqual(resumed.call_args.args[0][resumed.call_args.args[0].index("--resume") + 1], "sid-1")
        self.assertEqual(next_result["context_mode"], "continued")

    def test_nonpersistent_claude_result_does_not_offer_session_continuation(self):
        request = prepare_request([ADVISERS[1]])
        request['overrides']['claude'] = {'session_persistence': False}
        prepared = ask.prepare(request)['entries'][0]['request']
        completed = subprocess.CompletedProcess(['claude'], 0,
            json.dumps({'result': 'Review complete', 'session_id': 'ephemeral-id'}), '')
        with mock.patch.object(ask.ask_claude, 'resolve_claude_command', return_value=['claude']), \
             mock.patch.object(ask.ask_claude, 'run_command', return_value=completed) as run:
            result = ask.claude(prepared)
        self.assertIn('-p', run.call_args.args[0])
        self.assertIn('--no-session-persistence', run.call_args.args[0])
        self.assertFalse(result['continuation_available'])

    def test_web_tools_require_boolean_opt_in_and_reach_both_cli_flags(self):
        for enabled in (False, True):
            request = prepare_request([ADVISERS[1]])
            request["overrides"]["claude"] = {"web_tools": enabled}
            cli_request = ask.prepare(request)["entries"][0]["request"]
            completed = subprocess.CompletedProcess(["claude"], 0,
                json.dumps({"result": "Answer", "session_id": "sid-web"}), "")
            with mock.patch.object(ask.ask_claude, "resolve_claude_command", return_value=["claude"]), \
                 mock.patch.object(ask.ask_claude, "run_command", return_value=completed) as run:
                ask.claude(cli_request)
            command = run.call_args.args[0]
            expected = "Read,Grep,Glob" + (",WebSearch,WebFetch" if enabled else "")
            for flag in ("--tools", "--allowed-tools"):
                self.assertEqual(expected, command[command.index(flag) + 1])
            self.assertNotIn("Bash", expected)
        for invalid in ("true", 1, None, []):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "boolean"):
                ask.resolve({"catalog": CATALOG, "overrides": {"claude": {"web_tools": invalid}}})
        config = ask.resolve({"catalog": CATALOG,
                              "overrides": {"claude": {"web_tools": False}}})["config"]
        self.assertFalse(config["claude"]["web_tools"])

    def test_claude_failures_never_return_answer(self):
        request = ask.prepare(prepare_request([ADVISERS[1]]))["entries"][0]["request"]
        for completed, error in [
            (subprocess.CompletedProcess(["claude"], 1, "", "authentication failed"), "authentication failed"),
            (subprocess.CompletedProcess(["claude"], 0, "not-json", ""), "invalid JSON"),
            (subprocess.CompletedProcess(["claude"], 0, json.dumps({"result": " "}), ""), "Claude answer"),
            (subprocess.CompletedProcess(["claude"], 0, json.dumps({"is_error": True,
                "errors": ["budget exhausted"]}), ""), "budget exhausted"),
        ]:
            with self.subTest(error=error), \
                 mock.patch.object(ask.ask_claude, "resolve_claude_command", return_value=["claude"]), \
                 mock.patch.object(ask.ask_claude, "run_command", return_value=completed), \
                 self.assertRaisesRegex(ValueError, error):
                ask.claude(request)

    def test_claude_exit_error_uses_oauth_detail_from_stdout_json(self):
        request = ask.prepare(prepare_request([ADVISERS[1]]))["entries"][0]["request"]
        oauth_error = "Failed to authenticate: OAuth session expired and could not be refreshed"
        completed = subprocess.CompletedProcess(["claude"], 1,
            json.dumps({"is_error": True, "errors": [oauth_error]}), "")
        with mock.patch.object(ask.ask_claude, "resolve_claude_command", return_value=["claude"]), \
             mock.patch.object(ask.ask_claude, "run_command", return_value=completed) as launch, \
             self.assertRaisesRegex(ValueError, oauth_error):
            ask.claude(request)
        launch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
