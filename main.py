from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from models import Player, PlayerWithID, Enemy, EnemyWithID
from operations.operations_player import (
    read_all_players, read_one_player, create_player, update_player,
    delete_player, read_deleted_players, revive_player_by_id,
)
from operations.operations_enemy import (
    read_all_enemies, read_one_enemy, create_enemy, update_enemy,
    delete_enemy, read_deleted_enemies,
)
from utils.conection_db import get_session, init_db
from modelos.player_sql import PlayerModel
import shutil
import uvicorn
import os

app = FastAPI()

# HTML config
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ------------------ HTML Pages -------------------
@app.get("/players/html", response_class=HTMLResponse)
async def list_players_html(request: Request):
    players = read_all_players()
    return templates.TemplateResponse("listar.html", {"request": request, "players": players})

@app.get("/players/form", response_class=HTMLResponse)
async def form_player(request: Request):
    return templates.TemplateResponse("form_entidad.html", {"request": request})

@app.post("/players/form")
async def submit_player_form(
    name: str = Form(...),
    health: int = Form(...),
    armor: int = Form(...),
    is_dead: bool = Form(False),
    image: UploadFile = File(...)
):
    image_path = f"static/uploads/{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    player = Player(name=name, health=health, armor=armor, is_dead=is_dead)
    await create_player(player)
    return RedirectResponse(url="/players/html", status_code=302)

# ------------------ API REST -------------------
@app.get("/players_add/", response_model=List[PlayerWithID])
async def get_players():
    return read_all_players()

@app.get("/players/{player_id}", response_model=PlayerWithID)
async def get_player(player_id: int):
    player = read_one_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.post("/players_create/", response_model=PlayerWithID)
async def add_player(player: Player):
    return await create_player(player)

@app.put("/players/{player_id}", response_model=PlayerWithID)
async def update_player_endpoint(player_id: int, player_update: Player):
    updated_player = update_player(player_id, player_update.dict(exclude_unset=True))
    if not updated_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated_player

@app.delete("/players/{player_id}", response_model=PlayerWithID)
async def delete_player_endpoint(player_id: int):
    removed_player = delete_player(player_id)
    if not removed_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return removed_player

@app.get("/players/filter/", response_model=List[PlayerWithID])
async def filter_players(is_dead: Optional[bool] = None):
    players = read_all_players()
    if is_dead is not None:
        players = [player for player in players if player.is_dead == is_dead]
    return players

@app.get("/players/search/", response_model=List[PlayerWithID])
async def search_players_by_health(min_health: int = Query(0)):
    players = read_all_players()
    return [player for player in players if player.health >= min_health]

@app.put("/players/{player_id}/revive", response_model=PlayerWithID)
async def revive_player(player_id: int):
    player = revive_player_by_id(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.get("/players/deleted/", response_model=List[PlayerWithID])
async def get_deleted_players():
    return read_deleted_players()

# Enemies API
@app.post("/enemies/", response_model=EnemyWithID)
async def add_enemy(enemy: Enemy):
    return await create_enemy(enemy)

@app.get("/enemies/", response_model=List[EnemyWithID])
async def get_enemies():
    return read_all_enemies()

@app.get("/enemies/{enemy_id}", response_model=EnemyWithID)
async def get_enemy(enemy_id: int):
    enemy = read_one_enemy(enemy_id)
    if not enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return enemy

@app.put("/enemies/{enemy_id}", response_model=EnemyWithID)
async def update_enemy_endpoint(enemy_id: int, enemy_update: Enemy):
    updated_enemy = update_enemy(enemy_id, enemy_update.dict(exclude_unset=True))
    if not updated_enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return updated_enemy

@app.delete("/enemies/{enemy_id}", response_model=EnemyWithID)
async def delete_enemy_endpoint(enemy_id: int):
    removed_enemy = delete_enemy(enemy_id)
    if not removed_enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return removed_enemy

@app.get("/enemies/deleted/", response_model=List[EnemyWithID])
async def get_deleted_enemies():
    return read_deleted_enemies()

# Base de datos SQL
@app.get("/players_sql/")
async def get_players_sql(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(PlayerModel))
    return result.scalars().all()

# Información adicional
@app.get("/dev", response_class=HTMLResponse)
async def developer_info(request: Request):
    return templates.TemplateResponse("detalle.html", {"request": request, "info": "Desarrollador: Tu nombre"})

@app.get("/plan", response_class=HTMLResponse)
async def planning_info(request: Request):
    return templates.TemplateResponse("detalle.html", {"request": request, "info": "Planeación del proyecto..."})

@app.get("/design", response_class=HTMLResponse)
async def design_info(request: Request):
    return templates.TemplateResponse("detalle.html", {"request": request, "info": "Diseño de interfaz 2D..."})

@app.get("/goal", response_class=HTMLResponse)
async def project_goal(request: Request):
    return templates.TemplateResponse("detalle.html", {"request": request, "info": "Objetivo del proyecto: Crear videojuego 2D interactivo."})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
