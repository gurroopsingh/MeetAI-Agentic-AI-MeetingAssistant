"""
Task Tool — Manages meeting-derived tasks/action items.
MCP-ready: this tool can be exposed as an MCP tool in the future.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import models
from schemas import TaskUpdate


class TaskTool:
    """Tool for creating and managing tasks derived from meeting action items."""

    def create_task(self, db: Session, title: str, assignee: Optional[str] = None,
                    deadline: Optional[str] = None, priority: str = "medium",
                    meeting_id: Optional[int] = None, meeting_title: Optional[str] = None,
                    source_timestamp: Optional[float] = None) -> models.Task:
        """Create a new task."""
        task = models.Task(
            title=title,
            assignee=assignee,
            deadline=deadline,
            priority=priority,
            status="todo",
            meeting_id=meeting_id,
            meeting_title=meeting_title,
            source_timestamp=source_timestamp,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update_task(self, db: Session, task_id: int, update: TaskUpdate) -> Optional[models.Task]:
        """Update task fields."""
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            return None

        update_data = update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)
        return task

    def list_tasks(self, db: Session, status: Optional[str] = None,
                   meeting_id: Optional[int] = None) -> List[models.Task]:
        """List tasks with optional filters."""
        query = db.query(models.Task)
        if status:
            query = query.filter(models.Task.status == status)
        if meeting_id:
            query = query.filter(models.Task.meeting_id == meeting_id)
        return query.order_by(models.Task.created_at.desc()).all()

    def get_task(self, db: Session, task_id: int) -> Optional[models.Task]:
        """Get a single task by ID."""
        return db.query(models.Task).filter(models.Task.id == task_id).first()
