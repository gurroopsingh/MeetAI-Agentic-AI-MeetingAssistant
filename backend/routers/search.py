from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
import schemas
from tools.meeting_search_tool import MeetingSearchTool

router = APIRouter(prefix="/api/search", tags=["search"])
search_tool = MeetingSearchTool()


@router.get("", response_model=schemas.SearchResponse)
def search(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    """Global search across meetings, transcripts, tasks, and decisions."""
    results = search_tool.search(db, q)
    return schemas.SearchResponse(results=results, total=len(results))
