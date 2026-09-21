"""
Meeting Agent — Orchestration layer that coordinates all tools and providers.
This is the core AI agent that processes meetings end-to-end.

Provider selection is controlled by environment variables:
  AI_PROVIDER=azure  (or SPEECH_PROVIDER / LANGUAGE_PROVIDER / GENAI_PROVIDER individually)

Future: Deploy on Microsoft Foundry and orchestrate via MCP tools.
"""
import asyncio
import json
import logging
import os
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

import models
from providers.base import SpeechProvider, LanguageProvider, GenAIProvider

logger = logging.getLogger(__name__)


def _get_speech_provider() -> SpeechProvider:
    mode = os.getenv("SPEECH_PROVIDER") or os.getenv("AI_PROVIDER", "mock")
    if mode == "azure":
        from providers.azure_speech import AzureSpeechProvider
        return AzureSpeechProvider()
    else:
        from providers.mock import MockSpeechProvider
        return MockSpeechProvider()


def _get_language_provider() -> LanguageProvider:
    mode = os.getenv("LANGUAGE_PROVIDER") or os.getenv("AI_PROVIDER", "mock")
    if mode == "azure":
        from providers.azure_language import AzureLanguageProvider
        return AzureLanguageProvider()
    else:
        from providers.mock import MockLanguageProvider
        return MockLanguageProvider()


def _get_genai_provider() -> GenAIProvider:
    mode = os.getenv("GENAI_PROVIDER") or os.getenv("AI_PROVIDER", "mock")
    if mode in ("azure", "foundry"):
        from providers.foundry_genai import FoundryGenAIProvider
        return FoundryGenAIProvider()
    else:
        from providers.mock import MockGenAIProvider
        return MockGenAIProvider()


class MeetingAgent:
    """
    The main AI orchestration agent for MeetAI.

    Responsibilities:
    1. Coordinate speech transcription and speaker identification
    2. Run full meeting analysis (summary, topics, decisions, etc.)
    3. Answer questions about meetings (RAG-like)
    4. Generate catch-up summaries
    5. Generate follow-up emails
    """

    def __init__(self):
        self.speech = _get_speech_provider()
        self.language = _get_language_provider()
        self.genai = _get_genai_provider()
        logger.info(
            "MeetingAgent initialised. Speech: %s, Language: %s, GenAI: %s",
            type(self.speech).__name__,
            type(self.language).__name__,
            type(self.genai).__name__,
        )

    def _update_status(self, db: Session, meeting: models.Meeting, status: str):
        """Update meeting status in DB."""
        meeting.status = status
        db.commit()

    async def process_meeting(self, db: Session, meeting: models.Meeting) -> None:
        """
        Full meeting processing pipeline.
        Updates the meeting record in-place with analysis results.

        Stages:
          1. Extract audio (FFmpeg)
          2. Transcribe (Azure Speech / Mock)
          3. Azure Language analysis (key phrases, sentiment)
          4. Foundry / Mock comprehensive analysis
          5. Persist all results
        """
        try:
            # ── Stage 1: Extract audio ─────────────────────────────────────
            meeting.status = "extracting_audio"
            db.commit()
            logger.info("[Meeting %d] Extracting audio from: %s", meeting.id, meeting.file_path)
            audio_path = await self.speech.extract_audio(meeting.file_path or "")
            logger.info("[Meeting %d] Audio path: %s", meeting.id, audio_path)

            # ── Stage 2: Transcribe ───────────────────────────────────────
            meeting.status = "transcribing"
            db.commit()
            logger.info("[Meeting %d] Starting transcription…", meeting.id)
            transcript_segments = await self.speech.transcribe(audio_path)
            logger.info("[Meeting %d] Got %d transcript segments.", meeting.id, len(transcript_segments))

            if not transcript_segments:
                logger.warning("[Meeting %d] Empty transcript produced.", meeting.id)

            # ── Stage 3: Save transcript ──────────────────────────────────
            for seg in transcript_segments:
                db_seg = models.TranscriptSegment(
                    meeting_id=meeting.id,
                    speaker_name=seg.get("speaker"),
                    text=seg.get("text", ""),
                    start_time=seg.get("start_time", 0.0),
                    end_time=seg.get("end_time", 0.0),
                    confidence=seg.get("confidence") or 1.0,
                )
                db.add(db_seg)

            db.commit()

            # ── Stage 4: Build speaker profiles from transcript ───────────
            full_text = " ".join(s.get("text", "") for s in transcript_segments)
            speaker_stats: Dict[str, Dict] = {}
            colors = ["#6366f1", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b", "#3b82f6", "#ef4444"]
            for seg in transcript_segments:
                sp = seg.get("speaker") or "Unknown Speaker"
                dur = (seg.get("end_time", 0.0) - seg.get("start_time", 0.0))
                wc = len(seg.get("text", "").split())
                if sp not in speaker_stats:
                    speaker_stats[sp] = {"speaking_time": 0.0, "word_count": 0}
                speaker_stats[sp]["speaking_time"] += max(dur, 0.0)
                speaker_stats[sp]["word_count"] += wc

            for i, (name, stats) in enumerate(speaker_stats.items()):
                db.add(models.Speaker(
                    meeting_id=meeting.id,
                    name=name,
                    speaking_time=round(stats["speaking_time"], 2),
                    word_count=stats["word_count"],
                    avatar_color=colors[i % len(colors)],
                ))
            db.commit()

            # ── Stage 5: Azure Language analysis ─────────────────────────
            meeting.status = "analyzing"
            db.commit()

            key_phrases, sentiment_data = await asyncio.gather(
                self.language.extract_key_phrases(full_text),
                self.language.analyze_sentiment(full_text),
            )
            meeting_type = await self.language.classify_meeting_type(full_text)
            logger.info(
                "[Meeting %d] Language analysis done. Topics: %d, Sentiment: %s",
                meeting.id, len(key_phrases), sentiment_data.get("sentiment"),
            )

            language_context = (
                f"Key phrases: {', '.join(key_phrases[:10])}\n"
                f"Sentiment: {sentiment_data.get('sentiment', 'neutral')}"
            )

            # ── Stage 6: GenAI comprehensive analysis ─────────────────────
            meeting.status = "generating_insights"
            db.commit()

            # Check if provider supports the unified analyze_all method
            if hasattr(self.genai, "analyze_all"):
                analysis = await self.genai.analyze_all(transcript_segments, language_context)
            else:
                # Fallback: call each method individually (mock provider path)
                summary, decisions_data, actions_data, questions_data, chapters_data = await asyncio.gather(
                    self.genai.summarize(full_text),
                    self.genai.extract_decisions(full_text),
                    self.genai.extract_action_items(full_text),
                    self.genai.extract_unresolved_questions(full_text),
                    self.genai.generate_chapters(transcript_segments),
                )
                analysis = {
                    "executive_summary": summary,
                    "key_topics": key_phrases,
                    "decisions": decisions_data,
                    "action_items": actions_data,
                    "unresolved_questions": questions_data,
                    "chapters": chapters_data,
                    "meeting_type": meeting_type,
                }

            # ── Stage 7: Persist analysis results ────────────────────────
            meeting.summary = analysis.get("executive_summary") or analysis.get("summary", "")
            meeting.key_topics = json.dumps(
                analysis.get("key_topics") or key_phrases
            )
            meeting.sentiment = sentiment_data.get("sentiment", "neutral")
            meeting.meeting_type = analysis.get("meeting_type") or meeting_type

            # Duration from transcript
            if transcript_segments:
                meeting.duration = transcript_segments[-1].get("end_time", 0.0)

            # Decisions
            for d in (analysis.get("decisions") or []):
                db.add(models.Decision(
                    meeting_id=meeting.id,
                    text=d.get("text", ""),
                    timestamp=d.get("source_timestamp") or d.get("timestamp"),
                    speaker_name=d.get("speaker") or d.get("speaker_name"),
                    importance=self._map_confidence_to_importance(d.get("confidence")),
                ))

            # Action items
            for a in (analysis.get("action_items") or []):
                title = a.get("task") or a.get("title", "")
                assignee = a.get("owner") or a.get("assignee")
                deadline = a.get("deadline")
                priority = a.get("priority", "medium")
                timestamp = a.get("source_timestamp") or a.get("timestamp")

                db.add(models.ActionItem(
                    meeting_id=meeting.id,
                    title=title,
                    assignee=assignee,
                    deadline=deadline,
                    priority=priority,
                    timestamp=timestamp,
                    status="todo",
                ))
                db.add(models.Task(
                    title=title,
                    assignee=assignee,
                    deadline=deadline,
                    priority=priority,
                    meeting_id=meeting.id,
                    meeting_title=meeting.title,
                    source_timestamp=timestamp,
                    status="todo",
                ))

            # Unresolved questions
            for q in (analysis.get("unresolved_questions") or []):
                question_text = q.get("question") or q.get("text", "")
                db.add(models.UnresolvedQuestion(
                    meeting_id=meeting.id,
                    text=question_text,
                    asked_by=q.get("asked_by"),
                    timestamp=q.get("source_timestamp") or q.get("timestamp"),
                ))

            # Chapters
            for c in (analysis.get("chapters") or []):
                db.add(models.Chapter(
                    meeting_id=meeting.id,
                    title=c.get("title", ""),
                    start_time=c.get("start_timestamp") or c.get("start_time", 0.0),
                    end_time=c.get("end_timestamp") or c.get("end_time", 0.0),
                    summary=c.get("summary"),
                ))

            meeting.status = "ready"
            db.commit()
            logger.info("[Meeting %d] Processing complete. Status: ready", meeting.id)

        except Exception as e:
            logger.exception("[Meeting %d] Processing failed: %s", meeting.id, str(e))
            meeting.status = "failed"
            meeting.summary = f"Processing failed: {str(e)[:500]}"
            db.commit()
            raise

    def _map_confidence_to_importance(self, confidence) -> str:
        """Map a confidence float to importance level."""
        if confidence is None:
            return "medium"
        try:
            c = float(confidence)
            if c >= 0.8:
                return "high"
            if c >= 0.5:
                return "medium"
            return "low"
        except (TypeError, ValueError):
            return "medium"

    async def ask_question(self, db: Session, meeting_id: int, question: str) -> Dict:
        """Answer a question about a specific meeting using real transcript context."""
        segments = db.query(models.TranscriptSegment).filter(
            models.TranscriptSegment.meeting_id == meeting_id
        ).order_by(models.TranscriptSegment.start_time).all()

        segment_dicts = [
            {
                "speaker": s.speaker_name,
                "text": s.text,
                "start_time": s.start_time,
                "end_time": s.end_time,
            }
            for s in segments
        ]
        context = " ".join(s.text for s in segments)
        return await self.genai.answer_question(question, context, segment_dicts)

    async def generate_catch_up(
        self, db: Session, meeting_id: int, from_timestamp: Optional[float] = None
    ) -> Dict:
        """Generate a catch-me-up summary using real transcript."""
        segments = db.query(models.TranscriptSegment).filter(
            models.TranscriptSegment.meeting_id == meeting_id
        ).order_by(models.TranscriptSegment.start_time).all()

        segment_dicts = [
            {"speaker": s.speaker_name, "text": s.text, "start_time": s.start_time}
            for s in segments
        ]
        return await self.genai.generate_catch_up(segment_dicts, from_timestamp)

    async def generate_follow_up_email(
        self,
        db: Session,
        meeting_id: int,
        recipient_name: Optional[str] = None,
        additional_notes: Optional[str] = None,
    ) -> Dict:
        """Generate a follow-up email from real meeting data."""
        meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        decisions = db.query(models.Decision).filter(models.Decision.meeting_id == meeting_id).all()
        action_items = db.query(models.ActionItem).filter(models.ActionItem.meeting_id == meeting_id).all()

        meeting_data = {
            "title": meeting.title if meeting else "Meeting",
            "summary": meeting.summary if meeting else "",
            "decisions": [{"text": d.text, "speaker": d.speaker_name} for d in decisions],
            "action_items": [
                {"task": a.title, "owner": a.assignee, "deadline": a.deadline, "priority": a.priority}
                for a in action_items
            ],
        }
        if recipient_name:
            meeting_data["recipient_name"] = recipient_name
        if additional_notes:
            meeting_data["additional_notes"] = additional_notes

        return await self.genai.generate_follow_up_email(meeting_data)
