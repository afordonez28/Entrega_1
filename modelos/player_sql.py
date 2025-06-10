from sqlalchemy import Column, Integer, Float, Boolean
from utils.conection_db import Base
from sqlmodel import SQLModel, Field

class PlayerModel(SQLModel, table=True):
    __tablename__ = "players"  # Opcional: SQLModel puede generar esto automáticamente

    id: int | None = Field(default=None, primary_key=True)
    name: str
    health: int
    armor: int
