import csv
import os
from typing import List, Optional
from models import Player, PlayerWithID
from fastapi import UploadFile
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

PLAYER_CSV = os.path.join(DATA_DIR, "players.csv")
DELETED_CSV = os.path.join(DATA_DIR, "deleted_players.csv")
FIELDS = ["id", "name", "health", "regenerate_health", "speed", "jump", "is_dead", "armor", "hit_speed"]

# -------------------- CRUD PRINCIPAL --------------------

async def read_all_players() -> List[PlayerWithID]:
    players = []
    if not os.path.exists(PLAYER_CSV):
        return players

    with open(PLAYER_CSV, mode="r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            players.append(PlayerWithID(**_parse_row(row)))
    return players


async def read_one_player(player_id: int) -> Optional[PlayerWithID]:
    players = await read_all_players()
    return next((p for p in players if p.id == player_id), None)


async def create_player(player: Player, image: Optional[UploadFile] = None) -> PlayerWithID:
    players = await read_all_players()
    new_id = (max([p.id for p in players]) + 1) if players else 1

    new_player = PlayerWithID(id=new_id, **player.dict())

    # Guardar imagen si fue proporcionada
    if image:
        image_filename = f"{player.name.lower().replace(' ', '_')}.png"
        image_path = os.path.join(UPLOADS_DIR, image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    # Guardar en CSV
    file_exists = os.path.exists(PLAYER_CSV)
    with open(PLAYER_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(new_player.dict())

    return new_player


    # Guardar imagen (opcional)
    if image:
        extension = os.path.splitext(image.filename)[1].lower()
        if extension not in [".png", ".jpg", ".jpeg"]:
            raise ValueError("Formato de imagen no permitido.")
        image_path = os.path.join(UPLOADS_DIR, f"player_{new_id}{extension}")
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

    return new_player


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
        _write_players(players)
    return updated


async def delete_player(player_id: int) -> Optional[PlayerWithID]:
    players = await read_all_players()
    deleted = next((p for p in players if p.id == player_id), None)

    if not deleted:
        return None

    remaining = [p for p in players if p.id != player_id]
    _write_players(remaining)
    _store_deleted(deleted)
    return deleted


async def delete_all_players() -> List[PlayerWithID]:
    players = await read_all_players()
    for p in players:
        _store_deleted(p)
    _write_players([])
    return players


# -------------------- RESTAURAR Y BUSCAR --------------------

async def read_deleted_players() -> List[PlayerWithID]:
    if not os.path.exists(DELETED_CSV):
        return []
    with open(DELETED_CSV, mode="r", encoding="utf-8") as f:
        return [PlayerWithID(**_parse_row(r)) for r in csv.DictReader(f)]


async def revive_player_by_id(player_id: int) -> Optional[PlayerWithID]:
    deleted = await read_deleted_players()
    revived = next((p for p in deleted if p.id == player_id), None)

    if not revived:
        return None

    remaining = [p for p in deleted if p.id != player_id]
    _write_deleted(remaining)

    current = await read_all_players()
    _write_players(current + [revived])
    return revived


# -------------------- FUNCIONES AUXILIARES --------------------

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


def _write_players(players: List[PlayerWithID]):
    with open(PLAYER_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for p in players:
            writer.writerow(p.dict())


def _store_deleted(player: PlayerWithID):
    os.makedirs(DATA_DIR, exist_ok=True)
    mode = "a" if os.path.exists(DELETED_CSV) else "w"
    with open(DELETED_CSV, mode=mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(player.dict())


def _write_deleted(players: List[PlayerWithID]):
    with open(DELETED_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for p in players:
            writer.writerow(p.dict())
