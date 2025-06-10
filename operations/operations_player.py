import csv
from typing import List
from models import Player, PlayerWithID

# ------------------------ RUTAS Y CONSTANTES ------------------------
CSV_FILE = "data/player.csv"
DELETED_CSV_FILE = "data/deleted_player.csv"
FIELDNAMES = ["id", "name", "health", "regenerate_health", "speed", "jump", "is_dead", "armor", "hit_speed"]


from typing import List, Optional
from models import Player, PlayerWithID  # Asegúrate de tener estos modelos definidos

# ------------------------ UTILIDADES DE ARCHIVO ------------------------

def write_players_to_csv(players: List[PlayerWithID], file_path: str = CSV_FILE):
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for player in players:
            writer.writerow(player.dict())

def append_to_deleted_players(player: PlayerWithID):
    try:
        with open(DELETED_CSV_FILE, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(player.dict())
    except Exception as e:
        print(f"Error writing to deleted_players.csv: {e}")

def read_players_from_csv(file_path: str = CSV_FILE) -> List[PlayerWithID]:
    players = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["id"] = int(row["id"])
                row["name"] = row["name"]
                row["health"] = int(row["health"])
                row["regenerate_health"] = int(row["regenerate_health"])
                row["speed"] = int(row["speed"])
                row["jump"] = int(row["jump"])
                row["is_dead"] = int(row["is_dead"])
                row["armor"] = int(row["armor"])
                row["hit_speed"] = int(row["hit_speed"])
                players.append(PlayerWithID(**row))
    except FileNotFoundError:
        pass
    return players

# ------------------------ CRUD PRINCIPALES ------------------------

async def get_all_players() -> List[PlayerWithID]:
    return read_players_from_csv()

async def get_deleted_players() -> List[PlayerWithID]:
    return read_players_from_csv(DELETED_CSV_FILE)

async def get_player(player_id: int) -> Optional[PlayerWithID]:
    players = await get_all_players()
    for player in players:
        if player.id == player_id:
            return player
    return None

async def create_player(player: Player) -> PlayerWithID:
    players = read_players_from_csv()
    new_id = max([p.id for p in players], default=0) + 1
    player_with_id = PlayerWithID(id=new_id, **player.dict())
    players.append(player_with_id)
    write_players_to_csv(players)
    return player_with_id

async def update_player(player_id: int, updated_data: dict) -> Optional[PlayerWithID]:
    players = await get_all_players()
    updated_player = None
    for i, player in enumerate(players):
        if player.id == player_id:
            updated_dict = {**player.dict(), **updated_data}
            updated_player = PlayerWithID(**updated_dict)
            players[i] = updated_player
            break
    if updated_player:
        write_players_to_csv(players)
    return updated_player

async def delete_player(player_id: int) -> Optional[PlayerWithID]:
    players = await get_all_players()
    new_players = []
    removed_player = None
    for player in players:
        if player.id == player_id:
            removed_player = player
        else:
            new_players.append(player)
    if removed_player:
        write_players_to_csv(new_players)
        append_to_deleted_players(removed_player)
        return removed_player
    return None

async def delete_all_players() -> List[PlayerWithID]:
    players = await get_all_players()
    for player in players:
        append_to_deleted_players(player)
    write_players_to_csv([])
    return players

async def restore_player(player_id: int) -> Optional[PlayerWithID]:
    deleted_players = await get_deleted_players()
    to_restore = None
    remaining = []
    for player in deleted_players:
        if player.id == player_id:
            to_restore = player
        else:
            remaining.append(player)
    if to_restore:
        current_players = await get_all_players()
        current_players.append(to_restore)
        write_players_to_csv(current_players)
        write_players_to_csv(remaining, DELETED_CSV_FILE)
    return to_restore

