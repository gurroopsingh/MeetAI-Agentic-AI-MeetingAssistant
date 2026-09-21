"""
Speech Tool — Wraps the SpeechProvider for audio extraction and transcription.
MCP-ready: this tool can be exposed as an MCP tool in the future.
"""
from typing import List, Dict
from providers.base import SpeechProvider


class SpeechTool:
    """
    Tool for speech-to-text operations.
    Provider-agnostic — swap MockSpeechProvider for AzureSpeechProvider when ready.
    """

    def __init__(self, provider: SpeechProvider):
        self.provider = provider

    async def extract_audio(self, video_path: str) -> str:
        """Extract audio track from a video file."""
        return await self.provider.extract_audio(video_path)

    async def transcribe(self, audio_path: str) -> List[Dict]:
        """
        Transcribe audio to text segments with speaker diarization.
        Returns: List of {speaker, text, start_time, end_time, confidence}
        """
        return await self.provider.transcribe(audio_path)

    async def identify_speakers(self, audio_path: str) -> List[Dict]:
        """
        Profile all speakers in the audio.
        Returns: List of {name, speaking_time, word_count}
        """
        return await self.provider.identify_speakers(audio_path)
