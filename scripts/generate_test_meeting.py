"""
Generate a realistic meeting test MP4 with speech audio.
Uses edge-tts + FFmpeg stdin/stdout, collects all PCM frames, writes one WAV.
"""
import asyncio
import subprocess
import os
import sys
import wave
import io
import shutil

MEETING_SCRIPT = [
    ("en-US-JennyNeural", "Good morning everyone. Let us get started with today sprint planning meeting."),
    ("en-US-GuyNeural",   "Thanks Jenny. I wanted to discuss the API refactoring task first. We need to decide if we are going to use REST or GraphQL going forward."),
    ("en-US-JennyNeural", "I think REST is the safer choice for now given our timeline. We can always migrate later."),
    ("en-US-GuyNeural",   "Agreed. So the decision is to stick with REST for this sprint. I will create the tickets. Can you review the pull requests by end of Thursday?"),
    ("en-US-JennyNeural", "Yes, I will have the code review done by Thursday. Also, we need to discuss the database migration. Should we do it all at once or in phases?"),
    ("en-US-GuyNeural",   "Let us do a phased migration starting with the user table to reduce risk."),
    ("en-US-JennyNeural", "That makes sense. Action item: David will prepare the migration scripts by next Monday."),
    ("en-US-GuyNeural",   "One blocker. We are waiting on the design team for the new dashboard mockups. Can you follow up with them today?"),
    ("en-US-JennyNeural", "Yes, I will email Sarah from design right after this call. What is the budget approval status for the new tooling?"),
    ("en-US-GuyNeural",   "Still pending. I have escalated it to management. We should have an answer by end of week. That remains unresolved for now."),
    ("en-US-JennyNeural", "Okay, let us wrap up. To summarize: REST APIs, phased database migration, David handles migration scripts by Monday, I review pull requests by Thursday and follow up with design today."),
    ("en-US-GuyNeural",   "Perfect. Same time next week everyone. Thanks!"),
]

OUTPUT_WAV = "../test_meeting_audio.wav"
OUTPUT_MP4 = "../test_meeting.mp4"
WAV_RATE = 16000
WAV_CHANNELS = 1
WAV_SAMPWIDTH = 2  # 16-bit


async def chunk_to_pcm(voice: str, text: str, ffmpeg: str) -> bytes:
    """Generate speech via edge-tts, pipe MP3 through FFmpeg to get raw PCM16 bytes."""
    import edge_tts
    # Step 1: collect MP3 bytes
    mp3_bytes = []
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_bytes.append(chunk["data"])
    mp3_data = b"".join(mp3_bytes)

    # Step 2: convert MP3 → raw PCM via FFmpeg pipe
    result = subprocess.run(
        [ffmpeg, "-y", "-i", "pipe:0",
         "-ac", str(WAV_CHANNELS), "-ar", str(WAV_RATE),
         "-acodec", "pcm_s16le", "-f", "s16le", "pipe:1"],
        input=mp3_data, capture_output=True, timeout=60
    )
    if result.returncode != 0:
        print(f"    FFmpeg MP3→PCM error: {result.stderr.decode()[-200:]}")
        return b""
    return result.stdout


def write_wav(filename: str, pcm_frames: bytes):
    """Write PCM frames as a proper WAV file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(WAV_CHANNELS)
        wf.setsampwidth(WAV_SAMPWIDTH)
        wf.setframerate(WAV_RATE)
        wf.writeframes(pcm_frames)
    dur = len(pcm_frames) / (WAV_RATE * WAV_CHANNELS * WAV_SAMPWIDTH)
    print(f"  Written: {filename} ({dur:.1f}s)")


def create_mp4(wav_file: str, ffmpeg: str) -> bool:
    """Wrap WAV in an MP4 with a black video track."""
    result = subprocess.run(
        [ffmpeg, "-y",
         "-f", "lavfi", "-i", "color=c=black:size=640x360:rate=25",
         "-i", wav_file,
         "-shortest",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "35",
         "-c:a", "aac", OUTPUT_MP4],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        print("FFmpeg MP4 error:", result.stderr[-400:])
        return False
    size_kb = os.path.getsize(OUTPUT_MP4) // 1024
    print(f"  Created: {OUTPUT_MP4} ({size_kb} KB)")
    return True


async def main():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ERROR: FFmpeg not on PATH.")
        sys.exit(1)
    print(f"[1] FFmpeg: {ffmpeg}")

    print(f"[2] Generating {len(MEETING_SCRIPT)} speech chunks...")
    all_pcm = b""
    for i, (voice, text) in enumerate(MEETING_SCRIPT):
        print(f"  [{i+1}/{len(MEETING_SCRIPT)}] {voice}...")
        pcm = await chunk_to_pcm(voice, text, ffmpeg)
        all_pcm += pcm
        # Add 0.5s of silence between speakers
        silence = b"\x00" * (WAV_RATE * WAV_CHANNELS * WAV_SAMPWIDTH // 2)
        all_pcm += silence

    print(f"[3] Writing WAV ({len(all_pcm)//1024} KB of PCM)...")
    write_wav(OUTPUT_WAV, all_pcm)

    print(f"[4] Creating MP4...")
    if not create_mp4(OUTPUT_WAV, ffmpeg):
        sys.exit(1)

    print(f"\nDone! Use '{OUTPUT_MP4}' to test the MeetAI upload pipeline.")


if __name__ == "__main__":
    asyncio.run(main())
