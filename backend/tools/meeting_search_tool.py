"""
Meeting Search Tool — Provides full-text search across meetings, transcripts, tasks, decisions.
MCP-ready: this tool can be exposed as an MCP tool in the future.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models


class MeetingSearchTool:
    """
    Tool for searching meeting content, transcripts, and tasks.
    Works entirely from the database — no AI provider needed.
    """

    def search(self, db: Session, query: str, limit: int = 20) -> List[Dict]:
        """
        Full-text search across meetings, transcripts, tasks, and decisions.
        Returns list of SearchResult dicts.
        """
        results = []
        q = f"%{query.lower()}%"

        # Search meetings
        meetings = db.query(models.Meeting).filter(
            or_(
                models.Meeting.title.ilike(q),
                models.Meeting.description.ilike(q),
                models.Meeting.summary.ilike(q),
            )
        ).limit(5).all()

        for m in meetings:
            results.append({
                "type": "meeting",
                "id": m.id,
                "title": m.title,
                "excerpt": (m.summary or m.description or "")[:150],
                "meeting_id": m.id,
                "timestamp": None,
            })

        # Search transcript segments
        segments = db.query(models.TranscriptSegment).filter(
            models.TranscriptSegment.text.ilike(q)
        ).limit(8).all()

        for s in segments:
            results.append({
                "type": "transcript",
                "id": s.id,
                "title": f"{s.speaker_name or 'Unknown'} at {int(s.start_time // 60)}:{int(s.start_time % 60):02d}",
                "excerpt": s.text[:150],
                "meeting_id": s.meeting_id,
                "timestamp": s.start_time,
            })

        # Search decisions
        decisions = db.query(models.Decision).filter(
            models.Decision.text.ilike(q)
        ).limit(5).all()

        for d in decisions:
            results.append({
                "type": "decision",
                "id": d.id,
                "title": "Decision",
                "excerpt": d.text[:150],
                "meeting_id": d.meeting_id,
                "timestamp": d.timestamp,
            })

        # Search tasks
        tasks = db.query(models.Task).filter(
            or_(
                models.Task.title.ilike(q),
                models.Task.description.ilike(q),
            )
        ).limit(5).all()

        for t in tasks:
            results.append({
                "type": "task",
                "id": t.id,
                "title": t.title,
                "excerpt": f"Assigned to {t.assignee or 'Unassigned'} — {t.status}",
                "meeting_id": t.meeting_id,
                "timestamp": t.source_timestamp,
            })

        return results[:limit]
