from fastapi import FastAPI
from src.database import engine
from src import models
from src.routers import tasks

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(tasks.router)