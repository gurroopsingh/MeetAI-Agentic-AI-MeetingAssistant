from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class MeetingStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default=MeetingStatus.READY)
    duration = Column(Float, default=0.0)  # seconds
    file_path = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    transcript_segments = relationship("TranscriptSegment", back_populates="meeting", cascade="all, delete-orphan")
    speakers = relationship("Speaker", back_populates="meeting", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="meeting", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
    unresolved_questions = relationship("UnresolvedQuestion", back_populates="meeting", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="meeting", cascade="all, delete-orphan")

    # AI Analysis fields
    summary = Column(Text, nullable=True)
    key_topics = Column(Text, nullable=True)  # JSON string
    sentiment = Column(String(50), nullable=True)
    meeting_type = Column(String(100), nullable=True)


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    speaker_name = Column(String(100), nullable=True)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)  # seconds
    end_time = Column(Float, nullable=False)    # seconds
    confidence = Column(Float, default=1.0)

    meeting = relationship("Meeting", back_populates="transcript_segments")


class Speaker(Base):
    __tablename__ = "speakers"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=True)
    speaking_time = Column(Float, default=0.0)  # seconds
    word_count = Column(Integer, default=0)
    avatar_color = Column(String(20), nullable=True)

    meeting = relationship("Meeting", back_populates="speakers")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(Float, nullable=True)  # seconds
    speaker_name = Column(String(100), nullable=True)
    importance = Column(String(20), default="medium")

    meeting = relationship("Meeting", back_populates="decisions")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    title = Column(String(500), nullable=False)
    assignee = Column(String(100), nullable=True)
    deadline = Column(String(50), nullable=True)
    status = Column(String(50), default=TaskStatus.TODO)
    priority = Column(String(20), default=TaskPriority.MEDIUM)
    timestamp = Column(Float, nullable=True)

    meeting = relationship("Meeting", back_populates="action_items")


class UnresolvedQuestion(Base):
    __tablename__ = "unresolved_questions"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    text = Column(Text, nullable=False)
    asked_by = Column(String(100), nullable=True)
    timestamp = Column(Float, nullable=True)

    meeting = relationship("Meeting", back_populates="unresolved_questions")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    title = Column(String(255), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)

    meeting = relationship("Meeting", back_populates="chapters")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    assignee = Column(String(100), nullable=True)
    deadline = Column(String(50), nullable=True)
    status = Column(String(50), default=TaskStatus.TODO)
    priority = Column(String(20), default=TaskPriority.MEDIUM)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    meeting_title = Column(String(255), nullable=True)
    source_timestamp = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
