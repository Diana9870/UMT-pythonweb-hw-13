from sqlalchemy import Column, Integer, String
from .db import Base


class User(Base):
    """
    User model
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="user")