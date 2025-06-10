import csv
from typing import List, Optional
from models import Player, PlayerWithID



PLAYER_CSV = "data/players.csv"
DELETED_PLAYER_CSV = "data/deleted_players.csv"
PLAYER_FIELDS = ["id", "name", "health", "regenerate_health", "speed", "jump", "is_dead", "armor", "hit_speed"]

def revive_player_by_id(player_id: int) -> Optional[PlayerWithID]:
    players = read_all_players()
    for player in players:
        if player.id == player_id:
            player.is_dead = False
            write_players_to_csv(players)
            return player
    return None


def write_players_to_csv(players: List[PlayerWithID]):
    with open(PLAYER_CSV, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=PLAYER_FIELDS)
        writer.writeheader()
        for player in players:
            writer.writerow(player.dict())

def read_all_players() -> List[PlayerWithID]:
    players = []
    try:
        with open(PLAYER_CSV, mode="r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['id'] = int(row['id'])
                row['name'] = row.get('name', 'SinNombre')
                row['health'] = int(row['health'])
                row['regenerate_health'] = int(row['regenerate_health'])
                row['speed'] = float(row['speed'])
                row['jump'] = float(row['jump'])
                row['is_dead'] = row['is_dead'].lower() == "true"
                row['armor'] = int(row['armor'])
                row['hit_speed'] = int(row['hit_speed'])
                players.append(PlayerWithID(**row))
    except FileNotFoundError:
        pass
    return players

def read_one_player(player_id: int) -> Optional[PlayerWithID]:
    players = read_all_players()
    for player in players:
        if player.id == player_id:
            return player
    return None

async def create_player(player: Player) -> PlayerWithID:
    players = read_all_players()
    new_id = max([p.id for p in players], default=0) + 1
    player_with_id = PlayerWithID(id=new_id, **player.dict())
    players.append(player_with_id)
    write_players_to_csv(players)
    return player_with_id

def update_player(player_id: int, player_update: dict) -> Optional[PlayerWithID]:
    players = read_all_players()
    updated_player = None
    for player in players:
        if player.id == player_id:
            for key, value in player_update.items():
                setattr(player, key, value)
            updated_player = player
            break
    if updated_player:
        write_players_to_csv(players)
        return updated_player
    return None

def delete_player(player_id: int) -> Optional[PlayerWithID]:
    players = read_all_players()
    removed_player = None
    new_players = []
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



def append_to_deleted_players(player: PlayerWithID):
    try:
        with open(DELETED_PLAYER_CSV, mode="a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=PLAYER_FIELDS)
            if csvfile.tell() == 0:  # Si el archivo está vacío, escribe encabezado
                writer.writeheader()
            writer.writerow(player.dict())
    except Exception as e:
        print(f"Error writing to deleted_players.csv: {e}")

def write_players_to_csv(players: List[PlayerWithID]):
    with open(PLAYER_CSV, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=PLAYER_FIELDS)
        writer.writeheader()
        for player in players:
            player_dict = player.dict()
            player_dict["is_dead"] = str(player_dict["is_dead"])  # ← esta línea es clave
            writer.writerow(player_dict)

def read_deleted_players() -> List[PlayerWithID]:
    players = []
    try:
        with open(DELETED_PLAYER_CSV, mode="r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['id'] = int(row['id'])
                row['name'] = row.get('name', 'SinNombre')
                row['health'] = int(row['health'])
                row['regenerate_health'] = int(row['regenerate_health'])
                row['speed'] = float(row['speed'])
                row['jump'] = float(row['jump'])
                row['is_dead'] = row['is_dead'].lower() == "true"
                row['armor'] = int(row['armor'])
                row['hit_speed'] = int(row['hit_speed'])
                players.append(PlayerWithID(**row))
    except FileNotFoundError:
        pass
    return players