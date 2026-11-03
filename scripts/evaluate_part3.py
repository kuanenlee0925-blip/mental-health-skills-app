"""Re-run fictional scenarios and write evidence. No network or runtime DB writes.
Run: backend/.venv/Scripts/python.exe -m scripts.evaluate_part3
"""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import subprocess
import unittest
from backend.test_app import AppTests

ROOT = Path(__file__).resolve().parents[1]
CASES = [
('chat_persist_retry_and_restart', 'Alex asks for the steps, repeats the same request, then restarts the API.', '200 with saved demo reply; same reply ID on retry; exactly two ordered messages after restart.'),
('failure_retry_does_not_invent_or_duplicate_reply', 'Alex submits [demo:fail] twice with one request ID.', 'Both return 502; one failed user message, no invented assistant; changing content with that ID returns 409.'),
('support_rule_skips_both_calls_and_uses_event', 'Fictional role-play includes HURT   myself.', 'Application support notice, no assistant reply, zero model calls; not a general distress detector.'),
('missing_configuration_and_budget', 'Live settings are absent, then the call budget is zero.', '503 not_configured, then call_limit; zero actual provider calls.'),
('old_preferences_migrate_without_losing_history', 'An existing v1 profile upgrades, selects larger text, and restarts.', 'Standard text default; large choice persists; original message ID preserved; invalid size returns 422.'),
('sessions_idempotency_ordering_and_terminal_guard', 'Alex stops, retries saving, and a stale checkpoint arrives.', 'One stopped row; stale checkpoint cannot revert it; terminal overwrite gives 409; 59,999 ms completion gives 422.'),
('scoped_retrieval_empty_then_saved_history', 'Alex asks about a past session with sharing off, then on.', 'Off retrieves no sessions; on retrieves the stopped record and returns its exact reference ID.'),
('retrieval_other_conversation_and_user_scope', 'Alex starts another conversation; a separate fictional user has a record.', 'No cross-conversation messages without consent; consent never exposes the other user; direct table query rejected.'),
('sql_rejects_writes_comments_joins_unions_and_scope_bypass', 'Model proposes a write, extra statement, comment, UNION, wildcard, oversized limit or scope bypass.', 'All unsafe plans rejected; [demo:unsafe] returns 422; sessions remain readable.'),
('invalid_reference_and_provider_timeout', 'Model invents a record ID, then times out.', 'invalid_references then 504; zero assistant messages persisted.'),
('storage_failure_stops_model_calls', 'Question storage is unavailable before generation.', '503; zero provider calls; no claim that the operation was saved.'),
('delete_retains_preferences_and_busy_prevents_midcall_changes', 'Alex deletes fictional history during and after a pending request.', '429 while busy; confirmed deletion then succeeds, keeps ring preference, and has no foreign-key violations.'),
]
PACER_EXPECTED = [
'Twelve phases; final phase is sixth exhale; completion at 60,087 ms including scheduling delay.',
'Pause at 2,350 ms freezes cue; explicit resume excludes 10,000 ms; final active time 2,500 ms.',
'Stop at 4,050 ms stays stopped after a later 70,000 ms callback.',
'A jump from 100 to 65,000 ms produces interrupted, never completed.',
'Stop during pause records 100 ms active plus 10,000 ms excluded.',
'Fractional pause snapshots all keep active time 900 ms and wall = active + excluded.',
]

def main():
    rows = []
    for method, scenario, expected in CASES:
        result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(AppTests('test_' + method))
        rows.append({'id': f'S{len(rows)+1:02}', 'scenario': scenario, 'expected': expected,
                     'observed': 'All listed assertions passed.' if result.wasSuccessful() else 'FAILED: inspect test output.',
                     'passed': result.wasSuccessful(), 'test': 'backend/test_app.py::test_' + method})
        if not result.wasSuccessful():
            for _, detail in result.failures + result.errors:
                print(detail)
    run = subprocess.run(['node', '--test', '--test-reporter=tap', 'src/pacer.test.js'], cwd=ROOT/'frontend', text=True, capture_output=True)
    tests = re.findall(r'^(ok|not ok) \d+ - (.+)$', run.stdout, re.M)
    if len(tests) != len(PACER_EXPECTED):
        raise RuntimeError('Unexpected pacer report: ' + run.stdout + run.stderr)
    for (status, name), expected in zip(tests, PACER_EXPECTED):
        rows.append({'id': f'S{len(rows)+1:02}', 'scenario': name, 'expected': expected,
                     'observed': 'All listed assertions passed.' if status == 'ok' else 'FAILED',
                     'passed': status == 'ok', 'test': 'frontend/src/pacer.test.js::' + name})
    checks = [
        {'id':'B1', 'rule':'Retries, failures, and restarts never invent or duplicate a saved assistant reply.', 'cases':['S01','S02','S10','S11']},
        {'id':'B2', 'rule':'Retrieved history obeys consent and server scope, and unsafe SQL is rejected.', 'cases':['S07','S08','S09','S10']},
        {'id':'B3', 'rule':'Only the final planned phase completes an exercise; pauses and interruptions do not silently complete it.', 'cases':['S06','S13','S14','S15','S16','S17','S18']},
    ]
    for check in checks:
        check['passed'] = all(r['passed'] for r in rows if r['id'] in check['cases'])
    report = {'recorded_at':datetime.now(timezone.utc).isoformat(), 'mode':'deterministic fixtures and simulated clock; no live calls', 'scenarios':rows, 'cross_case_checks':checks}
    dest = ROOT/'docs/evidence/part3-scenarios.json'
    dest.write_text(json.dumps(report,indent=2),encoding='utf-8')
    lines=['# Part Three fictional scenario evaluation','',f"Recorded {report['recorded_at']}. {report['mode']}.",'',
           'These observations come from executing assertions in the linked source tests. Timing uses a simulated monotonic clock; browser observations are documented separately.', '',
           '| ID | Fictional scenario | Expected | Observed |','| --- | --- | --- | --- |']
    for r in rows:
        lines.append(f"| {r['id']} | {r['scenario']} | {r['expected']} | {'PASS' if r['passed'] else 'FAIL'} — {r['observed']} |")
    lines += ['', '## Three cross-case behavior checks', '']
    for c in checks:
        lines.append(f"- **{c['id']} — {'PASS' if c['passed'] else 'FAIL'}:** {c['rule']} Cases: {', '.join(c['cases'])}.")
    lines += ['', 'Reproduce with `backend/.venv/Scripts/python.exe -m scripts.evaluate_part3`. Backend cases use new temporary databases. The delete case affects only its isolated fixture. No paid model or real microphone is used.', '', 'Machine-readable evidence and exact test mappings: [part3-scenarios.json](evidence/part3-scenarios.json).']
    (ROOT/'docs/part3-evaluation.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'scenarios':len(rows),'passed':sum(r['passed'] for r in rows),'cross_case_checks':checks},indent=2))
    return 0 if all(r['passed'] for r in rows) and run.returncode == 0 else 1

if __name__ == '__main__':
    raise SystemExit(main())
