import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal, Base, engine


Base.metadata.create_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)