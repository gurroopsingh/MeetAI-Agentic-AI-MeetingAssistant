import asyncio
import json
import os
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from agent.meeting_agent import MeetingAgent

router = APIRouter(prefix="/api/meetings", tags=["meetings"])
agent = MeetingAgent()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def _process_meeting_background(meeting_id: int):
    """Background task: runs the meeting agent pipeline."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = "processing"
            db.commit()
            await agent.process_meeting(db, meeting)
    except Exception as e:
        db_err = SessionLocal()
        m = db_err.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        if m:
            m.status = "failed"
            db_err.commit()
        db_err.close()
        raise e
    finally:
        db.close()


@router.post("/upload", response_model=schemas.MeetingOut)
async def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a meeting video/audio file and start processing."""
    # Validate file type
    allowed = ["video/mp4", "video/quicktime", "video/webm", "audio/mpeg", "audio/wav"]
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "mp4"
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Create meeting record
    original_name = file.filename.rsplit(".", 1)[0] if file.filename else "New Meeting"
    title = original_name.replace("_", " ").replace("-", " ").title()
    meeting = models.Meeting(
        title=title,
        status="processing",
        file_path=file_path,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    # Queue background processing
    background_tasks.add_task(_process_meeting_background, meeting.id)

    return meeting


@router.get("", response_model=List[schemas.MeetingOut])
def get_meetings(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get all meetings."""
    return db.query(models.Meeting).order_by(models.Meeting.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{meeting_id}", response_model=schemas.MeetingDetail)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Get a single meeting with all related data."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.get("/{meeting_id}/video")
def get_meeting_video(meeting_id: int, db: Session = Depends(get_db)):
    """Serve the meeting video file (supports HTTP Range requests)."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting or not meeting.file_path or not os.path.exists(meeting.file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
        
    ext = meeting.file_path.rsplit(".", 1)[-1].lower()
    content_types = {
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mov": "video/quicktime",
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
    }
    media_type = content_types.get(ext, "application/octet-stream")
    
    return FileResponse(meeting.file_path, media_type=media_type, headers={"Accept-Ranges": "bytes"})


@router.get("/{meeting_id}/transcript", response_model=List[schemas.TranscriptSegmentOut])
def get_transcript(meeting_id: int, db: Session = Depends(get_db)):
    """Get transcript segments for a meeting."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return db.query(models.TranscriptSegment).filter(
        models.TranscriptSegment.meeting_id == meeting_id
    ).order_by(models.TranscriptSegment.start_time).all()


@router.get("/{meeting_id}/analysis", response_model=schemas.MeetingAnalysis)
def get_analysis(meeting_id: int, db: Session = Depends(get_db)):
    """Get full analysis for a meeting."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    topics = []
    if meeting.key_topics:
        try:
            topics = json.loads(meeting.key_topics)
        except Exception:
            topics = []

    return schemas.MeetingAnalysis(
        summary=meeting.summary or "",
        key_topics=topics,
        sentiment=meeting.sentiment or "neutral",
        meeting_type=meeting.meeting_type or "General",
        decisions=[schemas.DecisionOut.model_validate(d) for d in meeting.decisions],
        action_items=[schemas.ActionItemOut.model_validate(a) for a in meeting.action_items],
        unresolved_questions=[schemas.UnresolvedQuestionOut.model_validate(q) for q in meeting.unresolved_questions],
        chapters=[schemas.ChapterOut.model_validate(c) for c in meeting.chapters],
        speakers=[schemas.SpeakerOut.model_validate(s) for s in meeting.speakers],
    )


@router.post("/{meeting_id}/ask", response_model=schemas.AskResponse)
async def ask_meeting(
    meeting_id: int,
    request: schemas.AskRequest,
    db: Session = Depends(get_db),
):
    """Ask a question about a specific meeting."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    result = await agent.ask_question(db, meeting_id, request.question)
    return schemas.AskResponse(answer=result["answer"], sources=result.get("sources", []))


@router.post("/{meeting_id}/catch-up", response_model=schemas.CatchMeUpResponse)
async def catch_me_up(
    meeting_id: int,
    request: schemas.CatchMeUpRequest,
    db: Session = Depends(get_db),
):
    """Generate a catch-up summary for a meeting."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    result = await agent.generate_catch_up(db, meeting_id, request.from_timestamp)
    return schemas.CatchMeUpResponse(**result)


@router.post("/{meeting_id}/follow-up", response_model=schemas.FollowUpEmailResponse)
async def generate_follow_up(
    meeting_id: int,
    request: schemas.FollowUpEmailRequest,
    db: Session = Depends(get_db),
):
    """Generate a follow-up email for a meeting."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    result = await agent.generate_follow_up_email(db, meeting_id, request.recipient_name, request.additional_notes)
    return schemas.FollowUpEmailResponse(**result)


@router.delete("/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Delete a meeting."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    db.delete(meeting)
    db.commit()
    return {"message": "Meeting deleted"}
