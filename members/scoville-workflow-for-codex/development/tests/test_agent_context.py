import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_contract import PACKAGE, SUITE_ROOT, copy_started_profile
sys.path.insert(0, str(PACKAGE / 'scripts'))
import check_agent_context as context_helper

AGENT = '/root/manager/executor'
THREAD = 'fixture-child-session'


def events(used=44):
    usage = {'input_tokens': used - 1, 'output_tokens': 1, 'total_tokens': used}
    return [
        {'ordinal': 0, 'type': 'session_meta', 'payload': {'id': THREAD, 'source': {'subagent': {'thread_spawn': {'agent_path': AGENT, 'parent_thread_id': 'fixture-parent'}}}}},
        {'ordinal': 1, 'type': 'event_msg', 'payload': {'type': 'task_started', 'turn_id': 'turn-1', 'model_context_window': 100}},
        {'ordinal': 2, 'type': 'turn_context', 'payload': {'turn_id': 'turn-1', 'model': 'gpt-6-luna', 'effort': 'medium'}},
        {'ordinal': 3, 'type': 'token_usage_record', 'payload': {'thread_id': THREAD, 'turn_id': 'turn-1', 'usage': copy.deepcopy(usage)}},
        {'ordinal': 4, 'type': 'event_msg', 'payload': {'type': 'token_count', 'info': {'last_token_usage': copy.deepcopy(usage), 'model_context_window': 100}}},
    ]


def renumber(data):
    for number, event in enumerate(data):
        event['ordinal'] = number
    return data


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'profile'
        copy_started_profile(self.root)
        self.sessions = self.base / 'sessions'
        self.sessions.mkdir()
        self.rollout = self.sessions / 'unrelated-filename.jsonl'
        self.write(events())

    def write(self, data):
        self.rollout.write_text(''.join(json.dumps(e) + '\n' for e in data), encoding='utf-8')

    def run_helper(self, *extra, identity=THREAD):
        return subprocess.run([sys.executable, str(PACKAGE / 'scripts/check_agent_context.py'),
            '--project-root', str(self.root), '--sessions-root', str(self.sessions), *extra],
            env={**os.environ, 'CODEX_THREAD_ID': identity}, capture_output=True, text=True, encoding='utf-8')

    def blocked(self, *extra, **kwargs):
        run = self.run_helper(*extra, **kwargs)
        self.assertNotEqual(run.returncode, 0)
        result = json.loads(run.stdout)
        self.assertEqual(result['action'], 'blocked')
        self.assertTrue(result['diagnostic'])
        self.assertNotIn('reason', result)

    def test_only_own_active_last_call_controls_threshold(self):
        for used, action in ((44, 'continue'), (45, 'handover'), (90, 'handover')):
            self.write(events(used))
            run = self.run_helper()
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads(run.stdout)
            self.assertEqual(data['action'], action)
            self.assertEqual(data['used_tokens'], used)
            self.assertEqual(data['threshold_percent'], 45)
            self.assertEqual((data['thread_id'], data['parent_thread_id'], data['agent_id']),
                             (THREAD, 'fixture-parent', AGENT))
            self.assertEqual(data['reason'], 'threshold' if action == 'handover' else None)
        (self.root / '.scoville').mkdir(exist_ok=True)
        (self.root / '.scoville/config.json').write_text('{"workflow":{"context_threshold_percent":20}}')
        self.write(events(20))
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'handover')

    def test_identity_is_native_own_header_not_filename_or_parent_environment(self):
        foreign = events()
        foreign[0]['payload']['id'] = 'foreign'
        (self.sessions / (THREAD + '.jsonl')).write_text(json.dumps(foreign[0]) + '\n')
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'continue')
        self.blocked(identity='fixture-parent')
        for identity in ('', 'bad parent', 'x' * 129):
            self.blocked(identity=identity)
        manager = events()
        manager[0]['payload']['source'] = 'vscode'
        self.write(manager)
        self.blocked()

    def test_ambiguous_and_unreadable_sessions_block(self):
        duplicate = self.sessions / 'duplicate.jsonl'
        duplicate.write_bytes(self.rollout.read_bytes())
        self.blocked()
        duplicate.unlink()
        with patch.dict(os.environ, CODEX_THREAD_ID=THREAD):
            with patch.object(Path, 'open', side_effect=PermissionError('unreadable header')):
                with self.assertRaises(PermissionError):
                    context_helper.resolve_session(self.sessions)
            def failed_walk(root, *, onerror):
                onerror(PermissionError('unreadable directory'))
                return iter(())
            with patch.object(context_helper.os, 'walk', side_effect=failed_walk):
                with self.assertRaises(PermissionError):
                    context_helper.resolve_session(self.sessions)

    def test_missing_foreign_stale_and_finished_turns_block(self):
        invalid = []
        data = events(); data.pop(3); invalid.append(data)
        data = events(); data[3]['payload']['thread_id'] = 'foreign'; invalid.append(data)
        data = events(); data[3]['payload']['turn_id'] = 'old'; invalid.append(data)
        for window in (None, True, 0, '100'):
            data = events(); data[1]['payload']['model_context_window'] = window; invalid.append(data)
        data = events(); data.append({'type': 'event_msg', 'payload': {'type': 'task_started', 'turn_id': 'turn-2'}}); invalid.append(renumber(data))
        for state in ('task_complete', 'task_failed', 'task_aborted'):
            data = events(); data.append({'type': 'event_msg', 'payload': {'type': state, 'turn_id': 'turn-1'}}); invalid.append(renumber(data))
        for used in (0, 101, True):
            invalid.append(events(used))
        data = events(); data[4]['ordinal'] = 3; invalid.append(data)
        for data in invalid:
            with self.subTest(data=data):
                self.write(data)
                self.blocked()

    def test_own_compaction_forces_handover_even_after_usage_falls_and_on_reuse(self):
        for prior_turn in (False, True):
            data = events(10)
            data.insert(3, {'type': 'compacted', 'payload': {}})
            if prior_turn:
                data += [{'type': 'event_msg', 'payload': {'type': 'task_complete', 'turn_id': 'turn-1'}}]
                later = events(5)[1:]
                for event in later:
                    if 'turn_id' in event['payload']:
                        event['payload']['turn_id'] = 'turn-2'
                data += later
            self.write(renumber(data))
            result = json.loads(self.run_helper().stdout)
            self.assertEqual((result['action'], result['reason']), ('handover', 'compaction'))
            self.assertNotIn('used_tokens', result)

    def test_live_call_uses_new_usage_and_current_turn_start_window(self):
        data = events(20)
        newer = copy.deepcopy(events(45)[3])
        data.append(newer)
        self.write(renumber(data))
        result = json.loads(self.run_helper().stdout)
        self.assertEqual((result['used_tokens'], result['action']), (45, 'handover'))
        for change in ('missing_window', 'new_context', 'foreign_usage'):
            broken = copy.deepcopy(data)
            if change == 'missing_window':
                broken[1]['payload'].pop('model_context_window')
            elif change == 'new_context':
                broken.append(copy.deepcopy(broken[2]))
            else:
                broken[-1]['payload']['thread_id'] = 'foreign'
            self.write(renumber(broken))
            self.blocked()

    def test_first_call_needs_no_delayed_token_count(self):
        data = events(44)[:4]
        self.write(data)
        result = json.loads(self.run_helper().stdout)
        self.assertEqual((result['used_tokens'], result['model_context_window'], result['action']), (44, 100, 'continue'))

    def test_own_compaction_without_new_pair_still_hands_over_but_failed_turn_blocks(self):
        data = events()[:3] + [{'type': 'compacted', 'payload': {}}]
        self.write(renumber(data))
        result = json.loads(self.run_helper().stdout)
        self.assertEqual((result['action'], result['reason']), ('handover', 'compaction'))
        self.assertNotIn('used_tokens', result)
        data.append({'type': 'event_msg', 'payload': {'type': 'task_failed', 'turn_id': 'turn-1'}})
        self.write(renumber(data))
        self.blocked()

    def test_inherited_compaction_is_ignored_but_invalid_parent_chains_block(self):
        parent = {'type': 'session_meta', 'payload': {'id': 'fixture-parent', 'source': 'vscode'}}
        data = events(); data[1:1] = [copy.deepcopy(parent), {'type': 'compacted', 'payload': {}}]
        self.write(renumber(data))
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'continue')
        data = events(); data.insert(1, copy.deepcopy(data[0])); self.write(renumber(data))
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'continue')
        for index, identity in ((1, 'foreign'), (3, 'fixture-parent')):
            data = events(); extra = copy.deepcopy(parent); extra['payload']['id'] = identity
            data.insert(index, extra); self.write(renumber(data)); self.blocked()

    def test_incomplete_tail_and_corrupt_complete_record_never_use_old_sample(self):
        valid = self.rollout.read_bytes()
        for tail in (b'{"ordinal":5', b'not json\n', b'\xff\n'):
            self.rollout.write_bytes(valid + tail)
            self.blocked()
        self.rollout.write_bytes(valid)
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'continue')

    def test_retained_own_path_skips_search_and_rejects_changed_identity(self):
        result = json.loads(self.run_helper().stdout)
        empty = self.base / 'empty'; empty.mkdir()
        run = self.run_helper('--sessions-root', str(empty), '--session-path', result['session_path'])
        self.assertEqual(run.returncode, 0, run.stderr)
        foreign = events(); foreign[0]['payload']['id'] = 'foreign'; self.write(foreign)
        self.blocked('--session-path', result['session_path'])

    def test_old_manager_cli_cannot_silently_measure_another_agent(self):
        failed = self.run_helper('--agent-id', AGENT)
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, '')

    def builder(self,role,unit,model='gpt-6-luna',thinking='medium',extra=(),language='German'):
        assignment=self.base/('assignment-'+str(len(list(self.base.glob('assignment*'))))+'.txt')
        result_file=self.base/'result.txt';result_file.write_text('done; changed_paths: owner.py; before: snapshot; checks: pass.')
        argv=[sys.executable,str(PACKAGE/'scripts/build_dispatch_prompt.py'),'--communication-language',language,'--project-root',str(self.root),
              '--role',role,'--unit',unit,'--format','create','--project-name','fixture','--worker-number','1','--agent-id',AGENT,
              '--assignment-file',str(assignment),*extra]
        if model is not None:argv+=['--model',model]
        if thinking is not None:argv+=['--thinking',thinking]
        if role=='reviewer':argv+=['--executor-result',str(result_file)]
        if role=='explorer':argv+=['--supplemental-context',str(result_file)]
        run=subprocess.run(argv,env={**os.environ,'CODEX_HOME':str(self.base),'CODEX_THREAD_ID':'fixture-parent'},capture_output=True,text=True,encoding='utf-8')
        return run,assignment

    def test_reused_roles_receive_current_explicit_language_and_original_inputs(self):
        for role in ('explorer','executor','reviewer'):
            for language in ('German','English'):
                with self.subTest(role=role,language=language):
                    self.write(events())
                    run,path=self.builder(role,'W-001/step-1',language=language)
                    self.assertEqual(run.returncode,0,run.stderr)
                    native=json.loads(run.stdout)
                    def followup_task(*,target,message):
                        self.assertEqual(target,AGENT)
                        self.assertNotIn('Your commentary and messages go to the manager.', message)
                        self.assertNotIn('Communication language:', message)
                        # The native consumer needs the assignment path and identity,
                        # not one optional English introduction.
                        self.assertIn(str(path), message)
                        self.assertIn(str(path),message)
                    followup_task(**native)
                    full=path.read_text(encoding='utf-8')
                    self.assertIn(f'Communication language: {language}.',full)
                    self.assertNotIn('Your commentary and messages go to the manager.', full)
                    self.assertNotIn('shell_command_rules:', full)
                    self.assertNotIn('Read applicable AGENTS.md', full)
                    self.assertIn('1. [status: in_progress] Read the canonical files.',full)
                    self.assertNotIn('Check the local record shapes.',full)
                    if role!='executor':
                        self.assertIn((self.base/'result.txt').read_text(),full)

    def test_native_followup_requires_both_pair_flags_and_does_not_measure_again(self):
        for role,unit in (('executor','W-001/step-1'),('reviewer','W-001/step-1'),('reviewer','W-001')):
            self.write(events());run,path=self.builder(role,unit)
            self.assertEqual(run.returncode,0,run.stderr)
            native=json.loads(run.stdout)
            def followup_task(*,target,message):
                self.assertEqual(target,AGENT)
                self.assertIn(str(path),message)
                self.assertIn('PLAN-0001/'+unit,message)
            followup_task(**native)
            self.assertTrue(path.is_file())
        for model,thinking in ((None,'medium'),('gpt-6-luna',None)):
            run,path=self.builder('executor','W-001/step-1',model,thinking)
            self.assertNotEqual(run.returncode,0)
            self.assertEqual(run.stdout,'')
            self.assertFalse(path.exists())
        # The builder never measures context; the subagent owns its active check.
        self.rollout.unlink();run,path=self.builder('executor','W-001/step-1')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertTrue(path.is_file())

    def test_retained_pair_cannot_ignore_explicit_step_annotations(self):
        plan = self.root / 'docs/plans/0001-validate-profile.md'
        original = plan.read_text(encoding='utf-8')
        for annotation in ('[route: high]', '[execute: model=gpt-6.1-sol; reasoning=high]'):
            plan.write_text(original.replace('1. [status: in_progress] Read the canonical files.',
                            '1. [status: in_progress] ' + annotation + ' Read the canonical files.', 1), encoding='utf-8')
            run, path = self.builder('executor', 'W-001/step-1')
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('different explicit pair', run.stderr)
            self.assertFalse(path.exists())
        plan.write_text(original, encoding='utf-8')

    def test_followup_rejects_inferred_route_before_publication(self):
        run, path = self.builder('executor', 'W-001/step-1', extra=('--route', 'low'))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('--route cannot combine', run.stderr)
        self.assertFalse(path.exists())


if __name__=='__main__':unittest.main()
