"""
Azure Speech Provider — REST API implementation (no SDK, avoids Windows threading issues).

Uses Azure Speech Services Fast Transcription API:
  POST {SPEECH_ENDPOINT}/speechtotext/transcriptions:transcribe?api-version=2025-10-15
  
Audio extracted via FFmpeg (16kHz mono WAV).
"""
import os
import asyncio
import subprocess
import logging
import json
import re
import requests as req_lib

from typing import List, Dict, Optional
from providers.base import SpeechProvider

logger = logging.getLogger(__name__)


def _check_ffmpeg() -> bool:
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _enrich_speakers_with_names(segments: List[Dict]) -> None:
    """
    Detect explicit self-introductions in the transcript (e.g., 'I am Eric Johnson')
    and map the diarized speaker ID to the stated name.
    """
    speaker_names = {}
    pattern = re.compile(
        r"(?i:hi|hello|hey)?[\s,]*"
        r"(?i:i'm|i am|this is|my name is)\s+"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
    )
    for seg in segments:
        speaker_id = seg.get("speaker")
        text = seg.get("text", "")
        if speaker_id and speaker_id not in speaker_names:
            match = pattern.search(text)
            if match:
                speaker_names[speaker_id] = match.group(1)
                logger.info(f"Explicitly mapped {speaker_id} to {speaker_names[speaker_id]}")
    
    # Apply the names back to all segments
    for seg in segments:
        speaker_id = seg.get("speaker")
        if speaker_id in speaker_names:
            seg["speaker"] = speaker_names[speaker_id]


class AzureSpeechProvider(SpeechProvider):
    """
    Azure AI Speech provider using the Fast Transcription REST API.
    """

    def __init__(self):
        self.api_key = os.getenv("SPEECH_API_KEY")
        self.endpoint = os.getenv("SPEECH_ENDPOINT", "")
        self.language = os.getenv("SPEECH_LANGUAGE", "en-US")

        if not self.api_key:
            raise ValueError("SPEECH_API_KEY is not set.")
        if not self.endpoint:
            raise ValueError("SPEECH_ENDPOINT is not set.")
        logger.info("AzureSpeechProvider (Fast Transcription) initialized.")

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
        """Transcribe audio via Azure Speech Fast Transcription API with diarization."""
        if not audio_path or not os.path.exists(audio_path):
            logger.warning("Audio file not found: %s", audio_path)
            return []

        logger.info("Transcribing via Azure Fast Transcription API: %s", audio_path)

        def run_transcription():
            base_url = self.endpoint.rstrip("/")
            url = f"{base_url}/speechtotext/transcriptions:transcribe?api-version=2025-10-15"
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Accept": "application/json",
            }
            properties = {
                "locales": [self.language],
                "diarization": {
                    "enabled": True,
                    "maxSpeakers": 8
                }
            }

            try:
                with open(audio_path, "rb") as f:
                    files = {
                        "definition": (None, json.dumps(properties), "application/json"),
                        "audio": ("audio.wav", f, "audio/wav")
                    }
                    response = req_lib.post(url, headers=headers, files=files, timeout=300)

                if response.status_code != 200:
                    logger.error("Azure Fast Transcription error %d: %s", response.status_code, response.text[:500])
                    return []

                result = response.json()
                segments = []
                phrases = result.get("phrases", [])
                
                for phrase in phrases:
                    speaker_num = phrase.get("speaker")
                    speaker_str = f"Speaker {speaker_num}" if speaker_num else None
                    
                    start_time = phrase.get("offsetMilliseconds", 0) / 1000.0
                    end_time = start_time + (phrase.get("durationMilliseconds", 0) / 1000.0)
                    
                    segments.append({
                        "text": phrase.get("text", "").strip(),
                        "start_time": round(start_time, 3),
                        "end_time": round(end_time, 3),
                        "speaker": speaker_str,
                        "confidence": phrase.get("confidence", 1.0)
                    })

                # Safe speaker-name enrichment
                _enrich_speakers_with_names(segments)
                
                return segments
            except Exception as e:
                logger.error("Fast transcription request failed: %s", str(e))
                raise

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
