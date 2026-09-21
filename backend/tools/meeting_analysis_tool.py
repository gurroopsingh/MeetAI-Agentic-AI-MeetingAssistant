"""
Meeting Analysis Tool — Orchestrates language + GenAI providers for deep meeting analysis.
MCP-ready: this tool can be exposed as an MCP tool in the future.
"""
from typing import List, Dict, Optional
from providers.base import LanguageProvider, GenAIProvider


class MeetingAnalysisTool:
    """
    Tool for comprehensive meeting content analysis.
    Combines LanguageProvider (NLP) + GenAIProvider (generation).
    """

    def __init__(self, language_provider: LanguageProvider, genai_provider: GenAIProvider):
        self.language = language_provider
        self.genai = genai_provider

    async def summarize(self, transcript_text: str) -> str:
        """Generate a concise meeting summary."""
        return await self.genai.summarize(transcript_text)

    async def extract_topics(self, transcript_text: str) -> List[str]:
        """Extract key topics discussed in the meeting."""
        return await self.language.extract_key_phrases(transcript_text)

    async def extract_decisions(self, transcript_text: str) -> List[Dict]:
        """Extract decisions made during the meeting."""
        return await self.genai.extract_decisions(transcript_text)

    async def extract_action_items(self, transcript_text: str) -> List[Dict]:
        """Extract action items with assignees and deadlines."""
        return await self.genai.extract_action_items(transcript_text)

    async def extract_unresolved_questions(self, transcript_text: str) -> List[Dict]:
        """Extract questions that remained unanswered."""
        return await self.genai.extract_unresolved_questions(transcript_text)

    async def generate_chapters(self, segments: List[Dict]) -> List[Dict]:
        """Generate meeting chapters/timeline segments."""
        return await self.genai.generate_chapters(segments)

    async def analyze_sentiment(self, transcript_text: str) -> Dict:
        """Analyze overall meeting sentiment."""
        return await self.language.analyze_sentiment(transcript_text)

    async def classify_meeting(self, transcript_text: str) -> str:
        """Classify the meeting type."""
        return await self.language.classify_meeting_type(transcript_text)
