from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional


class FoodItem(BaseModel):
    nombre: str
    kcal_100: float
    prot_100: float
    carb_100: float
    grasa_100: float


class FoodCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=60)
    kcal_100: float = Field(gt=0)
    prot_100: float = Field(ge=0)
    carb_100: float = Field(ge=0)
    grasa_100: float = Field(ge=0)


class MealInput(BaseModel):
    alimento: str = Field(min_length=1)
    cantidad_g: float = Field(gt=0)
    fecha: Optional[str] = None  # ISO yyyy-mm-dd (opcional)
    # Opcional: macros por 100g para comidas personalizadas (no se guardan en alimentos.csv)
    kcal_100: Optional[float] = Field(default=None, gt=0)
    prot_100: Optional[float] = Field(default=None, ge=0)
    carb_100: Optional[float] = Field(default=None, ge=0)
    grasa_100: Optional[float] = Field(default=None, ge=0)


class MealEntry(BaseModel):
    id: str
    fecha: str
    alimento: str
    cantidad_g: float
    kcal: float
    prot: float
    carb: float
    grasa: float


class DaySummary(BaseModel):
    fecha: str
    kcal: float
    prot: float
    carb: float
    grasa: float
    comidas: List[MealEntry]


class ProductInfo(BaseModel):
    nombre: str
    marca: Optional[str] = None
    barcode: Optional[str] = None
    kcal_100: float
    prot_100: float
    carb_100: float
    grasa_100: float
