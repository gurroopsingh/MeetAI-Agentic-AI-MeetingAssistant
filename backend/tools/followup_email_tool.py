"""
Follow-up Email Tool — Generates follow-up email drafts from meeting analysis.
MCP-ready: this tool can be exposed as an MCP tool in the future.
"""
from typing import Optional
from providers.base import GenAIProvider


class FollowUpEmailTool:
    """Tool for generating professional follow-up emails from meeting data."""

    def __init__(self, genai_provider: GenAIProvider):
        self.genai = genai_provider

    async def generate(self, meeting_data: dict,
                       recipient_name: Optional[str] = None,
                       additional_notes: Optional[str] = None) -> dict:
        """
        Generate a follow-up email from meeting analysis data.
        Returns {subject, body}.
        """
        if recipient_name:
            meeting_data["recipient_name"] = recipient_name
        if additional_notes:
            meeting_data["additional_notes"] = additional_notes

        return await self.genai.generate_follow_up_email(meeting_data)
