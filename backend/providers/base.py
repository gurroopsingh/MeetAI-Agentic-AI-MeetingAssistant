"""
Provider Interfaces — Abstract base classes for all AI providers.
These interfaces ensure the frontend and business logic remain decoupled
from any specific AI service (Azure, OpenAI, local, mock, etc.)

Future implementations:
- AzureSpeechProvider(SpeechProvider)
- AzureLanguageProvider(LanguageProvider)
- MicrosoftFoundryProvider(GenAIProvider)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class SpeechProvider(ABC):
    """Abstract interface for speech/audio services."""

    @abstractmethod
    async def extract_audio(self, video_path: str) -> str:
        """Extract audio from a video file. Returns path to audio file."""
        ...

    @abstractmethod
    async def transcribe(self, audio_path: str) -> List[Dict]:
        """
        Transcribe audio to text with speaker diarization.
        Returns list of segments: [{speaker, text, start_time, end_time, confidence}]
        """
        ...

    @abstractmethod
    async def identify_speakers(self, audio_path: str) -> List[Dict]:
        """
        Identify and profile speakers.
        Returns: [{name, speaking_time, word_count}]
        """
        ...


class LanguageProvider(ABC):
    """Abstract interface for text/language analysis services."""

    @abstractmethod
    async def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases/topics from text."""
        ...

    @abstractmethod
    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment. Returns {sentiment, confidence, scores}."""
        ...

    @abstractmethod
    async def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities. Returns [{text, category, confidence}]."""
        ...

    @abstractmethod
    async def classify_meeting_type(self, text: str) -> str:
        """Classify the type of meeting (planning, standup, design, etc.)."""
        ...


class GenAIProvider(ABC):
    """Abstract interface for generative AI services."""

    @abstractmethod
    async def summarize(self, text: str, context: Optional[Dict] = None) -> str:
        """Generate a concise meeting summary."""
        ...

    @abstractmethod
    async def extract_decisions(self, text: str) -> List[Dict]:
        """Extract decisions made during the meeting."""
        ...

    @abstractmethod
    async def extract_action_items(self, text: str) -> List[Dict]:
        """Extract action items/tasks with assignees and deadlines."""
        ...

    @abstractmethod
    async def extract_unresolved_questions(self, text: str) -> List[Dict]:
        """Extract questions that were raised but not answered."""
        ...

    @abstractmethod
    async def generate_chapters(self, segments: List[Dict]) -> List[Dict]:
        """Generate meeting chapters/segments with titles."""
        ...

    @abstractmethod
    async def answer_question(self, question: str, context: str, segments: List[Dict]) -> Dict:
        """Answer a question about the meeting. Returns {answer, sources}."""
        ...

    @abstractmethod
    async def generate_catch_up(self, segments: List[Dict], from_timestamp: Optional[float]) -> Dict:
        """Generate a catch-me-up summary for someone who joined late."""
        ...

    @abstractmethod
    async def generate_follow_up_email(self, meeting_data: Dict) -> Dict:
        """Generate a follow-up email draft. Returns {subject, body}."""
        ...


class MeetingAnalysisProvider(ABC):
    """Orchestration interface combining all AI analysis for a meeting."""

    @abstractmethod
    async def analyze(self, transcript_segments: List[Dict], metadata: Dict) -> Dict:
        """
        Full meeting analysis pipeline.
        Returns complete analysis including summary, topics, decisions, etc.
        """
        ...
