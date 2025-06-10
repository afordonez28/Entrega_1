from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from models import Player, PlayerWithID, Enemy, EnemyWithID
from operations.operations_player import (
    get_all_players, get_player, create_player, update_player,
    delete_player, get_deleted_players, restore_player,
    delete_all_players as op_delete_all_players
)

from operations.operations_enemy import (
    read_all_enemies, read_one_enemy, create_enemy, update_enemy,
    delete_enemy, read_deleted_enemies, delete_all_enemies as op_delete_all_enemies
)
from utils.conection_db import get_session, init_db
from modelos.player_sql import PlayerModel
from operations.operations_player import router as player_router
import shutil
import uvicorn
import os



app = FastAPI()
app.include_router(player_router, prefix="/api/players", tags=["Players"])

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# HTML interfaces
@app.get("/players/created/{player_id}", response_class=HTMLResponse)
async def show_created_player(request: Request, player_id: int):
    player = await read_one_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    imagen = f"/static/uploads/{player.name.lower()}.png"
    return templates.TemplateResponse("personaje_creado.html", {"request": request, "player": player, "imagen": imagen})

@app.get("/players/form", response_class=HTMLResponse)
async def form_player(request: Request):
    return templates.TemplateResponse("form_entidad.html", {"request": request})

@app.get("/players/html", response_class=HTMLResponse)
async def list_players_html(request: Request):
    players = await read_all_players()
    imagenes = ["/static/uploads/personaje_1.png",
                "/static/uploads/personaje_2.png",
                "/static/uploads/personaje_3.png",
                "/static/uploads/personaje_4.png"]
    return templates.TemplateResponse("listar.html", {"request": request, "elementos": players, "imagenes": imagenes, "titulo": "Personajes"})

@app.get("/enemies/html", response_class=HTMLResponse)
async def list_enemies_html(request: Request):
    enemies = await read_all_enemies()
    imagenes = ["/static/uploads/enemie_1.png", "/static/uploads/enemie_2.png"]
    return templates.TemplateResponse("listar.html", {"request": request, "elementos": enemies, "imagenes": imagenes, "titulo": "Enemigos"})

@app.post("/players/form")
async def submit_player_form(
    name: str = Form(...), health: int = Form(...), armor: int = Form(...),
    is_dead: bool = Form(False), regenerate_health: int = Form(...),
    speed: float = Form(...), jump: float = Form(...), hit_speed: int = Form(...),
    image: UploadFile = File(...)
):
    image_path = f"static/uploads/{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    player = Player(name=name, health=health, armor=armor, is_dead=is_dead,
                    regenerate_health=regenerate_health, speed=speed,
                    jump=jump, hit_speed=hit_speed)
    new_player = await create_player(player)
    return RedirectResponse(url=f"/players/created/{new_player.id}", status_code=302)

@app.get("/enemies/form", response_class=HTMLResponse)
async def form_enemy(request: Request):
    return templates.TemplateResponse("form_enemigo.html", {"request": request})

@app.post("/enemies/form")
async def submit_enemy_form(
    name: str = Form(...), type: str = Form(...),
    health: int = Form(...), speed: float = Form(...),
    jump: float = Form(...), hit_speed: int = Form(...),
    spawn: float = Form(...), probability_spawn: float = Form(...)
):
    enemy = Enemy(name=name, type=type, health=health, speed=speed,
                  jump=jump, hit_speed=hit_speed,
                  spawn=spawn, probability_spawn=probability_spawn)
    await create_enemy(enemy)
    return RedirectResponse(url="/enemies/html", status_code=302)

# Estadísticas y historial
@app.get("/estadisticas", response_class=HTMLResponse)
async def estadisticas(request: Request):
    jugadores = await read_all_players()
    enemigos = await read_all_enemies()
    return templates.TemplateResponse("estadisticas.html", {"request": request, "jugadores": jugadores, "enemigos": enemigos})

@app.get("/historial", response_class=HTMLResponse)
async def historial(request: Request):
    historial = await read_deleted_players()
    return templates.TemplateResponse("historial.html", {"request": request, "historial": historial})

@app.get("/historial_enemigos", response_class=HTMLResponse)
async def historial_enemigos(request: Request):
    historial = await read_deleted_enemies()
    return templates.TemplateResponse("historial.html", {"request": request, "historial": historial, "titulo": "☠️ Enemigos Eliminados"})

# Info pages
@app.get("/desarrollador", response_class=HTMLResponse)
async def info_desarrollador(request: Request):
    contenido = """
    <ul>
      <li><strong>Nombre:</strong> Andrés Felipe Ordóñez</li>
      <li><strong>Código:</strong> 67001128</li>
      <li><strong>Correo:</strong> afordonez28@ucatolica.edu.co</li>
      <li><strong>Semestre:</strong> Séptimo</li>
    </ul>
    """
    return templates.TemplateResponse("detalle.html", {"request": request, "titulo": "👨‍💻 Desarrollador", "info": contenido})

@app.get("/objetivo", response_class=HTMLResponse)
async def objetivo_proyecto(request: Request):
    contenido = "<p>Crear interfaz gráfica 2D en Godot, fomentando creatividad...</p>"
    return templates.TemplateResponse("detalle.html", {"request": request, "titulo": "🎯 Objetivo del Proyecto", "info": contenido})

@app.get("/planeacion", response_class=HTMLResponse)
async def planeacion(request: Request):
    contenido = "<p>Fase de planeación: requisitos, diseño CRUD, gráficos...</p>"
    return templates.TemplateResponse("detalle.html", {"request": request, "titulo": "📋 Planeación", "info": contenido})

@app.get("/diseno", response_class=HTMLResponse)
async def diseno(request: Request):
    contenido = "<p>Estética PixelArt, navegación sencilla y estilo RPG...</p>"
    return templates.TemplateResponse("detalle.html", {"request": request, "titulo": "🎨 Diseño", "info": contenido})

@app.get("/acerca", response_class=HTMLResponse)
async def acerca(request: Request):
    return templates.TemplateResponse("acerca.html", {"request": request})

@app.get("/error_demo", response_class=HTMLResponse)
async def error_demo(request: Request):
    return templates.TemplateResponse("error.html", {"request": request, "codigo": 404, "mensaje": "Página no encontrada"})

# API REST - Players
@app.get("/players_add/", response_model=List[PlayerWithID])
async def get_players():
    return await read_all_players()

@app.post("/players_create/", response_model=PlayerWithID)
async def add_player(player: Player):
    return await create_player(player)

@app.get("/players/{player_id}", response_model=PlayerWithID)
async def get_player(player_id: int):
    player = await read_one_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.put("/players/{player_id}", response_model=PlayerWithID)
async def update_player_endpoint(player_id: int, player_update: Player):
    updated = await update_player(player_id, player_update.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated

@app.delete("/players/{player_id}", response_model=PlayerWithID)
async def delete_player_endpoint(player_id: int):
    removed = await delete_player(player_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Player not found")
    return removed

@app.get("/players/filter/", response_model=List[PlayerWithID])
async def filter_players(is_dead: Optional[bool] = None):
    players = await read_all_players()
    return [p for p in players if is_dead is None or p.is_dead == is_dead]

@app.get("/players/search/", response_model=List[PlayerWithID])
async def search_players_by_health(min_health: int = Query(0)):
    players = await read_all_players()
    return [p for p in players if p.health >= min_health]

@app.put("/players/{player_id}/revive", response_model=PlayerWithID)
async def revive_player(player_id: int):
    player = await revive_player_by_id(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.get("/players/deleted/", response_model=List[PlayerWithID])
async def get_deleted_players():
    return await read_deleted_players()

@app.delete("/players/delete_all", response_model=List[PlayerWithID])
async def delete_all_players_endpoint(confirm: bool = Query(False, description="Confirm deletion")):
    if not confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to delete all players")
    return await op_delete_all_players()

# API REST - Enemies
@app.post("/enemies/", response_model=EnemyWithID)
async def add_enemy(enemy: Enemy):
    return await create_enemy(enemy)

@app.get("/enemies/", response_model=List[EnemyWithID])
async def get_enemies():
    return await read_all_enemies()

@app.get("/enemies/{enemy_id}", response_model=EnemyWithID)
async def get_enemy(enemy_id: int):
    enemy = await read_one_enemy(enemy_id)
    if not enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return enemy

@app.put("/enemies/{enemy_id}", response_model=EnemyWithID)
async def update_enemy_endpoint(enemy_id: int, enemy_update: Enemy):
    updated = await update_enemy(enemy_id, enemy_update.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return updated

@app.delete("/enemies/{enemy_id}", response_model=EnemyWithID)
async def delete_enemy_endpoint(enemy_id: int):
    removed = await delete_enemy(enemy_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return removed

@app.get("/enemies/deleted/", response_model=List[EnemyWithID])
async def get_deleted_enemies():
    return await read_deleted_enemies()

@app.delete("/enemies/delete_all", response_model=List[EnemyWithID])
async def delete_all_enemies_endpoint(confirm: bool = Query(False, description="Confirm deletion")):
    if not confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to delete all enemies")
    return await op_delete_all_enemies()

# SQL players
@app.get("/players_sql/")
async def get_players_sql(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(PlayerModel))
    return result.scalars().all()

# Temporary players
@app.post("/players/temp_create/", response_model=PlayerWithID)
async def add_temp_player(player: Player):
    return await create_temporary_player(player)

@app.get("/players/temp_all/", response_model=List[PlayerWithID])
async def get_temp_players():
    return await read_all_temporary_players()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
