from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PlayerModel(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    health = Column(Integer)
    regenerate_health = Column(Integer)
    speed = Column(Float)
    jump = Column(Float)
    is_dead = Column(Boolean, default=False)
    armor = Column(Integer)
    hit_speed = Column(Integer)
    image = Column(String)  # Nueva columna para la imagen

class EnemyModel(Base):
    __tablename__ = "enemies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    speed = Column(Float)
    jump = Column(Float)
    hit_speed = Column(Integer)
    health = Column(Integer)
    type = Column(String)
    spawn = Column(Float)
    probability_spawn = Column(Float)
    image = Column(String)  # Nueva columna para la imagen