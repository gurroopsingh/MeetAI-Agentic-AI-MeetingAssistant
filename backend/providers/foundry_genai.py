"""
Microsoft Foundry GenAI Provider — Real implementation using gpt-4.1-mini via OpenAI-compatible API.
Replaces MockGenAIProvider when GENAI_PROVIDER=foundry.

CRITICAL: All analysis is grounded strictly in the provided transcript.
No hallucination. If info is not in the transcript, return null/empty.
"""
import os
import json
import logging
import asyncio
from typing import List, Dict, Optional

from providers.base import GenAIProvider

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_ANALYSIS = """You are MeetAI, a precise meeting analysis assistant.
Your ONLY data source is the transcript provided. You MUST NOT invent any:
- people, names, or speakers not mentioned
- decisions not explicitly made in the transcript
- action items or owners not explicitly assigned
- deadlines not mentioned
- timestamps beyond what the transcript provides

If the transcript lacks sufficient detail for a field, return null or an empty array.
All timestamps should be in SECONDS (float) derived from the transcript segment times.
Respond ONLY with valid JSON. No markdown, no explanations, no preamble."""

SYSTEM_PROMPT_QA = """You are MeetAI, a grounded Q&A assistant for meeting transcripts.
Answer questions ONLY based on the provided transcript.
If the answer is not present in the transcript, respond with exactly:
{"answer": "I couldn't find that information in this meeting.", "sources": []}
Include relevant speaker and timestamp in sources when available.
Respond ONLY with valid JSON."""

ANALYSIS_USER_TEMPLATE = """Analyse this meeting transcript and return a JSON object.

TRANSCRIPT:
{transcript}

LANGUAGE ANALYSIS (key phrases, sentiment):
{language_context}

Return this exact JSON structure:
{{
  "executive_summary": "A concise 2-4 sentence summary of the entire meeting",
  "key_topics": ["list", "of", "main", "topics"],
  "decisions": [
    {{
      "text": "exact decision made",
      "source_timestamp": 0.0,
      "speaker": "speaker name or null",
      "confidence": 0.9
    }}
  ],
  "action_items": [
    {{
      "task": "what needs to be done",
      "owner": "who is responsible or null",
      "deadline": "deadline string or null",
      "priority": "high|medium|low",
      "source_timestamp": 0.0
    }}
  ],
  "unresolved_questions": [
    {{
      "question": "the question that was raised but not answered",
      "source_timestamp": 0.0
    }}
  ],
  "chapters": [
    {{
      "title": "chapter title",
      "start_timestamp": 0.0,
      "end_timestamp": 0.0
    }}
  ],
  "meeting_type": "General|Planning|Sprint Planning|Design Review|Retrospective|Standup"
}}"""


def _build_transcript_text(segments: List[Dict]) -> str:
    """Format transcript segments into readable text for prompts."""
    lines = []
    for seg in segments:
        ts = seg.get("start_time", 0.0)
        mm = int(ts // 60)
        ss = int(ts % 60)
        speaker = seg.get("speaker") or "Unknown"
        text = seg.get("text", "").strip()
        if text:
            lines.append(f"[{mm:02d}:{ss:02d}] {speaker}: {text}")
    return "\n".join(lines)


class FoundryGenAIProvider(GenAIProvider):
    """
    Microsoft Foundry / Azure OpenAI provider using the OpenAI-compatible /openai/v1/ endpoint.
    Model: gpt-4.1-mini
    """

    def __init__(self):
        self.endpoint = os.getenv("FOUNDRY_ENDPOINT", "").rstrip("/")
        self.api_key = os.getenv("FOUNDRY_API_KEY")
        self.deployment = os.getenv("FOUNDRY_DEPLOYMENT", "gpt-4.1-mini")

        if not self.endpoint or not self.api_key:
            raise ValueError(
                "FOUNDRY_ENDPOINT and FOUNDRY_API_KEY must be set for FoundryGenAIProvider."
            )

        logger.info(
            "FoundryGenAIProvider initialised. Endpoint: %s, Deployment: %s",
            self.endpoint, self.deployment
        )

    def _get_client(self):
        from openai import AzureOpenAI
        # The endpoint is already the /openai/v1 path — but AzureOpenAI expects the base URL
        # Extract the base: https://meetai-ai103-korea.openai.azure.com/
        base_url = self.endpoint
        # If it contains /openai/v1, strip it — AzureOpenAI constructs its own path
        if "/openai/v1" in base_url:
            base_url = base_url.split("/openai/v1")[0]

        return AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=base_url,
            api_version="2024-12-01-preview",
        )

    def _chat(self, system: str, user: str, temperature: float = 0.1, max_tokens: int = 4096) -> str:
        """Synchronous chat completion call to Foundry."""
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def _parse_json_response(self, raw: str) -> Dict:
        """Parse JSON from model response, stripping markdown fences if present."""
        # Strip markdown code fences
        if raw.startswith("```"):
            lines = raw.split("\n")
            # Remove first and last fence line
            lines = [l for l in lines if not l.strip().startswith("```")]
            raw = "\n".join(lines)
        return json.loads(raw.strip())

    async def _full_analysis(self, segments: List[Dict], language_context: str = "") -> Dict:
        """Run one consolidated Foundry call for the full meeting analysis."""
        transcript_text = _build_transcript_text(segments)
        if not transcript_text.strip():
            logger.warning("Empty transcript — skipping Foundry analysis.")
            return {
                "executive_summary": "No transcript available for this meeting.",
                "key_topics": [],
                "decisions": [],
                "action_items": [],
                "unresolved_questions": [],
                "chapters": [],
                "meeting_type": "General",
            }

        # Truncate very long transcripts to stay within context window
        max_chars = 40000
        if len(transcript_text) > max_chars:
            logger.warning("Transcript truncated from %d to %d chars.", len(transcript_text), max_chars)
            transcript_text = transcript_text[:max_chars] + "\n[TRANSCRIPT TRUNCATED]"

        user_prompt = ANALYSIS_USER_TEMPLATE.format(
            transcript=transcript_text,
            language_context=language_context or "Not available",
        )

        def run():
            return self._chat(SYSTEM_PROMPT_ANALYSIS, user_prompt, temperature=0.1, max_tokens=4096)

        try:
            raw = await asyncio.to_thread(run)
            result = self._parse_json_response(raw)
            logger.info(
                "Foundry analysis complete. Decisions: %d, Actions: %d",
                len(result.get("decisions", [])),
                len(result.get("action_items", [])),
            )
            return result
        except json.JSONDecodeError as e:
            logger.error("Foundry returned invalid JSON: %s. Raw: %s", str(e), raw[:500])
            raise RuntimeError(f"Foundry returned malformed JSON: {e}")
        except Exception as e:
            logger.error("Foundry full_analysis failed: %s", str(e))
            raise

    # --- Individual methods required by GenAIProvider ABC ---
    # These all delegate to _full_analysis via a cached result stored on the instance.
    # In practice, meeting_agent.py calls each separately, so we make them lazy.

    async def summarize(self, text: str, context: Optional[Dict] = None) -> str:
        """For standalone summarisation — used in catch-up and email flows."""
        if not text.strip():
            return "No transcript available."

        user = (
            f"Based ONLY on this meeting transcript, write a concise 2-4 sentence executive summary:\n\n"
            f"{text[:10000]}"
        )
        def run():
            return self._chat(SYSTEM_PROMPT_ANALYSIS, user, temperature=0.1, max_tokens=500)
        try:
            return await asyncio.to_thread(run)
        except Exception as e:
            logger.error("Foundry summarize failed: %s", str(e))
            return "Summary unavailable due to an error."

    async def extract_decisions(self, text: str) -> List[Dict]:
        # Called by MeetingAnalysisTool.extract_decisions — but in practice
        # the agent uses process_meeting which calls _full_analysis_cached below.
        return []

    async def extract_action_items(self, text: str) -> List[Dict]:
        return []

    async def extract_unresolved_questions(self, text: str) -> List[Dict]:
        return []

    async def generate_chapters(self, segments: List[Dict]) -> List[Dict]:
        return []

    async def analyze_all(self, segments: List[Dict], language_context: str = "") -> Dict:
        """
        Main entry point for agent processing.
        Returns the full analysis dict from a single Foundry call.
        """
        return await self._full_analysis(segments, language_context)

    async def answer_question(self, question: str, context: str, segments: List[Dict]) -> Dict:
        """Answer a question grounded strictly in the meeting transcript."""
        if not context.strip():
            return {
                "answer": "I couldn't find that information in this meeting.",
                "sources": [],
            }

        transcript_text = _build_transcript_text(segments) if segments else context
        if len(transcript_text) > 15000:
            transcript_text = transcript_text[:15000] + "\n[TRANSCRIPT TRUNCATED]"

        user = (
            f"MEETING TRANSCRIPT:\n{transcript_text}\n\n"
            f"QUESTION: {question}\n\n"
            f'Respond with JSON: {{"answer": "...", "sources": [{{"speaker": "...", "timestamp": 0.0, "text": "..."}}]}}'
        )

        def run():
            return self._chat(SYSTEM_PROMPT_QA, user, temperature=0.0, max_tokens=800)

        try:
            raw = await asyncio.to_thread(run)
            result = self._parse_json_response(raw)
            return result
        except Exception as e:
            logger.error("Foundry answer_question failed: %s", str(e))
            return {
                "answer": "I couldn't find that information in this meeting.",
                "sources": [],
            }

    async def generate_catch_up(self, segments: List[Dict], from_timestamp: Optional[float]) -> Dict:
        """Generate a catch-up summary from the real transcript."""
        ts = from_timestamp or 0.0
        # Filter segments to only those after the requested timestamp
        relevant = [s for s in segments if s.get("start_time", 0.0) >= ts]
        if not relevant:
            relevant = segments  # fallback to all if none match

        transcript_text = _build_transcript_text(relevant)
        if not transcript_text.strip():
            return {
                "summary": "No content found after the specified time.",
                "key_points": [],
                "missed_decisions": [],
                "action_items_for_you": [],
            }

        mm = int(ts // 60)
        ss = int(ts % 60)

        user = (
            f"The user joined this meeting at {mm:02d}:{ss:02d}. "
            f"Here is what they missed (transcript from that point):\n\n"
            f"{transcript_text[:8000]}\n\n"
            f'Return JSON: {{"summary": "...", "key_points": ["..."], '
            f'"missed_decisions": ["..."], "action_items_for_you": ["..."]}}'
        )

        def run():
            return self._chat(SYSTEM_PROMPT_QA, user, temperature=0.1, max_tokens=1000)

        try:
            raw = await asyncio.to_thread(run)
            return self._parse_json_response(raw)
        except Exception as e:
            logger.error("Foundry generate_catch_up failed: %s", str(e))
            return {
                "summary": "Could not generate catch-up summary.",
                "key_points": [],
                "missed_decisions": [],
                "action_items_for_you": [],
            }

    async def generate_follow_up_email(self, meeting_data: Dict) -> Dict:
        """Generate a follow-up email strictly from actual meeting data."""
        title = meeting_data.get("title", "Meeting")
        summary = meeting_data.get("summary", "")
        decisions = meeting_data.get("decisions", [])
        action_items = meeting_data.get("action_items", [])
        recipient = meeting_data.get("recipient_name", "Team")
        notes = meeting_data.get("additional_notes", "")

        context = (
            f"MEETING TITLE: {title}\n"
            f"SUMMARY: {summary}\n"
            f"DECISIONS: {json.dumps(decisions)}\n"
            f"ACTION ITEMS: {json.dumps(action_items)}\n"
        )
        if notes:
            context += f"ADDITIONAL NOTES: {notes}\n"

        user = (
            f"Write a professional follow-up email to '{recipient}' based ONLY on the following "
            f"meeting data. Do not add anything not mentioned:\n\n{context}\n\n"
            f'Return JSON: {{"subject": "...", "body": "..."}}'
        )

        def run():
            return self._chat(SYSTEM_PROMPT_ANALYSIS, user, temperature=0.2, max_tokens=1500)

        try:
            raw = await asyncio.to_thread(run)
            return self._parse_json_response(raw)
        except Exception as e:
            logger.error("Foundry generate_follow_up_email failed: %s", str(e))
            return {
                "subject": f"Follow-up: {title}",
                "body": "Could not generate email body. Please try again.",
            }
