"""
Azure Speech Provider — REST API implementation (no SDK, avoids Windows threading issues).

Uses Azure Speech Services REST API for batch/continuous transcription:
  POST https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1
  
Audio extracted via FFmpeg (16kHz mono WAV). Each WAV chunk is sent to the REST API.
"""
import os
import asyncio
import subprocess
import logging
import struct
import wave
import requests as req_lib

from typing import List, Dict, Optional
from providers.base import SpeechProvider

logger = logging.getLogger(__name__)

# Max audio chunk for REST API (< 60s or < 25MB per request)
CHUNK_DURATION_SEC = 55  # Send in 55-second chunks


def _check_ffmpeg() -> bool:
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _get_wav_duration(wav_path: str) -> float:
    """Get duration of a WAV file in seconds."""
    try:
        with wave.open(wav_path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception:
        return 0.0


def _split_wav(wav_path: str, chunk_dur_sec: int) -> List[str]:
    """Split a WAV file into chunks using FFmpeg."""
    chunks = []
    total_dur = _get_wav_duration(wav_path)
    if total_dur <= 0:
        return [wav_path]

    n_chunks = max(1, int(total_dur / chunk_dur_sec) + (1 if total_dur % chunk_dur_sec else 0))
    if n_chunks == 1:
        return [wav_path]

    base = wav_path.rsplit(".", 1)[0]
    for i in range(n_chunks):
        start = i * chunk_dur_sec
        chunk_path = f"{base}_chunk{i:03d}.wav"
        cmd = [
            "ffmpeg", "-y",
            "-i", wav_path,
            "-ss", str(start),
            "-t", str(chunk_dur_sec),
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            chunk_path,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        if result.returncode == 0 and os.path.exists(chunk_path):
            chunks.append((chunk_path, start))

    return chunks  # List of (path, offset_seconds)


def _transcribe_chunk_rest(wav_path: str, api_key: str, region: str, language: str = "en-US") -> List[Dict]:
    """
    Send a WAV chunk to Azure Speech REST API.
    Returns list of {text, start_time, end_time, speaker, confidence} segments.
    """
    url = (
        f"https://{region}.stt.speech.microsoft.com/speech/recognition/"
        f"conversation/cognitiveservices/v1"
        f"?language={language}&format=detailed"
    )
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json",
    }
    with open(wav_path, "rb") as f:
        data = f.read()

    response = req_lib.post(url, headers=headers, data=data, timeout=120)

    if response.status_code != 200:
        logger.error("Azure Speech REST error %d: %s", response.status_code, response.text[:300])
        return []

    result = response.json()
    status = result.get("RecognitionStatus", "")
    if status == "NoMatch" or status == "InitialSilenceTimeout":
        logger.info("No speech recognized in this chunk (status=%s).", status)
        return []

    if status != "Success":
        logger.warning("Non-success recognition status: %s", status)

    display_text = result.get("DisplayText", "").strip()
    if not display_text:
        return []

    # Detailed N-best results with timing
    n_best = result.get("NBest", [])
    if n_best:
        best = n_best[0]
        words = best.get("Words", [])
        confidence = best.get("Confidence", None)

        if words:
            # Group words into segments by silence gaps (>1s gaps)
            segments = []
            current_words = []
            current_start = None

            for word in words:
                # Word timing in 100-nanosecond units
                w_offset = word.get("Offset", 0) / 10_000_000.0
                w_dur = word.get("Duration", 0) / 10_000_000.0
                w_text = word.get("Word", "")

                if current_start is None:
                    current_start = w_offset

                current_words.append((w_text, w_offset, w_offset + w_dur))

                # Check for a gap > 1.5s to start a new segment
                if len(current_words) > 1:
                    prev_end = current_words[-2][2]
                    if w_offset - prev_end > 1.5 and len(current_words) > 5:
                        seg_text = " ".join(w[0] for w in current_words[:-1])
                        seg_start = current_words[0][1]
                        seg_end = current_words[-2][2]
                        segments.append({
                            "text": seg_text,
                            "start_time": round(seg_start, 3),
                            "end_time": round(seg_end, 3),
                            "speaker": None,
                            "confidence": round(confidence, 3) if confidence else None,
                        })
                        current_words = [current_words[-1]]
                        current_start = w_offset

            # Flush remaining words
            if current_words:
                seg_text = " ".join(w[0] for w in current_words)
                seg_start = current_words[0][1]
                seg_end = current_words[-1][2]
                segments.append({
                    "text": seg_text,
                    "start_time": round(seg_start, 3),
                    "end_time": round(seg_end, 3),
                    "speaker": None,
                    "confidence": round(confidence, 3) if confidence else None,
                })
            return segments

    # Fallback: single segment with the whole recognised text
    # Use the overall offset from RecognitionResult if available
    offset_raw = result.get("Offset", 0)
    duration_raw = result.get("Duration", 0)
    start_sec = offset_raw / 10_000_000.0
    end_sec = start_sec + (duration_raw / 10_000_000.0)
    return [{
        "text": display_text,
        "start_time": round(start_sec, 3),
        "end_time": round(max(end_sec, start_sec + 1.0), 3),
        "speaker": None,
        "confidence": None,
    }]


class AzureSpeechProvider(SpeechProvider):
    """
    Azure AI Speech provider using the REST API.
    Works reliably on Windows without SDK threading issues.
    """

    def __init__(self):
        self.api_key = os.getenv("SPEECH_API_KEY")
        self.endpoint = os.getenv("SPEECH_ENDPOINT", "")
        self.region = self._extract_region(self.endpoint)
        self.language = os.getenv("SPEECH_LANGUAGE", "en-US")

        if not self.api_key:
            raise ValueError("SPEECH_API_KEY is not set.")
        if not self.region:
            raise ValueError(f"Cannot determine Speech region from SPEECH_ENDPOINT: {self.endpoint}")
        logger.info("AzureSpeechProvider (REST) — Region: %s", self.region)

    def _extract_region(self, endpoint: str) -> Optional[str]:
        if not endpoint:
            return None
        # https://koreacentral.api.cognitive.microsoft.com/ → koreacentral
        host = endpoint.replace("https://", "").replace("http://", "").split("/")[0]
        parts = host.split(".")
        return parts[0] if parts else None

    async def extract_audio(self, video_path: str) -> str:
        """Extract 16kHz mono WAV from video using FFmpeg."""
        if not video_path or not os.path.exists(video_path):
            logger.warning("Video file not found: %s", video_path)
            return video_path or ""

        audio_path = video_path.rsplit(".", 1)[0] + "_audio.wav"

        if not _check_ffmpeg():
            logger.warning("FFmpeg not available — returning original path.")
            return video_path

        def run():
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-ac", "1",
                "-ar", "16000",
                "-acodec", "pcm_s16le",
                audio_path,
            ]
            return subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        try:
            result = await asyncio.to_thread(run)
            if result.returncode == 0 and os.path.exists(audio_path):
                logger.info("Audio extracted: %s", audio_path)
                return audio_path
            else:
                logger.error("FFmpeg error (rc=%d): %s", result.returncode, result.stderr[:500])
                return video_path
        except Exception as e:
            logger.error("FFmpeg exception: %s", str(e))
            return video_path

    async def transcribe(self, audio_path: str) -> List[Dict]:
        """Transcribe audio via Azure Speech REST, splitting into chunks if needed."""
        if not audio_path or not os.path.exists(audio_path):
            logger.warning("Audio file not found: %s", audio_path)
            return []

        logger.info("Transcribing via Azure Speech REST: %s", audio_path)

        def run_transcription():
            duration = _get_wav_duration(audio_path)
            logger.info("Audio duration: %.1f seconds", duration)

            if duration <= 0:
                logger.warning("Could not determine audio duration.")
                # Attempt transcription anyway
                return _transcribe_chunk_rest(audio_path, self.api_key, self.region, self.language)

            if duration <= CHUNK_DURATION_SEC:
                # Single request
                segments = _transcribe_chunk_rest(audio_path, self.api_key, self.region, self.language)
                return segments
            else:
                # Split into chunks
                logger.info("Audio > %ds, splitting into chunks.", CHUNK_DURATION_SEC)
                chunk_info = _split_wav(audio_path, CHUNK_DURATION_SEC)
                all_segments = []

                for item in chunk_info:
                    if isinstance(item, tuple):
                        chunk_path, offset = item
                    else:
                        chunk_path, offset = item, 0.0

                    if not os.path.exists(chunk_path):
                        continue

                    segs = _transcribe_chunk_rest(chunk_path, self.api_key, self.region, self.language)
                    # Add offset to all timestamps
                    for seg in segs:
                        seg["start_time"] = round(seg["start_time"] + offset, 3)
                        seg["end_time"] = round(seg["end_time"] + offset, 3)
                    all_segments.extend(segs)

                    # Cleanup chunk file
                    try:
                        os.remove(chunk_path)
                    except Exception:
                        pass

                return all_segments

        try:
            segments = await asyncio.to_thread(run_transcription)
            logger.info("Transcription complete: %d segments.", len(segments))
            return segments
        except Exception as e:
            logger.error("Azure Speech REST transcription failed: %s", str(e))
            raise

    async def identify_speakers(self, audio_path: str) -> List[Dict]:
        """Speaker profiles built from segments by the agent. Return empty here."""
        return []
