from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models import Task, PomodoroSession
from src.schemas import TaskCreate, PomodoroSessionCreate
from datetime import timedelta

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_task_by_title(db: Session, title: str):
    return db.query(Task).filter(Task.title == title).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: TaskCreate):
    db_task = Task(title=task.title, description=task.description, status=task.status)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def create_pomodoro_session(db: Session, session: PomodoroSessionCreate):
    db_session = PomodoroSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_active_pomodoro_session(db: Session, task_id: int):
    return db.query(PomodoroSession).filter(PomodoroSession.task_id == task_id, PomodoroSession.completed == False).first()

#formating time to string (not working)

def format_timedelta(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}m {seconds}s"

def get_pomodoro_stats(db: Session):
    completed_sessions = db.query(PomodoroSession).filter(PomodoroSession.completed == True).all()
    stats = {}
    for session in completed_sessions:
        if session.task_id not in stats:
            stats[session.task_id] = {
                "completed_sessions": 0,
                "total_time_spent": timedelta()
            }
        stats[session.task_id]["completed_sessions"] += 1
        stats[session.task_id]["total_time_spent"] += session.end_time - session.start_time
    
    for task_id in stats:
        stats[task_id]["total_time_spent"] = format_timedelta(stats[task_id]["total_time_spent"])
    
    return stats