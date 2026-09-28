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
for _name, _data in _builder.payload(SUITE_ROOT, _member, _config).items():
    _target = Path(_test_package.name) / _name
    _target.parent.mkdir(parents=True, exist_ok=True)
    _target.write_bytes(_data)
MODEL_RESOLVER = PACKAGE / "scripts/resolve_model_pair.py"
SELECTOR = SUITE_ROOT / "members/scoville-plan/scoville-plan/scripts/select_context.py"
sys.path.insert(0, str(PACKAGE / "scripts"))
import resolve_model_pair as model_resolver
import build_dispatch_prompt as prompt_builder

class NativeWorkflowContractTests(unittest.TestCase):
    def test_model_resolver_rejects_malformed_user_config(self):
        source = (PACKAGE / "assets" / "workflow.toml").read_text(encoding="utf-8")
        for altered, diagnostic in (
            (source.replace('schema_version = 1', 'schema_version = true', 1), "schema_version"),
            (source.replace('reasoning = "medium"', 'reasoning = []', 1), "invalid execute.ultra_low values"),
            (source.replace('reasoning = "medium"', 'reasoning = { bad = true }', 1), "invalid execute.ultra_low values"),
        ):
            with self.subTest(diagnostic=diagnostic), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "workflow.toml"
                path.write_text(altered, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, diagnostic):
                    model_resolver.load_config(path)

    def test_models_preserve_five_routes_and_executor_overrides(self):
        config = model_resolver.load_config(PACKAGE / 'assets/workflow.toml', PACKAGE)
        self.assertEqual(set(config), {'schema_version', 'context', 'execute', 'review'})
        routes = ('ultra_low', 'low', 'medium', 'high', 'ultra_high')
        for role, table in [('executor', 'execute'), ('reviewer', 'review')]:
            self.assertEqual(set(config[table]), set(routes))
            for route in routes:
                pair = model_resolver.resolve(config, role, route)
                self.assertEqual(pair['model'], config[table][route]['model'])
                self.assertEqual(pair['thinking'], config[table][route]['reasoning'])
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
                        '--return-to-thread-id', 'manager'],
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

    def test_normal_messages_pass_unchanged_to_review_and_correction(self):
        context = {'work_item': {'unit': 'W-001', 'source_text': 'Work', 'context_text': 'Work'}}
        for role, field, text in [
            ('reviewer', 'executor_result', 'Completed. Import checks passed. No rollback proof yet.'),
            ('executor', 'reviewer_result', 'Changes requested. src/import.py: rollback leaves partial writes. Fix the transaction.')]:
            prompt = prompt_builder.build_prompt(role, PACKAGE, 'manager', '', context, {field: text})
            self.assertIn(text, prompt)
            self.assertNotIn('SCOVILLE_RESULT_V1', prompt)
            self.assertNotIn('code_changed=', prompt)
        with self.assertRaisesRegex(ValueError, '--executor-result'):
            prompt_builder.build_prompt('reviewer', PACKAGE, 'manager', '', context, {})

    def test_rollover_supplies_direct_receipt_recipient(self):
        context = {'work_item': {'unit': 'W-001', 'source_text': 'Work', 'context_text': 'Work'}}
        data = {'context_handoff': 'Checks A passed; B remains.', 'predecessor_thread_id': 'worker-a',
                'supplemental_context': 'B must pass. Keep existing authorization and rollback limits.'}
        for role in ('executor', 'reviewer'):
            inputs = dict(data)
            if role == 'reviewer': inputs['executor_result'] = 'Completed. See actual diff.'
            prompt = prompt_builder.build_prompt(role, PACKAGE, 'manager', '', context, inputs)
            self.assertIn('## predecessor_thread_id\nworker-a', prompt)
            self.assertIn('call send_message_to_thread with predecessor_thread_id as threadId', prompt)
            self.assertIn(data['context_handoff'], prompt)
        del data['predecessor_thread_id']
        with self.assertRaisesRegex(ValueError, '--predecessor-thread-id'):
            prompt_builder.build_prompt('executor', PACKAGE, 'manager', '', context, data)

    def test_continuation_cli_omits_completed_item_and_keeps_required_facts(self):
        spec = importlib.util.spec_from_file_location('continuation_fixture',
            SUITE_ROOT / 'members/scoville-plan/development/tests/test_select_context.py')
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'docs/plans').mkdir(parents=True)
            (root / 'docs/decisions').mkdir()
            (root / 'PROJECT_INDEX.md').write_text('---\nformat_version: 1\nactive_plan: PLAN-0001\n---\n', encoding='utf-8')
            (root / 'docs/plans/0001-test.md').write_text(fixture.plan(), encoding='utf-8')
            (root / 'docs/decisions/0001-test.md').write_text(fixture.DECISION, encoding='utf-8')
            handoff = 'Only inspect src/import.py final diff. Implementation and 34 checks passed. Return the result.'
            facts = 'Acceptance: no unintended diff. Preserve pending user approval for deployment. Evidence: checks.log. No release or scan.'
            (root / 'handoff.txt').write_text(handoff, encoding='utf-8')
            (root / 'facts.txt').write_text(facts, encoding='utf-8')
            selected = prompt_builder.select_unit(SELECTOR, root, 'W-003/steps-1-2')
            for role in ('executor', 'reviewer'):
                command = [sys.executable, '-B', str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                    '--unit', 'W-003/steps-1-2', '--role', role, '--project-root', str(root),
                    '--return-to-thread-id', 'manager', '--predecessor-thread-id', 'previous',
                    '--context-handoff', str(root / 'handoff.txt')]
                failed = subprocess.run(command, text=True, encoding='utf-8', capture_output=True)
                self.assertNotEqual(failed.returncode, 0)
                self.assertEqual(failed.stdout, '')
                self.assertIn('--supplemental-context', failed.stderr)
                result = subprocess.run(command + ['--supplemental-context', str(root / 'facts.txt')],
                    text=True, encoding='utf-8', capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(handoff, result.stdout)
                self.assertIn(facts, result.stdout)
                self.assertIn('return_to_thread_id=manager', result.stdout)
                self.assertIn('## Assigned unit\nW-003/steps-1-2', result.stdout)
                self.assertNotIn(selected['work_item']['context_text'].strip(), result.stdout)
                self.assertNotIn(selected['work_item']['source_text'].strip(), result.stdout)
                if role == 'reviewer': self.assertIn('Stay read-only.', result.stdout)
            # Empty handoffs must not silently switch back to full-item dispatch.
            (root / 'handoff.txt').write_text('  ', encoding='utf-8')
            failed = subprocess.run(command + ['--supplemental-context', str(root / 'facts.txt')],
                text=True, encoding='utf-8', capture_output=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, '')
            self.assertIn('--context-handoff', failed.stderr)


if __name__ == '__main__':
    unittest.main()
