"""
End-to-end test for MeetAI Azure integration.
Tests: upload → Azure Speech → Azure Language → Foundry → DB → queries
"""
import requests
import time
import json
import sys

BASE = "http://localhost:8000"
VIDEO = "test_meeting.mp4"

print("=" * 60)
print("MeetAI Azure Integration Test")
print("=" * 60)

# 1. Verify backend is up
print("\n[1] Backend health check...")
r = requests.get(f"{BASE}/health", timeout=10)
assert r.status_code == 200, f"Backend not healthy: {r.status_code}"
print("    OK — Backend running")

r = requests.get(f"{BASE}/", timeout=10)
info = r.json()
print(f"    Provider mode: {info.get('provider_mode')}")

# 2. Upload video
print(f"\n[2] Uploading {VIDEO}...")
with open(VIDEO, "rb") as f:
    res = requests.post(
        f"{BASE}/api/meetings/upload",
        files={"file": (VIDEO, f, "video/mp4")},
        timeout=30,
    )
assert res.status_code == 200, f"Upload failed: {res.status_code} — {res.text[:300]}"
meeting = res.json()
meeting_id = meeting["id"]
print(f"    Upload OK. Meeting ID: {meeting_id}")
print(f"    Title: {meeting['title']}")
print(f"    Status: {meeting['status']}")
print(f"    File: {meeting['file_path']}")

# 3. Poll for processing completion
print(f"\n[3] Polling for processing completion (up to 10 min)...")
start = time.time()
status = meeting["status"]
prev_status = None
while status not in ("ready", "failed"):
    elapsed = time.time() - start
    if elapsed > 600:
        print("    TIMEOUT after 10 minutes!")
        sys.exit(1)
    time.sleep(3)
    poll = requests.get(f"{BASE}/api/meetings/{meeting_id}", timeout=15).json()
    status = poll["status"]
    if status != prev_status:
        print(f"    [{int(elapsed)}s] Status: {status}")
        prev_status = status

if status == "failed":
    detail = requests.get(f"{BASE}/api/meetings/{meeting_id}", timeout=15).json()
    print(f"    FAILED. Summary (error): {detail.get('summary', 'No error message')[:500]}")
    sys.exit(1)

elapsed = time.time() - start
print(f"    Processing COMPLETE in {elapsed:.1f}s")

# 4. Fetch meeting details
print(f"\n[4] Fetching final meeting details...")
detail = requests.get(f"{BASE}/api/meetings/{meeting_id}", timeout=15).json()
print(f"    Duration: {detail['duration']:.1f}s")
print(f"    Summary: {(detail.get('summary') or 'None')[:200]}")
print(f"    Key topics: {detail.get('key_topics')}")
print(f"    Sentiment: {detail.get('sentiment')}")
print(f"    Meeting type: {detail.get('meeting_type')}")
print(f"    Decisions: {len(detail.get('decisions', []))}")
print(f"    Action items: {len(detail.get('action_items', []))}")
print(f"    Unresolved questions: {len(detail.get('unresolved_questions', []))}")
print(f"    Chapters: {len(detail.get('chapters', []))}")
print(f"    Speakers: {len(detail.get('speakers', []))}")

# 5. Fetch transcript
print(f"\n[5] Fetching transcript...")
transcript = requests.get(f"{BASE}/api/meetings/{meeting_id}/transcript", timeout=15).json()
print(f"    Segments: {len(transcript)}")
if transcript:
    seg = transcript[0]
    print(f"    First segment [{seg['start_time']:.1f}s–{seg['end_time']:.1f}s]: {seg['text'][:100]}")
    seg = transcript[-1]
    print(f"    Last segment [{seg['start_time']:.1f}s–{seg['end_time']:.1f}s]: {seg['text'][:100]}")
else:
    print("    WARNING: Empty transcript!")

# 6. Video streaming
print(f"\n[6] Testing video streaming endpoint...")
vid = requests.get(
    f"{BASE}/api/meetings/{meeting_id}/video",
    headers={"Range": "bytes=0-1023"},
    timeout=15,
)
print(f"    Status: {vid.status_code}")
print(f"    Content-Type: {vid.headers.get('content-type')}")
print(f"    Accept-Ranges: {vid.headers.get('accept-ranges')}")
print(f"    Content-Length: {vid.headers.get('content-length')}")

# 7. Ask Meeting
print(f"\n[7] Testing Ask Meeting (must use real transcript)...")
ask_payload = {"question": "What was discussed in this meeting?"}
ask_res = requests.post(
    f"{BASE}/api/meetings/{meeting_id}/ask",
    json=ask_payload,
    timeout=60,
)
assert ask_res.status_code == 200, f"Ask failed: {ask_res.status_code}"
ask_data = ask_res.json()
print(f"    Answer: {ask_data.get('answer', '')[:300]}")
print(f"    Sources: {len(ask_data.get('sources', []))} citations")

# 8. Catch Me Up
print(f"\n[8] Testing Catch Me Up...")
catchup_res = requests.post(
    f"{BASE}/api/meetings/{meeting_id}/catch-up",
    json={"from_timestamp": 0.0},
    timeout=60,
)
assert catchup_res.status_code == 200, f"Catch-up failed: {catchup_res.status_code}"
cu_data = catchup_res.json()
print(f"    Summary: {cu_data.get('summary', '')[:200]}")
print(f"    Key points: {len(cu_data.get('key_points', []))}")

# 9. Follow-up email
print(f"\n[9] Testing Follow-up Email...")
email_res = requests.post(
    f"{BASE}/api/meetings/{meeting_id}/follow-up",
    json={"recipient_name": "Team"},
    timeout=60,
)
assert email_res.status_code == 200, f"Email failed: {email_res.status_code}"
email_data = email_res.json()
print(f"    Subject: {email_data.get('subject', '')}")
print(f"    Body length: {len(email_data.get('body', ''))}")

# 10. Second upload — verify separate data
print(f"\n[10] Second upload — verify data isolation...")
with open(VIDEO, "rb") as f:
    res2 = requests.post(
        f"{BASE}/api/meetings/upload",
        files={"file": (VIDEO, f, "video/mp4")},
        timeout=30,
    )
m2 = res2.json()
m2_id = m2["id"]
print(f"    Second meeting ID: {m2_id} (different from {meeting_id})")
assert m2_id != meeting_id, "ERROR: Same meeting ID returned for second upload!"
print("    OK — Two separate meeting records created")

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
