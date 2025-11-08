from __future__ import annotations

import os
import sys
from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Permite ejecutar como script: python app/main.py
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.api.models import SessionInput, SessionOutput
from app.core.progression import (
    recomendar_proximo_peso,
    registrar,
    promedio_reps_semana,
)

app = FastAPI(title="Progressive Overload Helper API", version="0.1.0")

# CORS liberal para pruebas locales y despliegues simples
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir frontend estático simple
app.mount("/static", StaticFiles(directory="app/frontend"), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/session", response_model=SessionOutput)
async def post_session(data: SessionInput):
    proximo = recomendar_proximo_peso(data.peso_actual, data.reps, data.rpe)
    registrar(data.ejercicio, data.peso_actual, data.reps, date.today())
    promedio = promedio_reps_semana(data.ejercicio)
    return SessionOutput(
        ejercicio=data.ejercicio,
        peso_actual=data.peso_actual,
        reps=data.reps,
        rpe=data.rpe,
        proximo_peso=proximo,
        promedio_reps_semana=promedio,
    )


@app.get("/", response_class=HTMLResponse)
async def index():
    # Redirigir a frontend estático minimalista
    with open("app/frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


if __name__ == "__main__":
    # Permite: python app/main.py
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
