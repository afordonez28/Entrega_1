import csv
import os
from typing import List
from models import Player, PlayerWithID

# ------------------------ RUTAS Y CONSTANTES ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "../data/players.csv")
DELETED_CSV_FILE = os.path.join(BASE_DIR, "../data/deleted_players.csv")

FIELDNAMES = [
    "id", "name", "health", "regenerate_health",
    "speed", "jump", "is_dead", "armor", "hit_speed"
]

# ------------------------ FUNCIONES AUXILIARES ------------------------

def _read_csv(file_path: str) -> List[PlayerWithID]:
    data = []
    if not os.path.exists(file_path):
        return data
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(PlayerWithID(
                id=int(row["id"]),
                name=row["name"],
                health=int(row["health"]),
                regenerate_health=int(row["regenerate_health"]),
                speed=float(row["speed"]),
                jump=float(row["jump"]),
                is_dead=row["is_dead"] == "True",
                armor=int(row["armor"]),
                hit_speed=int(row["hit_speed"]),
            ))
    return data

def _write_csv(file_path: str, data: List[PlayerWithID]):
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for item in data:
            writer.writerow(item.dict())

def _append_to_csv(file_path: str, item: PlayerWithID):
    file_exists = os.path.exists(file_path)
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists or os.stat(file_path).st_size == 0:
            writer.writeheader()
        writer.writerow(item.dict())

# ------------------------ CRUD ------------------------

async def get_all_players() -> List[PlayerWithID]:
    return _read_csv(CSV_FILE)

async def get_deleted_players() -> List[PlayerWithID]:
    return _read_csv(DELETED_CSV_FILE)

async def get_player(player_id: int) -> PlayerWithID | None:
    data = _read_csv(CSV_FILE)
    for item in data:
        if item.id == player_id:
            return item
    return None

async def create_player(player: Player) -> PlayerWithID:
    data = _read_csv(CSV_FILE)
    new_id = max([item.id for item in data], default=0) + 1
    new_player = PlayerWithID(id=new_id, **player.dict())
    _append_to_csv(CSV_FILE, new_player)
    return new_player

async def update_player(player_id: int, updated_data: dict) -> PlayerWithID | None:
    data = _read_csv(CSV_FILE)
    updated = None
    for i, item in enumerate(data):
        if item.id == player_id:
            updated_dict = {**item.dict(), **updated_data}
            updated = PlayerWithID(**updated_dict)
            data[i] = updated
            break
    if updated:
        _write_csv(CSV_FILE, data)
    return updated

async def delete_player(player_id: int) -> PlayerWithID | None:
    data = _read_csv(CSV_FILE)
    deleted = None
    new_data = []
    for item in data:
        if item.id == player_id:
            deleted = item
        else:
            new_data.append(item)
    if deleted:
        _write_csv(CSV_FILE, new_data)
        _append_to_csv(DELETED_CSV_FILE, deleted)
    return deleted

async def delete_all_players() -> List[PlayerWithID]:
    data = _read_csv(CSV_FILE)
    for item in data:
        _append_to_csv(DELETED_CSV_FILE, item)
    _write_csv(CSV_FILE, [])
    return data

async def restore_player(player_id: int) -> PlayerWithID | None:
    deleted = _read_csv(DELETED_CSV_FILE)
    to_restore = None
    remaining = []
    for item in deleted:
        if item.id == player_id:
            to_restore = item
        else:
            remaining.append(item)
    if to_restore:
        current = _read_csv(CSV_FILE)
        current.append(to_restore)
        _write_csv(CSV_FILE, current)
        _write_csv(DELETED_CSV_FILE, remaining)
    return to_restore
