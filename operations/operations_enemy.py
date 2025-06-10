import csv
from typing import List, Optional
from models import Enemy, EnemyWithID

ENEMY_CSV = "data/enemies.csv"
DELETED_ENEMY_CSV = "data/deleted_enemies.csv"
ENEMY_FIELDS = ["id", "name", "speed", "jump", "hit_speed", "health", "type", "spawn", "probability_spawn"]

# -----------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------

def write_enemies_to_csv(enemies: List[EnemyWithID]):
    with open(ENEMY_CSV, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=ENEMY_FIELDS)
        writer.writeheader()
        for enemy in enemies:
            writer.writerow(enemy.dict())

def append_to_deleted_enemies(enemy: EnemyWithID):
    try:
        with open(DELETED_ENEMY_CSV, mode="a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ENEMY_FIELDS)
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(enemy.dict())
    except Exception as e:
        print(f"Error writing to deleted_enemies.csv: {e}")

# -----------------------------------------
# LECTURAS
# -----------------------------------------

def read_all_enemies() -> List[EnemyWithID]:
    enemies = []
    try:
        with open(ENEMY_CSV, mode="r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['id'] = int(row['id'])
                row['name'] = row.get('name', 'SinNombre')
                row['speed'] = float(row['speed'])
                row['jump'] = float(row['jump'])
                row['hit_speed'] = int(row['hit_speed'])
                row['health'] = int(row['health'])
                row['spawn'] = float(row['spawn'])
                row['probability_spawn'] = float(row['probability_spawn'])
                row['type'] = row.get('type', 'unknown')
                enemies.append(EnemyWithID(**row))
    except FileNotFoundError:
        pass
    return enemies

def read_deleted_enemies() -> List[EnemyWithID]:
    enemies = []
    try:
        with open(DELETED_ENEMY_CSV, mode="r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['id'] = int(row['id'])
                row['name'] = row.get('name', 'SinNombre')
                row['speed'] = float(row['speed'])
                row['jump'] = float(row['jump'])
                row['hit_speed'] = int(row['hit_speed'])
                row['health'] = int(row['health'])
                row['spawn'] = float(row['spawn'])
                row['probability_spawn'] = float(row['probability_spawn'])
                row['type'] = row.get('type', 'unknown')
                enemies.append(EnemyWithID(**row))
    except FileNotFoundError:
        pass
    return enemies

def read_one_enemy(enemy_id: int) -> Optional[EnemyWithID]:
    enemies = read_all_enemies()
    for enemy in enemies:
        if enemy.id == enemy_id:
            return enemy
    return None

# -----------------------------------------
# CRUD PRINCIPALES
# -----------------------------------------

async def create_enemy(enemy: Enemy) -> EnemyWithID:
    enemies = read_all_enemies()
    new_id = max([e.id for e in enemies], default=0) + 1
    enemy_with_id = EnemyWithID(id=new_id, **enemy.dict())
    enemies.append(enemy_with_id)
    write_enemies_to_csv(enemies)
    return enemy_with_id

async def update_enemy(enemy_id: int, enemy_update: dict) -> Optional[EnemyWithID]:
    enemies = read_all_enemies()
    updated_enemy = None
    for enemy in enemies:
        if enemy.id == enemy_id:
            for key, value in enemy_update.items():
                setattr(enemy, key, value)
            updated_enemy = enemy
            break
    if updated_enemy:
        write_enemies_to_csv(enemies)
        return updated_enemy
    return None

async def delete_enemy(enemy_id: int) -> Optional[EnemyWithID]:
    enemies = read_all_enemies()
    removed_enemy = None
    new_enemies = []
    for enemy in enemies:
        if enemy.id == enemy_id:
            removed_enemy = enemy
        else:
            new_enemies.append(enemy)
    if removed_enemy:
        write_enemies_to_csv(new_enemies)
        append_to_deleted_enemies(removed_enemy)
        return removed_enemy
    return None
