from pathlib import Path
import hashlib
import html
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
# Exercise the actual package, including bundled shared helpers and defaults.
SUITE_ROOT = ROOT.parents[1]
_build_spec = importlib.util.spec_from_file_location("workflow_test_build", SUITE_ROOT / "development/build_suite.py")
_builder = importlib.util.module_from_spec(_build_spec)
_build_spec.loader.exec_module(_builder)
_test_package = tempfile.TemporaryDirectory(prefix="workflow-tests-", ignore_cleanup_errors=True)
PACKAGE = Path(_test_package.name) / "scoville-workflow-for-codex"
_config = _builder.load(SUITE_ROOT, 'codex')
_member = next(m for m in _config['members'] if m['name'] == PACKAGE.name)
for _package_member in (_member, *(m for m in _config['members'] if m['name'] in {'scoville-code', 'scoville-plan'})):
    for _name, _data in _builder.payload(SUITE_ROOT, _package_member, _config).items():
        _target = Path(_test_package.name) / _name
        _target.parent.mkdir(parents=True, exist_ok=True)
        _target.write_bytes(_data)
MODEL_RESOLVER = PACKAGE / "scripts/resolve_model_pair.py"
SELECTOR = SUITE_ROOT / "members/scoville-plan/scoville-plan/scripts/select_context.py"
sys.path.insert(0, str(PACKAGE / "scripts"))
import resolve_model_pair as model_resolver
import build_dispatch_prompt as prompt_builder

class NativeWorkflowContractTests(unittest.TestCase):
    def test_configuration_mode_and_model_mode_are_exclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            base = [sys.executable, str(MODEL_RESOLVER), '--project-root', directory]
            for extra in ([], ['--show-config', '--role', 'executor']):
                failed = subprocess.run(base + extra, text=True, encoding='utf-8', capture_output=True)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn('usage:', failed.stderr)
                self.assertIn('--show-config', failed.stderr)
            corrected = subprocess.run(base + ['--show-config'], text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(corrected.returncode, 0, corrected.stderr)
            self.assertEqual(set(json.loads(corrected.stdout)['config']), {'schema_version', 'execute', 'review', 'explore'})

    def test_model_resolver_rejects_malformed_user_config(self):
        source = (PACKAGE / "assets" / "workflow.toml").read_text(encoding="utf-8")
        for altered, diagnostic in (
            (source.replace('schema_version = 1', 'schema_version = true', 1), "schema_version"),
            (source.replace('reasoning = "high"', 'reasoning = []', 1), "invalid review.ultra_low values"),
            (source.replace('reasoning = "high"', 'reasoning = { bad = true }', 1), "invalid review.ultra_low values"),
            (source.replace('[execute.ultra_low]\nmodel = "gpt-6-luna"\nreasoning = "medium"',
                            '[execute.ultra_low]\nmodel = "gpt-6-luna"\nreasoning = []', 1), "invalid execute.ultra_low values"),
        ):
            with self.subTest(diagnostic=diagnostic), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "workflow.toml"
                path.write_text(altered, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, diagnostic):
                    model_resolver.load_config(path, Path(directory))

    def test_models_preserve_five_routes_and_executor_overrides(self):
        config = model_resolver.load_config(PACKAGE / 'assets/workflow.toml', PACKAGE)
        self.assertEqual(set(config), {'schema_version', 'execute', 'review', 'explore'})
        expected = {
            'ultra_low': ('gpt-6-luna', 'medium', 'gpt-6-luna', 'high'),
            'low': ('gpt-6.1-sol', 'low', 'gpt-6.1-sol', 'medium'),
            'medium': ('gpt-6.1-sol', 'high', 'gpt-6.1-sol', 'high'),
            'high': ('gpt-6.1-sol', 'xhigh', 'gpt-6-astra', 'high'),
            'ultra_high': ('gpt-6-astra', 'high', 'gpt-6-astra', 'xhigh'),
        }
        with tempfile.TemporaryDirectory() as directory:
            for role, table, offset in [('executor', 'execute', 0), ('reviewer', 'review', 2)]:
                self.assertEqual(set(config[table]), set(expected))
                for route, values in expected.items():
                    with self.subTest(role=role, route=route):
                        pair = dict(model=values[offset], thinking=values[offset + 1], route=route)
                        self.assertEqual(model_resolver.resolve(config, role, route), pair)
                        result = subprocess.run(
                            [sys.executable, str(MODEL_RESOLVER), '--project-root', directory,
                             '--role', role, '--route', route],
                            text=True, encoding='utf-8', capture_output=True)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertEqual(json.loads(result.stdout), dict(valid=True, **pair))
        pair = model_resolver.resolve(config, 'executor', 'low', 'custom', 'high')
        self.assertEqual(pair, dict(model='custom', thinking='high', route='low'))
        self.assertEqual(model_resolver.resolve(config, 'reviewer', 'low', 'custom', 'medium'),
                         dict(model='custom', thinking='medium', route='low'))

    def test_explicit_plan_reasoning_reaches_dispatch_and_resolver(self):
        fixture_spec = importlib.util.spec_from_file_location('reasoning_fixture',
            SUITE_ROOT / 'members/scoville-plan/development/tests/test_select_context.py')
        fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(fixture)
        config = model_resolver.load_config(PACKAGE / 'assets/workflow.toml', PACKAGE)
        for level in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'):
            with self.subTest(level=level), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / 'docs/plans').mkdir(parents=True)
                (root / 'docs/decisions').mkdir()
                (root / 'PROJECT_INDEX.md').write_text('---\nformat_version: 1\nactive_plan: PLAN-0001\n---\n', encoding='utf-8')
                annotation = '[execute: reasoning=' + level + ']'
                (root / 'docs/plans/0001-test.md').write_text(fixture.plan().replace(
                    '1. Inspect the producer.', '1. ' + annotation + ' Inspect the producer.'), encoding='utf-8')
                (root / 'docs/decisions/0001-test.md').write_text(fixture.DECISION, encoding='utf-8')
                context = prompt_builder.select_unit(SELECTOR, root, 'W-003')
                self.assertIn(annotation, context['work_item']['source_text'])
                prompt = prompt_builder.build_prompt('executor', root, 'manager', 'test', context, {})
                self.assertIn(annotation, prompt)
                pair = model_resolver.resolve(config, 'executor', 'low', override_reasoning=level)
                self.assertEqual(pair['thinking'], level)

    def test_correction_uses_executor_route_without_attempt_state(self):
        config = model_resolver.load_config(PACKAGE / 'assets/workflow.toml', PACKAGE)
        original = {'model': 'gpt-6-luna', 'thinking': 'high'}
        correction = model_resolver.resolve(config, 'executor', 'medium',
                                            original['model'], original['thinking'])
        self.assertEqual(correction['model'], original['model'])
        self.assertEqual(correction['thinking'], original['thinking'])
        with self.assertRaises(ValueError):
            model_resolver.resolve(config, 'repair', 'medium')

    def test_missing_route_diagnostic_and_corrected_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, str(MODEL_RESOLVER), '--project-root', directory,
                       '--role', 'reviewer']
            failed = subprocess.run(command, text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(failed.returncode, 1)
            self.assertIn('--route', json.loads(failed.stdout)['diagnostic'])
            corrected = subprocess.run(command + ['--route', 'medium', '--override-model',
                                       'gpt-6-astra', '--override-reasoning', 'medium'],
                                       text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(corrected.returncode, 0, corrected.stdout)
            self.assertEqual(json.loads(corrected.stdout)['thinking'], 'medium')

    def test_actual_selector_source_and_crlf_survive_dispatch(self):
        fixture_spec = importlib.util.spec_from_file_location('plan_fixture',
            SUITE_ROOT / 'members/scoville-plan/development/tests/test_select_context.py')
        fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(fixture)
        for ending in ('\n', '\r\n'):
            with self.subTest(ending=repr(ending)), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / 'Änderung 中文'
                (root / 'docs/plans').mkdir(parents=True)
                (root / 'docs/decisions').mkdir()
                files = {'PROJECT_INDEX.md': '---\nformat_version: 1\nactive_plan: PLAN-0001\n---\n',
                         'docs/plans/0001-test.md': fixture.plan(10).replace(
                             'Evidence: [old executor attempt, old reviewer attempt]',
                             'Evidence: Prüfung mit Komma, Ergebnis erhalten.'),
                         'docs/decisions/0001-test.md': fixture.DECISION}
                for name, content in files.items():
                    (root / name).write_bytes(content.replace('\n', ending).encode('utf-8'))
                before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                for unit in ('W-004', 'W-003', 'W-003/step-2', 'W-003/steps-1-2'):
                    context = prompt_builder.select_unit(SELECTOR, root, unit)
                    completed = subprocess.run([sys.executable, '-B', str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                        '--unit', unit, '--role', 'executor', '--project-root', str(root),
                        '--manager-agent-id', 'manager'],
                        input='{}', text=True, encoding='utf-8', capture_output=True,
                        env={**os.environ, 'PYTHONIOENCODING': 'cp1252'})
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    prompt = completed.stdout
                    embedded = prompt.split('## Work Item context\n', 1)[1]
                    self.assertEqual(embedded.rstrip() + '\n', context['work_item']['context_text'])
                    self.assertEqual(prompt.count(context['work_item']['context_text'].rstrip()), 1)
                    self.assertIn('## Assigned unit\n' + unit, prompt)
                    self.assertFalse(prompt.startswith('{'))
                    for decision in context['decisions']:
                        self.assertNotIn(decision, prompt)
                    self.assertIn(context['work_item']['acceptance'], prompt)
                    self.assertIn(context['work_item']['outcome'], prompt)
                    self.assertEqual(context['work_item']['unit'], unit)
                    self.assertTrue(context['work_item']['source_text'])
                for unit in ('W-003/step-1..2', 'W-003/step-0', 'W-999', 'W-003/step-4'):
                    with self.assertRaises(ValueError):
                        prompt_builder.select_unit(SELECTOR, root, unit)
                self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_dispatch_budget_failure_and_corrected_assignment_with_bundled_selector(self):
        fixture_spec = importlib.util.spec_from_file_location('budget_fixture',
            SUITE_ROOT / 'members/scoville-plan/development/tests/test_select_context.py')
        fixture = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(fixture)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'docs/plans').mkdir(parents=True)
            (root / 'docs/decisions').mkdir()
            (root / 'PROJECT_INDEX.md').write_text(
                '---\nformat_version: 1\nactive_plan: PLAN-0001\n---\n', encoding='utf-8')
            outcome = 'é' * 20_000 + ' END-OF-REQUIRED-CONTEXT'
            (root / 'docs/plans/0001-test.md').write_text(fixture.plan().replace(
                'Outcome: Return ✓ without unrelated bodies.', 'Outcome: ' + outcome), encoding='utf-8')
            (root / 'docs/decisions/0001-test.md').write_text(fixture.DECISION, encoding='utf-8')
            assignment = root / 'assignment.md'
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            command = [sys.executable, '-B', str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                       '--project-root', str(root), '--unit', 'W-003/step-1', '--role', 'executor',
                       '--format', 'create', '--manager-agent-id', 'manager', '--project-name', 'Budget test',
                       '--worker-number', '1', '--route', 'medium', '--assignment-file', str(assignment)]
            for extra, code in (([], 'OUTPUT_BUDGET_EXCEEDED'),
                                (['--max-output-bytes', '512'], 'OUTPUT_BUDGET_EXCEEDED'),
                                (['--max-output-bytes', '0'], 'OUTPUT_BUDGET_INVALID')):
                failed = subprocess.run(command + extra, text=True, encoding='utf-8', capture_output=True)
                self.assertEqual(failed.returncode, 1, failed.stderr)
                self.assertEqual(failed.stdout, '')
                diagnostic = json.JSONDecoder().raw_decode(failed.stderr.split('ERROR: Plan selection failed: ', 1)[1])[0]['diagnostics'][0]
                self.assertEqual(diagnostic['code'], code)
                if code == 'OUTPUT_BUDGET_EXCEEDED':
                    required = diagnostic['observed']['required_bytes']
                    self.assertGreater(required, 65_536)
                    self.assertIn(f'--max-output-bytes {required}', diagnostic['message'])
                self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
            corrected = subprocess.run(command + ['--max-output-bytes', str(required)],
                                       text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(corrected.returncode, 0, corrected.stderr)
            arguments = json.loads(corrected.stdout)
            self.assertEqual(set(arguments), {'message', 'task_name', 'fork_turns', 'model', 'reasoning_effort'})
            self.assertEqual(arguments['fork_turns'], 'none')
            self.assertIn(str(assignment), arguments['message'])
            self.assertIn('PLAN-0001/W-003/step-1', arguments['message'])
            # Consume the generated file as directed by the native message.
            prompt = assignment.read_text(encoding='utf-8')
            self.assertIn(outcome, prompt)
            self.assertIn('## Assigned unit\nW-003/step-1', prompt)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*')
                                      if p.is_file() and p != assignment})

    def test_normal_messages_pass_unchanged_to_review_and_correction(self):
        context = {'plan': {'non_goals': '## Non-goals\n\n- No publication.'}, 'work_item': {'unit': 'W-001', 'source_text': 'Work', 'context_text': 'Work'}}
        for role, field, text in [
            ('reviewer', 'executor_result', 'Completed. Import checks passed. No rollback proof yet.'),
            ('executor', 'reviewer_result', 'Changes requested. src/import.py: rollback leaves partial writes. Fix the transaction.')]:
            prompt = prompt_builder.build_prompt(role, PACKAGE, 'manager', '', context,
                {field: text, 'supplemental_context': 'Initial review of the named change against Work Item Acceptance. No earlier assessment.'})
            self.assertIn(text, prompt)
            self.assertNotIn('SCOVILLE_RESULT_V1', prompt)
            self.assertNotIn('code_changed=', prompt)
        with self.assertRaisesRegex(ValueError, '--executor-result'):
            prompt_builder.build_prompt('reviewer', PACKAGE, 'manager', '', context, {})

    def test_obsolete_transfer_inputs_are_rejected(self):
        context = {'plan': {'non_goals': '## Non-goals\n\n- No publication.'},
                   'work_item': {'unit': 'W-001', 'source_text': 'Work', 'context_text': 'Work'}}
        for obsolete in ('context_handoff', 'predecessor_agent_id'):
            with self.subTest(obsolete=obsolete), self.assertRaisesRegex(ValueError, 'unknown role input'):
                prompt_builder.build_prompt('executor', PACKAGE, 'manager', '', context, {obsolete: 'old'})

    def test_failed_child_remaining_work_uses_ordinary_assignment(self):
        context = {'plan': {'non_goals': '## Non-goals\n\n- No publication.'},
                   'work_item': {'unit': 'W-001/step-2', 'source_text': 'Work', 'context_text': 'Work'}}
        facts = 'Prior writer confirmed stopped. A and its checks passed. Only B remains; no release.'
        prompt = prompt_builder.build_prompt('executor', PACKAGE, 'manager', '', context,
                                             {'supplemental_context': facts})
        self.assertIn(facts, prompt)
        self.assertIn('## Work Item context', prompt)
        for forbidden in ('HANDOFF_ACCEPTED', 'TAKEOVER_COMPLETE', 'rollover_pending', 'check_context_checkpoint'):
            self.assertNotIn(forbidden, prompt)


if __name__ == '__main__':
    unittest.main()
