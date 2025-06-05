from sqlalchemy import Column, Integer, String
from src.configurations.database import BaseModel

class User(BaseModel):
    __tablename__ = "users_table"

    id = Column(Integer, primary_key=True)
    e_mail = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
