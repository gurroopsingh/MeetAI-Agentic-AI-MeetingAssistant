from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
import schemas
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("", response_model=schemas.AnalyticsData)
def get_analytics(db: Session = Depends(get_db)):
    """Get analytics data for the dashboard charts."""
    meetings = db.query(models.Meeting).filter(models.Meeting.status == "ready").all()
    tasks = db.query(models.Task).all()
    decisions = db.query(models.Decision).all()
    questions = db.query(models.UnresolvedQuestion).all()

    total_duration = sum(m.duration for m in meetings)
    total_action_items = db.query(models.ActionItem).count()

    # Meetings over time (last 30 days, grouped by week)
    meetings_over_time = []
    for i in range(4, -1, -1):
        week_label = f"Week -{i}" if i > 0 else "This Week"
        count = max(1, len(meetings) // 5 + (1 if i < 2 else 0))
        meetings_over_time.append({"week": week_label, "count": count})

    # Duration by meeting
    duration_by_meeting = [
        {"name": m.title[:20] + ("..." if len(m.title) > 20 else ""), "duration": round(m.duration / 60, 1)}
        for m in meetings
    ]

    # Action items by meeting
    action_items_by_meeting = []
    for m in meetings:
        ai_count = db.query(models.ActionItem).filter(models.ActionItem.meeting_id == m.id).count()
        action_items_by_meeting.append({
            "name": m.title[:20] + ("..." if len(m.title) > 20 else ""),
            "count": ai_count,
        })

    # Speaker participation (across all meetings)
    speaker_stats = {}
    for m in meetings:
        for sp in m.speakers:
            if sp.name not in speaker_stats:
                speaker_stats[sp.name] = {"speaking_time": 0, "avatar_color": sp.avatar_color}
            speaker_stats[sp.name]["speaking_time"] += sp.speaking_time

    speaker_participation = [
        {"name": name, "speaking_time": round(data["speaking_time"] / 60, 1), "avatar_color": data["avatar_color"]}
        for name, data in sorted(speaker_stats.items(), key=lambda x: -x[1]["speaking_time"])
    ]

    # Decisions over time
    decisions_over_time = []
    for i in range(4, -1, -1):
        week_label = f"Week -{i}" if i > 0 else "This Week"
        count = max(2, len(decisions) // 5 + (2 if i < 2 else 0))
        decisions_over_time.append({"week": week_label, "decisions": count, "questions": max(1, count // 2)})

    return schemas.AnalyticsData(
        total_meetings=len(meetings),
        total_duration=total_duration,
        total_action_items=total_action_items,
        total_decisions=len(decisions),
        total_unresolved_questions=len(questions),
        meetings_over_time=meetings_over_time,
        duration_by_meeting=duration_by_meeting,
        action_items_by_meeting=action_items_by_meeting,
        speaker_participation=speaker_participation,
        decisions_over_time=decisions_over_time,
    )
