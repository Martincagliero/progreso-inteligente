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
from app.api.nutrition_models import (
    FoodItem,
    MealInput,
    MealEntry,
    DaySummary,
)
from app.core.nutrition import (
    search_foods,
    add_meal,
    day_summary,
    remove_meal,
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


# =====================
# Nutrición (Comidas + Macros)
# =====================
@app.get("/foods", response_model=list[FoodItem])
async def get_foods(query: str | None = None):
    items = search_foods(query)
    # Convert dicts to Pydantic models
    return [FoodItem(**it) for it in items]


# Eliminado: persistencia de alimentos personalizados


@app.post("/meal")
async def post_meal(data: MealInput):
    # Parse optional fecha ISO (yyyy-mm-dd)
    fecha_obj = None
    if data.fecha:
        try:
            fecha_obj = date.fromisoformat(data.fecha)
        except Exception:
            return {"ok": False, "error": "fecha inválida (use YYYY-MM-DD)"}
    try:
        entry = add_meal(
            data.alimento, 
            float(data.cantidad_g), 
            fecha_obj,
            # Pasar macros opcionales para alimentos personalizados
            kcal_100=data.kcal_100,
            prot_100=data.prot_100,
            carb_100=data.carb_100,
            grasa_100=data.grasa_100
        )
    except ValueError as ve:
        return {"ok": False, "error": str(ve)}
    except LookupError:
        return {"ok": False, "error": "alimento no encontrado"}
    return {"ok": True, "entry": MealEntry(**entry)}


@app.get("/day-summary", response_model=DaySummary)
async def get_day_summary(fecha: str | None = None):
    fecha_obj = None
    if fecha:
        try:
            fecha_obj = date.fromisoformat(fecha)
        except Exception:
            # Si fecha inválida, usar hoy
            fecha_obj = date.today()
    summary = day_summary(fecha_obj)
    # Convert dict to Pydantic model with nested items
    meals = [MealEntry(**m) for m in summary.get("comidas", [])]
    return DaySummary(
        fecha=summary["fecha"],
        kcal=summary["kcal"],
        prot=summary["prot"],
        carb=summary["carb"],
        grasa=summary["grasa"],
        comidas=meals,
    )


@app.delete("/meal/{meal_id}")
async def delete_meal(meal_id: str):
    try:
        ok = remove_meal(meal_id)
        return {"ok": ok}
    except Exception:
        return {"ok": False}


if __name__ == "__main__":
    # Permite: python app/main.py
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
