from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from src import crud, models, schemas
from src.database import get_db

router = APIRouter()

@router.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = crud.get_task_by_title(db, title=task.title)
    if db_task:
        raise HTTPException(status_code=400, detail="Title already registered")
    return crud.create_task(db=db, task=task)

@router.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.get("/tasks/{task_id}", response_model=schemas.Task, summary="Get task by ID")
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if crud.get_task_by_title(db, title=task.title) and db_task.title != task.title:
        raise HTTPException(status_code=400, detail="Title already registered")
    db_task.title = task.title
    db_task.description = task.description
    db_task.status = task.status
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/tasks/{task_id}", response_model=schemas.Task)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return db_task

@router.post("/pomodoro/", response_model=schemas.PomodoroSession)
def create_pomodoro_session(session: schemas.PomodoroSessionCreate, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=session.task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.create_pomodoro_session(db=db, session=session)

@router.post("/pomodoro/{task_id}/stop", response_model=schemas.PomodoroSession)
def stop_pomodoro_session(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_session = crud.get_active_pomodoro_session(db, task_id=task_id)
    if db_session is None:
        raise HTTPException(status_code=400, detail="No active Pomodoro session found")
    db_session.completed = True
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/pomodoro/stats", response_model=List[schemas.PomodoroStats])
def get_pomodoro_stats(db: Session = Depends(get_db)):
    stats = crud.get_pomodoro_stats(db)
    return [
        schemas.PomodoroStats(
            task_id=task_id,
            completed_sessions=data["completed_sessions"],
            total_time_spent=data["total_time_spent"]
        )
        for task_id, data in stats.items()
    ]