from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# --- Speaker ---
class SpeakerBase(BaseModel):
    name: str
    role: Optional[str] = None
    speaking_time: float = 0.0
    word_count: int = 0
    avatar_color: Optional[str] = None


class SpeakerOut(SpeakerBase):
    id: int
    meeting_id: int

    class Config:
        from_attributes = True


# --- TranscriptSegment ---
class TranscriptSegmentOut(BaseModel):
    id: int
    meeting_id: int
    speaker_name: Optional[str]
    text: str
    start_time: float
    end_time: float
    confidence: float

    class Config:
        from_attributes = True


# --- Decision ---
class DecisionOut(BaseModel):
    id: int
    meeting_id: int
    text: str
    timestamp: Optional[float]
    speaker_name: Optional[str]
    importance: str

    class Config:
        from_attributes = True


# --- ActionItem ---
class ActionItemOut(BaseModel):
    id: int
    meeting_id: int
    title: str
    assignee: Optional[str]
    deadline: Optional[str]
    status: str
    priority: str
    timestamp: Optional[float]

    class Config:
        from_attributes = True


# --- UnresolvedQuestion ---
class UnresolvedQuestionOut(BaseModel):
    id: int
    meeting_id: int
    text: str
    asked_by: Optional[str]
    timestamp: Optional[float]

    class Config:
        from_attributes = True


# --- Chapter ---
class ChapterOut(BaseModel):
    id: int
    meeting_id: int
    title: str
    start_time: float
    end_time: float
    summary: Optional[str]

    class Config:
        from_attributes = True


# --- Meeting ---
class MeetingOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    duration: float
    file_path: Optional[str]
    thumbnail_url: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    summary: Optional[str]
    key_topics: Optional[str]
    sentiment: Optional[str]
    meeting_type: Optional[str]

    class Config:
        from_attributes = True


class MeetingDetail(MeetingOut):
    speakers: List[SpeakerOut] = []
    decisions: List[DecisionOut] = []
    action_items: List[ActionItemOut] = []
    unresolved_questions: List[UnresolvedQuestionOut] = []
    chapters: List[ChapterOut] = []


class MeetingAnalysis(BaseModel):
    summary: str
    key_topics: List[str]
    sentiment: str
    meeting_type: str
    decisions: List[DecisionOut]
    action_items: List[ActionItemOut]
    unresolved_questions: List[UnresolvedQuestionOut]
    chapters: List[ChapterOut]
    speakers: List[SpeakerOut]


# --- Task ---
class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assignee: Optional[str]
    deadline: Optional[str]
    status: str
    priority: str
    meeting_id: Optional[int]
    meeting_title: Optional[str]
    source_timestamp: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[str] = None


# --- Ask Meeting ---
class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[dict] = []


# --- Catch Me Up ---
class CatchMeUpRequest(BaseModel):
    from_timestamp: Optional[float] = None


class CatchMeUpResponse(BaseModel):
    summary: str
    key_points: List[str]
    missed_decisions: List[str]
    action_items_for_you: List[str]


# --- Follow Up Email ---
class FollowUpEmailRequest(BaseModel):
    recipient_name: Optional[str] = None
    additional_notes: Optional[str] = None


class FollowUpEmailResponse(BaseModel):
    subject: str
    body: str


# --- Search ---
class SearchResult(BaseModel):
    type: str  # meeting, transcript, task, decision
    id: int
    title: str
    excerpt: str
    meeting_id: Optional[int] = None
    timestamp: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int


# --- Analytics ---
class AnalyticsData(BaseModel):
    total_meetings: int
    total_duration: float
    total_action_items: int
    total_decisions: int
    total_unresolved_questions: int
    meetings_over_time: List[dict]
    duration_by_meeting: List[dict]
    action_items_by_meeting: List[dict]
    speaker_participation: List[dict]
    decisions_over_time: List[dict]
