from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class SessionInput(BaseModel):
    ejercicio: str = Field(min_length=1)
    peso_actual: float = Field(gt=0)
    reps: int = Field(ge=1)
    rpe: int = Field(ge=1, le=10)


class SessionOutput(BaseModel):
    ejercicio: str
    peso_actual: float
    reps: int
    rpe: int
    proximo_peso: float
    promedio_reps_semana: Optional[float]
