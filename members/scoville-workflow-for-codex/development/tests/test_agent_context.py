"""Packaged native telemetry boundaries and the real followup argument consumer."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from test_contract import PACKAGE, SUITE_ROOT, copy_started_profile
import check_agent_context as context_helper

AGENT='/root/manager/executor'
THREAD='fixture-child-session'


def events(used=44):
    usage={'input_tokens':used-1,'output_tokens':1,'total_tokens':used}
    payloads=[
        ('session_meta',{'id':THREAD,'source':{'subagent':{'thread_spawn':{'agent_path':AGENT,'parent_thread_id':'fixture-parent'}}}}),
        ('event_msg',{'type':'task_started','turn_id':'turn-1'}),
        ('turn_context',{'turn_id':'turn-1','model':'gpt-6-luna','effort':'medium'}),
        ('token_usage_record',{'thread_id':THREAD,'turn_id':'turn-1','usage':usage}),
        ('event_msg',{'type':'token_count','info':{'last_token_usage':usage.copy(),'model_context_window':100}}),
        ('event_msg',{'type':'task_complete','turn_id':'turn-1'}),
    ]
    return [{'ordinal':n,'type':kind,'payload':payload} for n,(kind,payload) in enumerate(payloads)]


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.root=self.base/'project'
        copy_started_profile(self.root)
        self.sessions=self.base/'sessions';self.sessions.mkdir()
        self.rollout=self.sessions/('rollout-'+THREAD+'.jsonl')
        self.write(events())

    def write(self,data):
        self.rollout.write_text('\n'.join(json.dumps(x) for x in data)+'\n',encoding='utf-8')

    def run_helper(self,*extra):
        return subprocess.run([sys.executable,str(PACKAGE/'scripts/check_agent_context.py'),
            '--agent-id',AGENT,'--project-root',str(self.root),
            '--sessions-root',str(self.sessions),*extra],env={**os.environ,'CODEX_THREAD_ID':'fixture-parent'},capture_output=True,text=True,encoding='utf-8')

    def test_below_exact_and_above_default45(self):
        for used,action in ((44,'reuse'),(45,'spawn'),(46,'spawn')):
            with self.subTest(used=used):
                self.write(events(used));run=self.run_helper()
                self.assertEqual(run.returncode,0,run.stderr)
                data=json.loads(run.stdout)
                self.assertEqual(data['action'],action)
                self.assertEqual(data['used_tokens'],used)
                self.assertEqual(data['threshold_percent'],45)
                self.assertEqual((data['thread_id'], data['parent_thread_id']), (THREAD, 'fixture-parent'))
                self.assertEqual((data['model'],data['reasoning_effort']),('gpt-6-luna','medium'))
                self.assertEqual(data.get('replacement_of'), AGENT if action == 'spawn' else None)
                if action == 'reuse': self.assertNotIn('replacement_of', data)
        (self.root/'.scoville').mkdir()
        (self.root/'.scoville/config.json').write_text('{"workflow":{"context_threshold_percent":20}}')
        for used,action in ((19,'reuse'),(20,'spawn'),(21,'spawn')):
            self.write(events(used));data=json.loads(self.run_helper().stdout)
            self.assertEqual((data['threshold_percent'],data['action']),(20,action))

    def test_lookup_uses_exact_handle_and_current_parent_not_filename(self):
        renamed = self.sessions / 'unrelated-filename.jsonl'
        self.rollout.rename(renamed)
        foreign = events()
        foreign[0]['payload']['source']['subagent']['thread_spawn']['parent_thread_id'] = 'other-parent'
        self.write(foreign)
        self.assertEqual(json.loads(self.run_helper().stdout)['thread_id'], THREAD)
        foreign[0]['payload']['source']['subagent']['thread_spawn']['parent_thread_id'] = 'fixture-parent'
        foreign[0]['payload']['source']['subagent']['thread_spawn']['agent_path'] = AGENT + '_similar'
        self.write(foreign)
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'reuse')
        renamed.unlink()
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'blocked')

    def test_ambiguous_valid_headers_block_even_with_invalid_telemetry(self):
        duplicate = self.sessions / 'duplicate.jsonl'
        duplicate.write_text(json.dumps(events()[0]) + '\n', encoding='utf-8')
        result = json.loads(self.run_helper().stdout)
        self.assertEqual(result['action'], 'blocked')
        self.assertIn('2 matches', result['diagnostic'])
        duplicate.unlink()
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'reuse')

    def test_historical_invalid_headers_are_nonmatches_with_bounded_reads(self):
        invalid = [b'', b'not json\n', b'\xff\n', b'[]\n',
            b'{"ordinal":true,"type":"session_meta","payload":{}}\n',
            b'{"ordinal":0,"type":"event_msg","payload":{}}\n',
            b'{"ordinal":0,"type":"session_meta","payload":{"source":{"subagent":[]}}}\n',
            b' ' * (context_helper.HEADER_LIMIT + 1)]
        for number, header in enumerate(invalid):
            (self.sessions / f'historical-{number}.jsonl').write_bytes(header)
        self.assertEqual(json.loads(self.run_helper().stdout)['action'], 'reuse')
        calls = []
        original = Path.open
        class HeaderStream:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def readline(self, size):
                calls.append(size)
                return b' ' * size
        with patch.dict(os.environ, CODEX_THREAD_ID='fixture-parent'), patch.object(Path, 'open', return_value=HeaderStream()):
            with self.assertRaisesRegex(ValueError, '0 matches'):
                context_helper.resolve_session(AGENT, self.sessions)
        self.assertTrue(calls)
        self.assertEqual(set(calls), {context_helper.HEADER_LIMIT + 1})

    def test_environment_and_io_failures_cannot_select_a_partial_match(self):
        for parent in ('', 'bad parent', 'x' * 129):
            with patch.dict(os.environ, CODEX_THREAD_ID=parent):
                with self.assertRaisesRegex(ValueError, 'CODEX_THREAD_ID'):
                    context_helper.resolve_session(AGENT, self.sessions)
        with patch.dict(os.environ, CODEX_THREAD_ID='fixture-parent'):
            with patch.object(Path, 'open', side_effect=PermissionError('unreadable header')):
                with self.assertRaisesRegex(PermissionError, 'unreadable header'):
                    context_helper.resolve_session(AGENT, self.sessions)
            def failed_walk(root, *, onerror):
                onerror(PermissionError('unreadable directory'))
                return iter(())
            with patch.object(context_helper.os, 'walk', side_effect=failed_walk):
                with self.assertRaisesRegex(PermissionError, 'unreadable directory'):
                    context_helper.resolve_session(AGENT, self.sessions)

    def test_removed_thread_flag_rejects_before_measurement_or_publication(self):
        failed = self.run_helper('--thread-id', THREAD)
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, '')
        run, assignment = self.builder('executor', 'W-001/step-1', extra=('--thread-id', THREAD))
        self.assertEqual(run.returncode, 2)
        self.assertFalse(assignment.exists())
        run, assignment = self.builder('executor', 'W-001/step-1', extra=('--manager-agent-id', '/root/manager'))
        self.assertEqual(run.returncode, 2)
        self.assertFalse(assignment.exists())

    def test_invalid_missing_active_compacted_and_wrong_binding_never_dispatch(self):
        cases=[]
        data=events();data.pop(3);cases.append(data)
        data=events();data[0]['payload']['id']='other';cases.append(data)
        data=events();data[0]['payload']['source']['subagent']['thread_spawn']['agent_path']='/root/other';cases.append(data)
        data=events();data[3]['payload']['turn_id']='old';cases.append(data)
        data=events();data[4]['payload']['info']['last_token_usage']['total_tokens']=10;cases.append(data)
        data=events();data.append({'ordinal':6,'type':'event_msg','payload':{'type':'task_started','turn_id':'turn-2'}});cases.append(data)
        data=events();data.insert(5,{'ordinal':5,'type':'compacted','payload':{}});data[6]['ordinal']=6;cases.append(data)
        data=events();data[4]['payload']={'type':'task_aborted','turn_id':'turn-1'};cases.append(data)
        data=events();data[4]['ordinal']=3;cases.append(data)
        data=events();data[2]['payload'].pop('effort');cases.append(data)
        for used in (0,101,True):
            cases.append(events(used))
        for n,data in enumerate(cases):
            with self.subTest(case=n):
                self.write(data);run=self.run_helper();result=json.loads(run.stdout)
                self.assertNotEqual(run.returncode,0)
                self.assertEqual(result['action'],'blocked')
                self.assertNotIn('replacement_of', result)
                self.assertTrue(result['diagnostic'])
        self.rollout.unlink()
        self.assertEqual(json.loads(self.run_helper().stdout)['action'],'blocked')

    def test_inherited_parent_metadata_keeps_child_binding_and_turn_fence(self):
        parent = {'type':'session_meta','payload':{'id':'fixture-parent','source':'vscode'}}
        ancestor = {'type':'session_meta','payload':{'id':'fixture-grandparent','source':'vscode'}}
        def renumber(data):
            for n,event in enumerate(data):event['ordinal']=n
            return data
        data=events();data.insert(1,copy.deepcopy(parent));self.write(renumber(data))
        self.assertEqual(json.loads(self.run_helper().stdout)['action'],'reuse')
        data=events();data.insert(1,copy.deepcopy(data[0]));self.write(renumber(data))
        self.assertEqual(json.loads(self.run_helper().stdout)['action'],'reuse')
        data=events();p=copy.deepcopy(parent)
        p['payload']['source']={'subagent':{'thread_spawn':{'parent_thread_id':'fixture-grandparent'}}}
        data[1:1]=[p,copy.deepcopy(ancestor)];self.write(renumber(data))
        self.assertEqual(json.loads(self.run_helper().stdout)['action'],'reuse')
        invalid=[]
        data=events();data.insert(1,copy.deepcopy(ancestor));invalid.append(data)
        data=events();data.insert(3,copy.deepcopy(parent));invalid.append(data)
        data=events();duplicate=copy.deepcopy(data[0])
        duplicate['payload']['source']['subagent']['thread_spawn']['parent_thread_id']='another-parent'
        data.insert(1,duplicate);invalid.append(data)
        data=events();duplicate=copy.deepcopy(data[0])
        duplicate['payload']['source']['subagent']['thread_spawn']['agent_path']='/root/other'
        data.insert(1,duplicate);invalid.append(data)
        data=events();data.insert(0,copy.deepcopy(parent));invalid.append(data)
        data=events();data[1:1]=[copy.deepcopy(parent),copy.deepcopy(parent)];invalid.append(data)
        data=events();p=copy.deepcopy(parent)
        p['payload']['source']={'subagent':{'thread_spawn':{'parent_thread_id':THREAD}}}
        data.insert(1,p);invalid.append(data)
        data=events();data.insert(3,copy.deepcopy(data[0]));invalid.append(data)
        data=events();data[0]['payload']['source']['subagent']['thread_spawn'].pop('parent_thread_id');invalid.append(data)
        data=events();extra=copy.deepcopy(ancestor);extra['payload'].pop('id')
        data[1:1]=[copy.deepcopy(parent),extra];invalid.append(data)
        data=events();data[1:1]=[copy.deepcopy(parent),copy.deepcopy(ancestor)];invalid.append(data)
        for data in invalid:
            self.write(renumber(data));run=self.run_helper()
            self.assertNotEqual(run.returncode,0)
            self.assertEqual(json.loads(run.stdout)['action'],'blocked')

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
                        self.assertIn('Next task:', message)
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
        # The manager's agent check owns the measurement; the builder uses its result.
        self.rollout.unlink();run,path=self.builder('executor','W-001/step-1')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertTrue(path.is_file())

    def test_retained_session_path_skips_search_and_keeps_binding(self):
        first=json.loads(self.run_helper().stdout)
        self.assertEqual(first['session_path'],str(self.rollout.resolve()))
        empty=self.base/'empty sessions';empty.mkdir()
        run=subprocess.run([sys.executable,str(PACKAGE/'scripts/check_agent_context.py'),'--agent-id',AGENT,
            '--project-root',str(self.root),'--sessions-root',str(empty),'--session-path',first['session_path']],
            env={**os.environ,'CODEX_THREAD_ID':'fixture-parent'},capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual({k:v for k,v in json.loads(run.stdout).items()},first)
        foreign=events();foreign[0]['payload']['source']['subagent']['thread_spawn']['agent_path']=AGENT+'_other'
        self.write(foreign)
        for path in (self.rollout,self.base/'missing.jsonl'):
            blocked=self.run_helper('--session-path',str(path))
            self.assertNotEqual(blocked.returncode,0)
            result=json.loads(blocked.stdout)
            self.assertEqual(result['action'],'blocked')
            self.assertIn('--session-path',result['diagnostic'])
            self.assertIn('rerun once without --session-path',result['diagnostic'])

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
