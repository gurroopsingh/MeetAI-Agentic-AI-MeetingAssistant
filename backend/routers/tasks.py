from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from tools.task_tool import TaskTool

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
task_tool = TaskTool()


@router.get("", response_model=List[schemas.TaskOut])
def get_tasks(
    status: Optional[str] = None,
    meeting_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get all tasks, optionally filtered by status or meeting."""
    return task_tool.list_tasks(db, status=status, meeting_id=meeting_id)


@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single task."""
    task = task_tool.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update a task (status, priority, assignee, deadline)."""
    task = task_tool.update_task(db, task_id, update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=schemas.TaskOut)
def create_task(
    title: str,
    assignee: Optional[str] = None,
    deadline: Optional[str] = None,
    priority: str = "medium",
    db: Session = Depends(get_db),
):
    """Create a standalone task."""
    return task_tool.create_task(db, title=title, assignee=assignee, deadline=deadline, priority=priority)
