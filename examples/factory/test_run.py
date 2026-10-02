"""Offline characterization/regression tests for the factory runner's refusal gate.

Run from examples/: python -m unittest factory.test_run -v
No providers, credentials, worker side effects or user-home state are used.
"""
from __future__ import annotations

import contextlib
import copy
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from . import blackboard, run


class RefusalGateTests(unittest.TestCase):
    def invoke(self, decision):
        with tempfile.TemporaryDirectory() as temp:
            work_dir = Path(temp)
            argv = ['factory.run', '--request', 'synthetic fixture',
                    '--project-id', 'fixture', '--work-dir', temp, '--dry-script']
            with (
                mock.patch.dict(os.environ, {'OPENAI_API_KEY': 'offline-fixture-not-a-key'}, clear=True),
                mock.patch.object(run.sys, 'argv', argv),
                mock.patch.object(run.router, 'route', return_value=copy.deepcopy(decision)),
                mock.patch.object(run.script_factory, 'draft_script', return_value=[]) as script,
                mock.patch.object(run.voice_synth, 'synthesize') as voice,
                mock.patch('urllib.request.urlopen', side_effect=AssertionError('network is forbidden')),
                contextlib.redirect_stdout(io.StringIO()) as output,
            ):
                status = run.main()
            state = blackboard.read('fixture', work_dir=work_dir)
            self.assertEqual(status, 0)  # preserve the existing blocked-run exit contract
            voice.assert_not_called()
            return script.call_count, state['status'], output.getvalue()

    @staticmethod
    def decision(auto_ship=True, reason=None):
        return {'task_type': 'blog', 'pipeline': 'blog', 'auto_ship': auto_ship,
                'required_workers': ['script'], 'estimated_cost_usd': 0.0,
                'blocking_reason': reason}

    def test_false_without_reason_blocks(self):
        for reason in (None, '', False):
            with self.subTest(reason=reason):
                calls, state, output = self.invoke(self.decision(False, reason))
                self.assertEqual(calls, 0)
                self.assertEqual(state, 'blocked')
                self.assertIn('not running workers', output)

    def test_false_with_reason_still_blocks(self):
        calls, state, output = self.invoke(self.decision(False, 'Needs human approval'))
        self.assertEqual(calls, 0)
        self.assertEqual(state, 'blocked')
        self.assertIn('Needs human approval', output)

    def test_missing_auto_ship_blocks(self):
        decision = self.decision()
        del decision['auto_ship']
        calls, state, _ = self.invoke(decision)
        self.assertEqual(calls, 0)
        self.assertEqual(state, 'blocked')

    def test_non_boolean_auto_ship_blocks(self):
        for value in (None, 0, 1, 'true', 'false', '', [], {}):
            with self.subTest(value=value):
                calls, state, _ = self.invoke(self.decision(value))
                self.assertEqual(calls, 0)
                self.assertEqual(state, 'blocked')

    def test_malformed_decision_blocks(self):
        for value in (None, [], 'true', True, 1, {}):
            with self.subTest(value=value):
                calls, state, _ = self.invoke(value)
                self.assertEqual(calls, 0)
                self.assertEqual(state, 'blocked')

    def test_true_with_null_reason_reaches_only_mock_script(self):
        calls, _, output = self.invoke(self.decision(True, None))
        self.assertEqual(calls, 1)
        self.assertIn('--dry-script', output)

    def test_true_with_blocking_reason_preserves_existing_refusal(self):
        calls, _, output = self.invoke(self.decision(True, 'Existing blocker'))
        self.assertEqual(calls, 0)
        self.assertIn('Existing blocker', output)


if __name__ == '__main__':
    unittest.main()
