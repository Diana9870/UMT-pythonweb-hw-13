from fastapi import FastAPI
from app.routes import auth, users
from app.database.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)