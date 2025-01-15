from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    status: Optional[str] = Field("TODO")

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    pomodoro_sessions: List["PomodoroSession"] = []

    class Config:
        orm_mode = True

class PomodoroSessionBase(BaseModel):
    task_id: int
    start_time: datetime
    end_time: datetime
    completed: bool

class PomodoroSessionCreate(PomodoroSessionBase):
    pass

class PomodoroSession(PomodoroSessionBase):
    id: int

    class Config:
        orm_mode = True

class PomodoroStats(BaseModel):
    task_id: int
    completed_sessions: int
    total_time_spent: str