import csv
from typing import List, Optional
from models import Player, PlayerWithID
from fastapi import APIRouter, HTTPException
import os
router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")

PLAYER_CSV = os.path.join(DATA_DIR, "players.csv")
DELETED_PLAYER_CSV = os.path.join(DATA_DIR, "deleted_players.csv")
PLAYER_FIELDS = ["id", "name", "health", "regenerate_health", "speed", "jump", "is_dead", "armor", "hit_speed"]

# ---------------------- CRUD Functions ----------------------
os.makedirs(DATA_DIR, exist_ok=True)


async def read_all_players() -> List[PlayerWithID]:
    players = []
    try:
        with open(PLAYER_CSV, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                players.append(PlayerWithID(**{**row, "id": int(row["id"]), "health": int(row["health"]),
                                               "regenerate_health": int(row["regenerate_health"]),
                                               "speed": int(row["speed"]), "jump": int(row["jump"]),
                                               "is_dead": row["is_dead"] == "True",
                                               "armor": int(row["armor"]), "hit_speed": int(row["hit_speed"])}))
    except FileNotFoundError:
        pass
    return players

async def read_one_player(player_id: int) -> Optional[PlayerWithID]:
    players = await read_all_players()
    for player in players:
        if player.id == player_id:
            return player
    return None

async def create_player(player: Player) -> PlayerWithID:
    players = await read_all_players()
    new_id = max([p.id for p in players], default=0) + 1

    # Creamos un diccionario que incluye explícitamente todos los campos necesarios
    player_with_id = PlayerWithID(id=new_id, **player.dict())
    player_dict = {
        "id": player_with_id.id,
        "name": player_with_id.name,
        "health": player_with_id.health,
        "regenerate_health": player_with_id.regenerate_health,
        "speed": player_with_id.speed,
        "jump": player_with_id.jump,
        "is_dead": str(player_with_id.is_dead),  # Guardar como string para CSV
        "armor": player_with_id.armor,
        "hit_speed": player_with_id.hit_speed
    }

    with open(PLAYER_CSV, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=PLAYER_FIELDS)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(player_dict)

    return player_with_id


async def update_player(player_id: int, update_data: dict) -> Optional[PlayerWithID]:
    players = await read_all_players()
    updated = None
    for i, player in enumerate(players):
        if player.id == player_id:
            player_data = player.dict()
            player_data.update(update_data)
            players[i] = PlayerWithID(**player_data)
            updated = players[i]
            break
    if updated:
        with open(PLAYER_CSV, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=PLAYER_FIELDS)
            writer.writeheader()
            for p in players:
                writer.writerow(p.dict())
    return updated

async def delete_player(player_id: int) -> Optional[PlayerWithID]:
    players = await read_all_players()
    deleted = None
    remaining = []
    for p in players:
        if p.id == player_id:
            deleted = p
        else:
            remaining.append(p)
    if deleted:
        with open(PLAYER_CSV, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=PLAYER_FIELDS)
            writer.writeheader()
            for p in remaining:
                writer.writerow(p.dict())
        with open(DELETED_PLAYER_CSV, mode="a", newline="") as d_file:
            writer = csv.DictWriter(d_file, fieldnames=PLAYER_FIELDS)
            if d_file.tell() == 0:
                writer.writeheader()
            writer.writerow(deleted.dict())
    return deleted

async def delete_all_players() -> List[PlayerWithID]:
    players = await read_all_players()
    with open(PLAYER_CSV, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=PLAYER_FIELDS)
        writer.writeheader()
    with open(DELETED_PLAYER_CSV, mode="a", newline="") as d_file:
        writer = csv.DictWriter(d_file, fieldnames=PLAYER_FIELDS)
        if d_file.tell() == 0:
            writer.writeheader()
        for p in players:
            writer.writerow(p.dict())
    return players

async def read_deleted_players() -> List[PlayerWithID]:
    players = []
    try:
        with open(DELETED_PLAYER_CSV, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                players.append(PlayerWithID(**{**row, "id": int(row["id"]), "health": int(row["health"]),
                                               "regenerate_health": int(row["regenerate_health"]),
                                               "speed": int(row["speed"]), "jump": int(row["jump"]),
                                               "is_dead": row["is_dead"] == "True",
                                               "armor": int(row["armor"]), "hit_speed": int(row["hit_speed"])}))
    except FileNotFoundError:
        pass
    return players

async def revive_player_by_id(player_id: int) -> Optional[PlayerWithID]:
    deleted = await read_deleted_players()
    restored = None
    remaining = []
    for p in deleted:
        if p.id == player_id:
            restored = p
        else:
            remaining.append(p)
    if restored:
        with open(PLAYER_CSV, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=PLAYER_FIELDS)
            writer.writerow(restored.dict())
        with open(DELETED_PLAYER_CSV, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=PLAYER_FIELDS)
            writer.writeheader()
            for p in remaining:
                writer.writerow(p.dict())
    return restored

# ---------------------- Router Endpoints ----------------------

@router.get("/", response_model=List[PlayerWithID])
async def get_players():
    return await read_all_players()

@router.get("/{player_id}", response_model=PlayerWithID)
async def get_player(player_id: int):
    player = await read_one_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.post("/", response_model=PlayerWithID)
async def post_player(player: Player):
    return await create_player(player)

@router.put("/{player_id}", response_model=PlayerWithID)
async def put_player(player_id: int, player_update: Player):
    updated = await update_player(player_id, player_update.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated

@router.delete("/{player_id}", response_model=PlayerWithID)
async def delete_single_player(player_id: int):
    deleted = await delete_player(player_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Player not found")
    return deleted

@router.delete("/", response_model=List[PlayerWithID])
async def delete_all():
    return await delete_all_players()

@router.get("/deleted/", response_model=List[PlayerWithID])
async def get_deleted_players_route():
    return await read_deleted_players()

@router.put("/revive/{player_id}", response_model=PlayerWithID)
async def revive(player_id: int):
    revived = await revive_player_by_id(player_id)
    if not revived:
        raise HTTPException(status_code=404, detail="Player not found")
    return revived



# Almacén temporal en memoria
temporary_players = []
temporary_id_counter = 10000  # Un número alto para no colisionar con CSV

async def create_temporary_player(player: Player) -> PlayerWithID:
    global temporary_id_counter
    temporary_id_counter += 1
    new_player = PlayerWithID(id=temporary_id_counter, **player.dict())
    temporary_players.append(new_player)
    return new_player

async def read_all_temporary_players() -> List[PlayerWithID]:
    return temporary_players
