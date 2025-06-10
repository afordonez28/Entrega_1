import csv
import os
import shutil
from typing import List, Optional
from fastapi import UploadFile
from models import Player, PlayerWithID

# ---------------------- CONFIGURACIÓN DE RUTAS ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
PLAYER_CSV = os.path.join(DATA_DIR, "players.csv")
DELETED_PLAYER_CSV = os.path.join(DATA_DIR, "deleted_players.csv")

PLAYER_FIELDS = [
    "id", "name", "health", "regenerate_health",
    "speed", "jump", "is_dead", "armor", "hit_speed"
]

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ---------------------- FUNCIONES AUXILIARES ----------------------

def _parse_row(row: dict) -> dict:
    return {
        "id": int(row["id"]),
        "name": row["name"],
        "health": int(row["health"]),
        "regenerate_health": int(row["regenerate_health"]),
        "speed": int(row["speed"]),
        "jump": int(row["jump"]),
        "is_dead": row["is_dead"] == "True",
        "armor": int(row["armor"]),
        "hit_speed": int(row["hit_speed"]),
    }

def _write_players_to_csv(players: List[PlayerWithID]):
    with open(PLAYER_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PLAYER_FIELDS)
        writer.writeheader()
        for p in players:
            writer.writerow(p.dict())

def _append_to_deleted_players(player: PlayerWithID):
    with open(DELETED_PLAYER_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PLAYER_FIELDS)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(player.dict())

def _write_deleted_players(players: List[PlayerWithID]):
    with open(DELETED_PLAYER_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PLAYER_FIELDS)
        writer.writeheader()
        for p in players:
            writer.writerow(p.dict())

# ---------------------- LECTURAS ----------------------

async def read_all_players() -> List[PlayerWithID]:
    players = []
    if not os.path.exists(PLAYER_CSV):
        return players
    with open(PLAYER_CSV, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            players.append(PlayerWithID(**_parse_row(row)))
    return players

async def read_deleted_players() -> List[PlayerWithID]:
    if not os.path.exists(DELETED_PLAYER_CSV):
        return []
    with open(DELETED_PLAYER_CSV, mode="r", encoding="utf-8") as f:
        return [PlayerWithID(**_parse_row(row)) for row in csv.DictReader(f)]

async def read_one_player(player_id: int) -> Optional[PlayerWithID]:
    players = await read_all_players()
    for player in players:
        if player.id == player_id:
            return player
    return None

# ---------------------- CRUD PRINCIPAL ----------------------

async def create_player(player: Player, image: Optional[UploadFile] = None) -> PlayerWithID:
    players = await read_all_players()
    new_id = max([p.id for p in players], default=0) + 1
    player_with_id = PlayerWithID(id=new_id, **player.dict())
    players.append(player_with_id)

    # Guardar imagen si fue proporcionada
    if image:
        ext = os.path.splitext(image.filename)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg"]:
            raise ValueError("Formato de imagen no permitido.")
        image_path = os.path.join(UPLOADS_DIR, f"player_{new_id}{ext}")
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

    _write_players_to_csv(players)
    return player_with_id

async def update_player(player_id: int, update: dict) -> Optional[PlayerWithID]:
    players = await read_all_players()
    updated = None
    for i, p in enumerate(players):
        if p.id == player_id:
            updated_data = {**p.dict(), **update}
            updated = PlayerWithID(**updated_data)
            players[i] = updated
            break
    if updated:
        _write_players_to_csv(players)
    return updated

async def delete_player(player_id: int) -> Optional[PlayerWithID]:
    players = await read_all_players()
    remaining = []
    deleted = None
    for p in players:
        if p.id == player_id:
            deleted = p
        else:
            remaining.append(p)
    if deleted:
        _write_players_to_csv(remaining)
        _append_to_deleted_players(deleted)
        return deleted
    return None

async def delete_all_players() -> List[PlayerWithID]:
    players = await read_all_players()
    for p in players:
        _append_to_deleted_players(p)
    _write_players_to_csv([])
    return players

# ---------------------- RESTAURACIÓN ----------------------

async def revive_player_by_id(player_id: int) -> Optional[PlayerWithID]:
    deleted = await read_deleted_players()
    revived = None
    remaining = []
    for p in deleted:
        if p.id == player_id:
            revived = p
        else:
            remaining.append(p)
    if revived:
        _write_deleted_players(remaining)
        current = await read_all_players()
        current.append(revived)
        _write_players_to_csv(current)
        return revived
    return None
