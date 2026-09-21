"""
Azure AI Language Provider — Real implementation using azure-ai-textanalytics SDK.
Replaces MockLanguageProvider when LANGUAGE_PROVIDER=azure.

Handles: key phrase extraction, sentiment analysis, entity recognition.
"""
import os
import asyncio
import logging
from typing import List, Dict, Optional

from providers.base import LanguageProvider

logger = logging.getLogger(__name__)

MEETING_TYPE_KEYWORDS = {
    "standup": ["standup", "stand-up", "daily", "yesterday", "today", "blockers"],
    "sprint_planning": ["sprint", "backlog", "story points", "velocity", "iteration"],
    "design_review": ["design", "mockup", "wireframe", "prototype", "figma", "ux", "ui"],
    "retrospective": ["retrospective", "retro", "went well", "improve", "lessons learned"],
    "all_hands": ["all hands", "company update", "announcement", "org"],
    "planning": ["roadmap", "q1", "q2", "q3", "q4", "planning", "goals", "okr"],
}


class AzureLanguageProvider(LanguageProvider):
    """
    Real Azure AI Language provider.
    Uses azure-ai-textanalytics SDK.
    """

    def __init__(self):
        self.endpoint = os.getenv("LANGUAGE_ENDPOINT")
        self.api_key = os.getenv("LANGUAGE_API_KEY")

        if not self.endpoint or not self.api_key:
            raise ValueError(
                "LANGUAGE_ENDPOINT and LANGUAGE_API_KEY must be set for AzureLanguageProvider."
            )

        logger.info("AzureLanguageProvider initialised. Endpoint: %s", self.endpoint)

    def _get_client(self):
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential
        return TextAnalyticsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )

    def _chunk_text(self, text: str, max_chars: int = 5000) -> List[str]:
        """Split text into chunks within Azure's document size limit."""
        chunks = []
        while len(text) > max_chars:
            split_at = text.rfind(" ", 0, max_chars)
            if split_at == -1:
                split_at = max_chars
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip()
        if text:
            chunks.append(text)
        return chunks

    async def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text using Azure AI Language."""
        if not text.strip():
            return []

        def run():
            client = self._get_client()
            chunks = self._chunk_text(text)
            all_phrases = []
            for chunk in chunks:
                docs = [{"id": "1", "text": chunk, "language": "en"}]
                response = client.extract_key_phrases(documents=docs)
                for doc in response:
                    if not doc.is_error:
                        all_phrases.extend(doc.key_phrases)
                    else:
                        logger.warning("Key phrase extraction error: %s", doc.error)
            # Deduplicate while preserving order
            seen = set()
            unique = []
            for p in all_phrases:
                if p.lower() not in seen:
                    seen.add(p.lower())
                    unique.append(p)
            return unique[:20]  # Return top 20

        try:
            return await asyncio.to_thread(run)
        except Exception as e:
            logger.error("Azure Language extract_key_phrases failed: %s", str(e))
            return []

    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the transcript."""
        if not text.strip():
            return {"sentiment": "neutral", "confidence": 0.5, "scores": {}}

        def run():
            client = self._get_client()
            # Use first 5000 chars for overall sentiment
            snippet = text[:5000]
            docs = [{"id": "1", "text": snippet, "language": "en"}]
            response = client.analyze_sentiment(documents=docs)
            for doc in response:
                if not doc.is_error:
                    scores = {
                        "positive": round(doc.confidence_scores.positive, 3),
                        "neutral": round(doc.confidence_scores.neutral, 3),
                        "negative": round(doc.confidence_scores.negative, 3),
                    }
                    confidence = max(scores.values())
                    return {
                        "sentiment": doc.sentiment,
                        "confidence": confidence,
                        "scores": scores,
                    }
            return {"sentiment": "neutral", "confidence": 0.5, "scores": {}}

        try:
            return await asyncio.to_thread(run)
        except Exception as e:
            logger.error("Azure Language analyze_sentiment failed: %s", str(e))
            return {"sentiment": "neutral", "confidence": 0.5, "scores": {}}

    async def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from transcript."""
        if not text.strip():
            return []

        def run():
            client = self._get_client()
            snippet = text[:5000]
            docs = [{"id": "1", "text": snippet, "language": "en"}]
            response = client.recognize_entities(documents=docs)
            entities = []
            for doc in response:
                if not doc.is_error:
                    for entity in doc.entities:
                        entities.append({
                            "text": entity.text,
                            "category": entity.category,
                            "confidence": round(entity.confidence_score, 3),
                        })
            return entities

        try:
            return await asyncio.to_thread(run)
        except Exception as e:
            logger.error("Azure Language extract_entities failed: %s", str(e))
            return []

    async def classify_meeting_type(self, text: str) -> str:
        """Classify meeting type via keyword heuristics on the transcript."""
        text_lower = text.lower()
        scores = {}
        for mtype, keywords in MEETING_TYPE_KEYWORDS.items():
            scores[mtype] = sum(1 for kw in keywords if kw in text_lower)
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "General"
        return best.replace("_", " ").title()
