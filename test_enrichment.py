import sys
import os
os.chdir(r"e:\PROJECTS\MeetAI — Agentic AI Meeting Assistant\backend")
sys.path.insert(0, r"e:\PROJECTS\MeetAI — Agentic AI Meeting Assistant\backend")

from providers.azure_speech import _enrich_speakers_with_names

def test(desc, segs, expected):
    test_segs = [dict(s) for s in segs]
    _enrich_speakers_with_names(test_segs)
    actual = [s['speaker'] for s in test_segs]
    passed = actual == expected
    print('[PASS]' if passed else '[FAIL]', desc)
    if not passed:
        print('  Exp:', expected)
        print('  Got:', actual)
    return passed

r = []
r.append(test('Hi this is Eric Johnson maps',   [{'speaker': 'Speaker 1', 'text': 'Hi, this is Eric Johnson.'}], ['Eric Johnson']))
r.append(test('i am Eric Johnson maps',         [{'speaker': 'Speaker 2', 'text': 'i am Eric Johnson'}], ['Eric Johnson']))
r.append(test('My name is Alice Smith maps',    [{'speaker': 'Speaker 3', 'text': 'My name is Alice Smith.'}], ['Alice Smith']))
r.append(test('sorry stays Speaker 1',          [{'speaker': 'Speaker 1', 'text': 'I am sorry.'}], ['Speaker 1']))
r.append(test('supportive stays Speaker 2',     [{'speaker': 'Speaker 2', 'text': 'This is supportive.'}], ['Speaker 2']))
r.append(test('checking right stays Spkr 3',    [{'speaker': 'Speaker 3', 'text': 'I am checking right now.'}], ['Speaker 3']))
r.append(test('great news stays Speaker 2',     [{'speaker': 'Speaker 2', 'text': 'This is great news!'}], ['Speaker 2']))
r.append(test('on the call stays Speaker 1',    [{'speaker': 'Speaker 1', 'text': 'I am on the call.'}], ['Speaker 1']))
r.append(test('Mixed: Eric maps others stay', [
    {'speaker': 'Speaker 1', 'text': 'Good morning.'},
    {'speaker': 'Speaker 2', 'text': 'Hi, this is Eric Johnson. Happy to be here.'},
    {'speaker': 'Speaker 1', 'text': 'Thanks.'},
    {'speaker': 'Speaker 2', 'text': 'I am sorry, can you repeat?'},
], ['Speaker 1', 'Eric Johnson', 'Speaker 1', 'Eric Johnson']))

print()
print('ALL PASSED' if all(r) else f'{r.count(False)} TEST(S) FAILED')
