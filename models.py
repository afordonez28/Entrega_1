from pydantic import BaseModel, Field
from typing import Optional

class Player(BaseModel):
    name: str = Field(..., min_length=1, example="Juan")
    health: int = Field(..., ge=0)
    regenerate_health: int = Field(..., ge=0)
    speed: float = Field(..., gt=0)
    jump: float = Field(..., gt=0)
    is_dead: bool
    armor: int = Field(..., ge=0)
    hit_speed: int = Field(..., ge=0)
    image: str = Field(..., example="data:image/png;base64,...")  # Campo para la imagen en base64

class PlayerCreate(Player):
    pass

class PlayerWithID(Player):
    id: int

class Enemy(BaseModel):
    name: str = Field(..., min_length=1, example="Orco")
    speed: float = Field(..., gt=0, example=1.5)
    jump: float = Field(..., gt=0, example=1.2)
    hit_speed: int = Field(..., ge=0, example=2)
    health: int = Field(..., ge=0, example=100)
    type: str = Field(..., min_length=1, example="goblin")
    spawn: float = Field(..., gt=0, example=3.0)
    probability_spawn: float = Field(..., ge=0, example=0.5)
    image: str = Field(..., example="data:image/png;base64,...")  # Campo para la imagen en base64

class EnemyCreate(Enemy):
    pass

class EnemyWithID(Enemy):
    id: int