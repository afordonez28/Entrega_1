from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Enemy(BaseModel):
    name: str
    speed: float
    jump: float
    hit_speed: int
    health: int
    type: str
    spawn: float
    probability_spawn: float
    image: str

class Player(BaseModel):
    name: str
    health: int
    regenerate_health: int
    speed: float
    jump: float
    is_dead: bool
    armor: int
    hit_speed: int
    image: str

# In-memory DB
enemies_db: List[Enemy] = []
players_db: List[Player] = []

# Histórico de eliminados
deleted_enemies: List[Enemy] = []
deleted_players: List[Player] = []

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/players", response_class=HTMLResponse)
def players_page(request: Request):
    return templates.TemplateResponse("players.html", {"request": request})

@app.get("/enemies", response_class=HTMLResponse)
def enemies_page(request: Request):
    return templates.TemplateResponse("enemies.html", {"request": request})

@app.get("/stats", response_class=HTMLResponse)
def stats_page(request: Request):
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "total_players": len(players_db),
            "total_enemies": len(enemies_db),
        }
    )

@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# --- API endpoints ---

@app.get("/api/players/")
def get_players():
    return players_db

@app.post("/api/players/")
def create_player(player: Player):
    players_db.append(player)
    return {"message": "Jugador creado"}

@app.put("/api/players/{idx}")
def update_player(idx: int, player: Player):
    if 0 <= idx < len(players_db):
        players_db[idx] = player
        return {"message": "Jugador actualizado"}
    else:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

@app.delete("/api/players/")
def delete_all_players():
    global deleted_players
    deleted_players.extend(players_db.copy())
    players_db.clear()
    return {"message": "Todos los jugadores eliminados"}

@app.get("/api/players/history/")
def get_deleted_players():
    return deleted_players

@app.get("/api/enemies/")
def get_enemies():
    return enemies_db

@app.post("/api/enemies/")
def create_enemy(enemy: Enemy):
    enemies_db.append(enemy)
    return {"message": "Enemigo creado"}

@app.put("/api/enemies/{idx}")
def update_enemy(idx: int, enemy: Enemy):
    if 0 <= idx < len(enemies_db):
        enemies_db[idx] = enemy
        return {"message": "Enemigo actualizado"}
    else:
        raise HTTPException(status_code=404, detail="Enemigo no encontrado")

@app.delete("/api/enemies/")
def delete_all_enemies():
    global deleted_enemies
    deleted_enemies.extend(enemies_db.copy())
    enemies_db.clear()
    return {"message": "Todos los enemigos eliminados"}

@app.get("/api/enemies/history/")
def get_deleted_enemies():
    return deleted_enemies

@app.get("/api/stats/")
def get_stats():
    return {
        "total_players": len(players_db),
        "total_enemies": len(enemies_db),
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)