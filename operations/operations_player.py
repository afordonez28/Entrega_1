import csv
from typing import List, Optional
from models import Player, PlayerWithID
from fastapi import APIRouter, HTTPException
router = APIRouter()

PLAYER_CSV = "data/players.csv"
DELETED_PLAYER_CSV = "data/deleted_players.csv"
PLAYER_FIELDS = ["id", "name", "health", "regenerate_health", "speed", "jump", "is_dead", "armor", "hit_speed"]

#epoints router:
@router.get("/players", response_model=List[PlayerWithID])
async def get_players():
    return await read_all_players()

@router.get("/players/{player_id}", response_model=PlayerWithID)
async def get_player(player_id: int):
    player = await read_one_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.post("/players", response_model=PlayerWithID)
async def post_player(player: Player):
    return await create_player(player)

@router.put("/players/{player_id}", response_model=PlayerWithID)
async def put_player(player_id: int, player_update: dict):
    updated = await update_player(player_id, player_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated

@router.delete("/players/{player_id}", response_model=PlayerWithID)
async def delete_single_player(player_id: int):
    deleted = await delete_player(player_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Player not found")
    return deleted

@router.delete("/players", response_model=List[PlayerWithID])
async def delete_all():
    return await delete_all_players()

@router.get("/players/deleted", response_model=List[PlayerWithID])
async def get_deleted_players():
    return await read_deleted_players()

@router.put("/players/revive/{player_id}", response_model=PlayerWithID)
async def revive(player_id: int):
    revived = await revive_player_by_id(player_id)
    if not revived:
        raise HTTPException(status_code=404, detail="Player not found")
    return revived


#endpoints
async def read_all_players() -> List[PlayerWithID]:
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

async def delete_all_players() -> List[PlayerWithID]:
    players = await read_all_players()
    for player in players:
        await append_to_deleted_players(player)
    await write_players_to_csv([])  # Vacía el archivo
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
    player_with_id = PlayerWithID(id=new_id, **player.dict())
    players.append(player_with_id)
    await write_players_to_csv(players)
    return player_with_id


async def update_player(player_id: int, player_update: dict) -> Optional[PlayerWithID]:
    players = await read_all_players()
    updated_player = None
    for player in players:
        if player.id == player_id:
            for key, value in player_update.items():
                setattr(player, key, value)
            updated_player = player
            break
    if updated_player:
        await write_players_to_csv(players)
        return updated_player
    return None


async def delete_player(player_id: int) -> Optional[PlayerWithID]:
    players = await read_all_players()
    removed_player = None
    new_players = []
    for player in players:
        if player.id == player_id:
            removed_player = player
        else:
            new_players.append(player)
    if removed_player:
        await write_players_to_csv(new_players)
        await append_to_deleted_players(removed_player)
        return removed_player
    return None


async def revive_player_by_id(player_id: int) -> Optional[PlayerWithID]:
    players = await read_all_players()
    for player in players:
        if player.id == player_id:
            player.is_dead = False
            await write_players_to_csv(players)
            return player
    return None


async def write_players_to_csv(players: List[PlayerWithID]):
    with open(PLAYER_CSV, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=PLAYER_FIELDS)
        writer.writeheader()
        for player in players:
            player_dict = player.dict()
            player_dict["is_dead"] = str(player_dict["is_dead"])  # Asegura que se guarde como "True"/"False"
            writer.writerow(player_dict)


async def append_to_deleted_players(player: PlayerWithID):
    try:
        with open(DELETED_PLAYER_CSV, mode="a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=PLAYER_FIELDS)
            if csvfile.tell() == 0:  # Si el archivo está vacío, escribe encabezado
                writer.writeheader()
            player_dict = player.dict()
            player_dict["is_dead"] = str(player_dict["is_dead"])
            writer.writerow(player_dict)
    except Exception as e:
        print(f"Error writing to deleted_players.csv: {e}")


async def read_deleted_players() -> List[PlayerWithID]:
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
