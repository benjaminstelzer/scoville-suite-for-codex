"""Run Claude preparation commands and the adapter against a local CLI double."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_ask_behavior import PACKAGE, SCRIPTS, ask, prepare_request, ADVISERS


class ClaudeRecipeTests(unittest.TestCase):
    def cli(self, *arguments, request=None):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / 'ask.py'), *arguments],
            input=json.dumps(request) if request is not None else None,
            text=True, encoding='utf-8', capture_output=True,
        )

    def test_cli_diagnostics_and_corrected_selections(self):
        with tempfile.TemporaryDirectory() as temporary:
            for flags, expected, corrected in [
                (['--adviser', 'claude', '--effort', 'ultra'],
                 ["request.overrides.advisers[0].effort", "adviser claude", "'ultra'", 'low, medium, high, xhigh, max'],
                 ['--adviser', 'claude', '--effort', 'high']),
                (['--adviser', 'opus'],
                 ["request.overrides.advisers[0]", "'opus'", 'astra, sol, claude, fable'],
                 ['--adviser', 'claude']),
            ]:
                with self.subTest(flags=flags):
                    bad = self.cli('--project-root', temporary, *flags)
                    self.assertEqual(bad.returncode, 1)
                    for fragment in expected:
                        self.assertIn(fragment, bad.stdout)
                    good = self.cli('--project-root', temporary, *corrected)
                    self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
                    adviser = json.loads(good.stdout)['config']['advisers'][0]
                    prepared = ask.prepare(prepare_request([adviser]))
                    self.assertEqual(prepared['entries'][0]['request']['adviser'], adviser)

    def test_project_and_request_origins_follow_merge_precedence(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / '.scoville').mkdir()
            config_file = project / '.scoville/config.json'
            saved = {'ask': {'advisers': [{'id': 'claude', 'effort': 'ultra'}]}}
            config_file.write_text(json.dumps(saved), encoding='utf-8')
            bad = self.cli('--project-root', temporary)
            self.assertEqual(bad.returncode, 1)
            error = json.loads(bad.stdout)['error']
            self.assertIn(str(config_file), error)
            self.assertIn("ask.advisers[0].effort (adviser claude)='ultra'", error)
            request = {'operation': 'resolve', 'project_root': temporary,
                       'overrides': {'presets': {'claude': {'effort': 'high'}}}}
            corrected = self.cli(request=request)
            self.assertEqual(corrected.returncode, 0, corrected.stdout)
            self.assertEqual(json.loads(corrected.stdout)['config']['advisers'][0]['effort'], 'high')
            request['overrides']['presets']['claude']['effort'] = 'ultra'
            bad = self.cli(request=request)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("request.overrides.presets.claude.effort='ultra'", json.loads(bad.stdout)['error'])

    def test_case_sensitive_mode_and_existing_workspace(self):
        request = {'operation': 'prepare', **prepare_request([ADVISERS[1]])}
        bad = self.cli(request={**request, 'mode': 'Review'})
        self.assertEqual(bad.returncode, 1)
        self.assertIn("request.mode='Review'", json.loads(bad.stdout)['error'])
        self.assertEqual(self.cli(request=request).returncode, 0)
        bad = self.cli(request={**request, 'cwd': 'relative/project'})
        self.assertEqual(bad.returncode, 1)
        self.assertIn('request.cwd=', json.loads(bad.stdout)['error'])
        self.assertEqual(self.cli(request=request).returncode, 0)

    def test_plaintext_and_per_adviser_reference(self):
        question = 'Line 1\n"quoted"\npath\\file.py\nÄnderung 😀'
        prepared = ask.prepare(prepare_request(['claude', 'fable'], question=question))
        for entry in prepared['entries']:
            request = entry['request']
            self.assertTrue(request['prompt'].endswith(question))
            self.assertIn('consultation_reference: ' + entry['reference'], request['prompt'])
            self.assertIn('workspace_root: ' + request['cwd'], request['prompt'])
            self.assertIn('adviser_id: ' + entry['adviser']['id'], request['prompt'])

    def test_fresh_followup_and_overrides_reach_cli(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            project = base / 'project'
            project.mkdir()
            (project / '.scoville').mkdir()
            config = project / '.scoville/config.json'
            config.write_text(json.dumps({'ask': {'presets': {'claude': {'effort': 'medium'}}}}), encoding='utf-8')
            question = 'Line 1\n"quoted"\npath\\file.py\nÄnderung 😀'
            question_file = base / 'question.txt'
            question_file.write_text(question, encoding='utf-8')
            request_file = base / 'request.json'
            common = ['--question-file', str(question_file), '--mode', 'review',
                      '--scope', 'sample.py', '--reference', 'round-1', '--output-file', str(request_file)]
            generated = self.cli('--project-root', str(project), '--adviser', 'claude', *common,
                                 '--effort', 'max', '--web-tools', 'true',
                                 '--timeout-seconds', '45', '--max-budget-usd', '3')
            self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
            self.assertEqual(json.loads(generated.stdout)['request_file'], str(request_file))
            initial = json.loads(request_file.read_text(encoding='utf-8'))
            self.assertEqual(initial['adviser']['effort'], 'max')
            self.assertTrue(initial['claude']['web_tools'])
            self.assertEqual(initial['claude']['timeout_seconds'], 45)
            self.assertEqual(initial['claude']['max_budget_usd'], 3)
            self.assertEqual(json.loads(config.read_text(encoding='utf-8'))['ask']['presets']['claude']['effort'], 'medium')

            fake_cli = base / 'fake_claude.py'
            fake_cli.write_text(
                "import json, os, sys\nfrom pathlib import Path\n"
                "sys.stdin.reconfigure(encoding='utf-8')\n"
                "prompt = sys.stdin.read()\n"
                "Path('received.json').write_text(json.dumps({'args': sys.argv[1:], 'prompt': prompt, 'cwd': os.getcwd()}), encoding='utf-8')\n"
                "print(json.dumps({'result': 'Complete answer', 'session_id': 'exact-session', 'permission_denials': []}))\n",
                encoding='utf-8')
            launch = ("import sys; sys.path.insert(0, sys.argv[1]); import ask; "
                      "ask.ask_claude.configure_standard_streams(); "
                      "ask.ask_claude.resolve_claude_command=lambda: [sys.executable, sys.argv[2]]; "
                      "sys.exit(ask.main(['--input-file', sys.argv[3]]))")

            def consume(path):
                completed = subprocess.run([sys.executable, '-c', launch, str(SCRIPTS), str(fake_cli), str(path)],
                                           text=True, encoding='utf-8', capture_output=True)
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                return json.loads(completed.stdout), json.loads((project / 'received.json').read_text(encoding='utf-8'))

            answer, received = consume(request_file)
            self.assertEqual(received['prompt'], initial['prompt'])
            self.assertTrue(received['prompt'].endswith(question))
            self.assertEqual(Path(received['cwd']), project)
            self.assertNotIn('--resume', received['args'])
            self.assertIn('WebSearch,WebFetch', received['args'][received['args'].index('--tools') + 1])
            self.assertTrue(answer['continuation_available'])
            config.write_text(json.dumps({'ask': {'presets': {'claude': {'effort': 'high'}},
                                                       'claude': {'web_tools': False, 'max_budget_usd': 20}}}), encoding='utf-8')
            question_file.write_text('Follow-up\nOnly sample.py', encoding='utf-8')
            followup_file = base / 'followup.json'
            followup = ['--resume-request', str(request_file), '--session-id', answer['session_id'],
                        '--question-file', str(question_file), '--mode', 'review', '--scope', 'sample.py',
                        '--reference', 'round-2', '--output-file', str(followup_file)]
            generated = self.cli(*followup)
            self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
            resumed = json.loads(followup_file.read_text(encoding='utf-8'))
            for key in ('adviser', 'claude', 'cwd'):
                self.assertEqual(resumed[key], initial[key])
            answer, received = consume(followup_file)
            self.assertEqual(answer['context_mode'], 'continued')
            self.assertEqual(received['args'][received['args'].index('--resume') + 1], 'exact-session')
            self.assertEqual(received['prompt'], resumed['prompt'])
            self.assertIn('round-2:claude', received['prompt'])
            self.assertNotIn(question, received['prompt'])
            generated = self.cli(*followup, '--model', 'claude-fable-5-1', '--effort', 'high', '--web-tools', 'false')
            self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
            answer, received = consume(followup_file)
            self.assertEqual(answer['requested_model'], 'claude-fable-5-1')
            self.assertEqual(answer['requested_effort'], 'high')
            self.assertEqual(received['args'][received['args'].index('--tools') + 1], 'Read,Grep,Glob')
            self.assertEqual(received['args'][received['args'].index('--resume') + 1], 'exact-session')

    def test_invalid_preparation_never_replaces_output_then_correction_succeeds(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            question = base / 'question.txt'
            question.write_text('Review sample.py', encoding='utf-8')
            output = base / 'request.json'
            output.write_text('existing evidence', encoding='utf-8')
            valid = ['--project-root', temporary, '--adviser', 'claude', '--question-file', str(question),
                     '--mode', 'review', '--scope', 'sample.py', '--reference', 'first', '--output-file', str(output)]
            for extra, diagnostic in [(['--effort', 'ultra'], 'effort'),
                                      (['--model', 'model with spaces'], 'model'),
                                      (['--timeout-seconds', '0'], '--timeout-seconds'),
                                      (['--session-id', 'unexpected'], '--resume-request')]:
                failed = self.cli(*valid, *extra)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn(diagnostic, failed.stdout + failed.stderr)
                self.assertEqual(output.read_text(encoding='utf-8'), 'existing evidence')
            good = self.cli(*valid)
            self.assertEqual(good.returncode, 0, good.stdout)
            retained = output.read_bytes()
            followup = ['--resume-request', str(output), '--question-file', str(question),
                        '--mode', 'review', '--scope', 'sample.py', '--reference', 'next', '--output-file', str(output)]
            failed = self.cli(*followup)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('--session-id', failed.stdout)
            self.assertEqual(output.read_bytes(), retained)
            corrected = self.cli(*followup, '--session-id', 'exact-session')
            self.assertEqual(corrected.returncode, 0, corrected.stdout)
            self.assertEqual(json.loads(output.read_text(encoding='utf-8'))['session_id'], 'exact-session')

    def test_invalid_project_root_and_native_model_report_fields(self):
        for request, fragment, fixed in [
            ({'project_root': 5}, 'request.project_root=5', {'project_root': str(PACKAGE)}),
            ({'overrides': {'advisers': [{'id': 'sol', 'model': 'model with spaces'}]}},
             'without whitespace', {'overrides': {'advisers': ['sol']}}),
        ]:
            bad = self.cli(request={'operation': 'resolve', **request})
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn(fragment, bad.stdout)
            good = self.cli(request={'operation': 'resolve', **fixed})
            self.assertEqual(good.returncode, 0, good.stdout)

    def test_preparation_diagnostics_name_cli_flags_and_corrected_calls_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            question = base / 'question.txt'
            question.write_text('Review sample.py', encoding='utf-8')
            first = base / 'first.json'
            flags = ['--project-root', temporary, '--adviser', 'claude', '--question-file', str(question),
                     '--mode', 'review', '--scope', 'sample.py', '--reference', 'first', '--output-file', str(first)]
            for extra, expected in [
                (['--project-root', 'relative-project'], "--project-root='relative-project'"),
                (['--timeout-seconds', 'inf'], '--timeout-seconds=inf'),
                (['--question-file', str(base / 'missing.txt')], '--question-file'),
            ]:
                with self.subTest(extra=extra):
                    failed = self.cli(*flags, *extra)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertIn(expected, json.loads(failed.stdout)['error'])
                    corrected = self.cli(*flags)
                    self.assertEqual(corrected.returncode, 0, corrected.stdout)
                    self.assertEqual(json.loads(first.read_text(encoding='utf-8'))['operation'], 'claude')
            following = base / 'next.json'
            followup = ['--resume-request', str(first), '--session-id', 'exact-id', '--question-file', str(question),
                        '--mode', 'review', '--scope', 'sample.py', '--reference', 'next', '--output-file', str(following)]
            failed = self.cli(*followup, '--resume-request', str(base / 'missing.json'))
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('--resume-request', json.loads(failed.stdout)['error'])
            corrected = self.cli(*followup)
            self.assertEqual(corrected.returncode, 0, corrected.stdout)
            self.assertEqual(json.loads(following.read_text(encoding='utf-8'))['session_id'], 'exact-id')


if __name__ == '__main__':
    unittest.main()
