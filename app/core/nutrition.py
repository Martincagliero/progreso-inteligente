from __future__ import annotations

import csv
import uuid
import httpx
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional, Dict

FOODS_HEADERS = ["nombre", "kcal_100", "prot_100", "carb_100", "grasa_100"]
MEALS_HEADERS = ["id", "fecha", "alimento", "cantidad_g", "kcal", "prot", "carb", "grasa"]


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def foods_path() -> Path:
    return _project_root() / "alimentos.csv"


def meals_path() -> Path:
    return _project_root() / "comidas.csv"


def _ensure_csv(path: Path, headers: List[str]) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)


def _upgrade_meals_csv_if_needed() -> None:
    """Ensure comidas.csv exists and includes an 'id' column; migrate if needed."""
    path = meals_path()
    if not path.exists():
        _ensure_csv(path, MEALS_HEADERS)
        return
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if "id" in fieldnames:
            return
        rows = list(reader)
    # Rewrite file with id column
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(MEALS_HEADERS)
        for row in rows:
            try:
                fecha = row.get("fecha") or ""
                alimento = row.get("alimento") or ""
                cantidad_g = float(row.get("cantidad_g") or 0)
                kcal = float(row.get("kcal") or 0)
                prot = float(row.get("prot") or 0)
                carb = float(row.get("carb") or 0)
                grasa = float(row.get("grasa") or 0)
            except Exception:
                # Skip malformed
                continue
            w.writerow([
                str(uuid.uuid4()), fecha, alimento, cantidad_g, kcal, prot, carb, grasa
            ])


@dataclass
class Food:
    nombre: str
    kcal_100: float
    prot_100: float
    carb_100: float
    grasa_100: float

    @staticmethod
    def from_row(row: Dict[str, str]) -> "Food":
        return Food(
            nombre=row["nombre"],
            kcal_100=float(row["kcal_100"]),
            prot_100=float(row["prot_100"]),
            carb_100=float(row["carb_100"]),
            grasa_100=float(row["grasa_100"]),
        )

    def to_dict(self) -> Dict[str, float | str]:
        return {
            "nombre": self.nombre,
            "kcal_100": self.kcal_100,
            "prot_100": self.prot_100,
            "carb_100": self.carb_100,
            "grasa_100": self.grasa_100,
        }


def seed_foods_if_missing() -> None:
    """Create alimentos.csv with common foods if missing."""
    path = foods_path()
    if path.exists():
        return
    _ensure_csv(path, FOODS_HEADERS)
    seed = [
        ("Pechuga de pollo", 165, 31, 0, 3.6),
        ("Arroz blanco cocido", 130, 2.7, 28, 0.3),
        ("Avena", 389, 16.9, 66.3, 6.9),
        ("Huevo (entero)", 155, 13, 1.1, 11),
        ("Leche entera", 61, 3.2, 4.8, 3.3),
        ("Pan blanco", 265, 9, 49, 3.2),
        ("Pasta cocida", 157, 5.8, 30.9, 0.9),
        ("Aceite de oliva", 884, 0, 0, 100),
        ("Manzana", 52, 0.3, 14, 0.2),
        ("Banana", 89, 1.1, 23, 0.3),
        ("Yogur natural", 61, 3.5, 4.7, 3.3),
    ]
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for r in seed:
            w.writerow([r[0], r[1], r[2], r[3], r[4]])


def ensure_additional_foods() -> None:
    """Append a richer set of foods if they are not already present.
    This can be called safely multiple times; it avoids duplicates by nombre (case-insensitive).
    """
    path = foods_path()
    _ensure_csv(path, FOODS_HEADERS)

    extras = [
        ("Yogur griego (descremado)", 59, 10.0, 3.6, 0.4),
        ("Batata cocida", 90, 2.0, 21.0, 0.1),
        ("Salmón", 208, 20.0, 0.0, 13.0),
        ("Atún en lata (agua)", 132, 29.0, 0.0, 1.0),
        ("Lentejas cocidas", 116, 9.0, 20.0, 0.4),
        ("Garbanzos cocidos", 164, 8.9, 27.4, 2.6),
        ("Mantequilla de maní", 588, 25.0, 20.0, 50.0),
        ("Proteína whey", 370, 90.0, 5.0, 2.0),
        ("Brócoli", 34, 2.8, 7.0, 0.4),
        ("Espinaca", 23, 2.9, 3.6, 0.4),
        ("Quinoa cocida", 120, 4.4, 21.3, 1.9),
        ("Requesón (cottage) 2%", 82, 11.0, 3.4, 2.3),
        ("Almendras", 579, 21.0, 22.0, 50.0),
        ("Arroz integral cocido", 111, 2.6, 23.0, 0.9),
        ("Palta (aguacate)", 160, 2.0, 9.0, 15.0),
    ]

    # Load existing names
    existing: set[str] = set()
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nombre = (row.get("nombre") or "").strip().lower()
            if nombre:
                existing.add(nombre)

    # Append missing extras
    to_add = [r for r in extras if r[0].strip().lower() not in existing]
    if not to_add:
        return
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for r in to_add:
            w.writerow([r[0], r[1], r[2], r[3], r[4]])


def load_foods() -> List[Food]:
    seed_foods_if_missing()
    ensure_additional_foods()
    with foods_path().open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        foods: List[Food] = []
        for row in reader:
            try:
                foods.append(Food.from_row(row))
            except Exception:
                continue
        # Lista blanca de nombres permitidos (seed + extras) para evitar mostrar alimentos ad-hoc agregados previamente
        allowed = {
            "pechuga de pollo","arroz blanco cocido","avena","huevo (entero)","leche entera","pan blanco","pasta cocida","aceite de oliva","manzana","banana","yogur natural",
            "yogur griego (descremado)","batata cocida","salmón","atún en lata (agua)","lentejas cocidas","garbanzos cocidos","mantequilla de maní","proteína whey","brócoli","espinaca","quinoa cocida","requesón (cottage) 2%","almendras","arroz integral cocido","palta (aguacate)"
        }
        return [f for f in foods if f.nombre.lower() in allowed]


def search_foods(query: Optional[str] = None, limit: int = 20) -> List[Dict[str, float | str]]:
    q = (query or "").strip().lower()
    items = [f.to_dict() for f in load_foods()]
    if not q:
        return items[:limit]
    filtered = [it for it in items if q in str(it["nombre"]).lower()]
    return filtered[:limit]


def _find_food(nombre: str) -> Optional[Food]:
    nombre_l = nombre.strip().lower()
    for f in load_foods():
        if f.nombre.lower() == nombre_l:
            return f
    return None


def _normalize_off_product(p: dict) -> Optional[dict]:
    try:
        nutr = p.get("nutriments", {})
        # kcal per 100g: prefer energy-kcal_100g, fallback convert energy_100g (kJ)
        kcal = nutr.get("energy-kcal_100g")
        if kcal is None and nutr.get("energy_100g") is not None:
            try:
                kcal = float(nutr.get("energy_100g")) / 4.184
            except Exception:
                kcal = None
        prot = nutr.get("proteins_100g")
        carb = nutr.get("carbohydrates_100g")
        grasa = nutr.get("fat_100g")
        if None in (kcal, prot, carb, grasa):
            return None
        name = (p.get("product_name") or p.get("generic_name") or "").strip()
        brand = (p.get("brands") or "").split(",")[0].strip() or None
        code = p.get("code") or p.get("_id")
        return {
            "nombre": name or (brand or "Producto") ,
            "marca": brand,
            "barcode": code,
            "kcal_100": round(float(kcal), 2),
            "prot_100": round(float(prot), 2),
            "carb_100": round(float(carb), 2),
            "grasa_100": round(float(grasa), 2),
        }
    except Exception:
        return None


def off_lookup_barcode(barcode: str) -> Optional[dict]:
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        resp = httpx.get(url, timeout=8.0)
        if resp.status_code != 200:
            return None
        data = resp.json()
        prod = data.get("product")
        if not prod:
            return None
        return _normalize_off_product(prod)
    except Exception:
        return None


def off_search(query: str, limit: int = 5) -> list[dict]:
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": max(5, limit * 2),
    }
    try:
        resp = httpx.get("https://world.openfoodfacts.org/cgi/search.pl", params=params, timeout=8.0)
        if resp.status_code != 200:
            return []
        products = resp.json().get("products", [])
        out: list[dict] = []
        for p in products:
            norm = _normalize_off_product(p)
            if norm:
                out.append(norm)
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []


def add_or_update_food(nombre: str, kcal_100: float, prot_100: float, carb_100: float, grasa_100: float) -> Dict[str, float | str]:
    """Add a new food to alimentos.csv or update it if exists (matched by nombre, case-insensitive)."""
    if not nombre or len(nombre.strip()) < 2:
        raise ValueError("nombre inválido")
    if kcal_100 <= 0 or prot_100 < 0 or carb_100 < 0 or grasa_100 < 0:
        raise ValueError("valores nutricionales inválidos")

    path = foods_path()
    _ensure_csv(path, FOODS_HEADERS)

    nombre_key = nombre.strip().lower()
    rows: list[dict] = []
    updated = False
    if path.exists():
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row.get("nombre") or "").strip().lower() == nombre_key:
                    row = {
                        "nombre": nombre.strip(),
                        "kcal_100": str(kcal_100),
                        "prot_100": str(prot_100),
                        "carb_100": str(carb_100),
                        "grasa_100": str(grasa_100),
                    }
                    updated = True
                rows.append(row)

    if not updated:
        rows.append({
            "nombre": nombre.strip(),
            "kcal_100": str(kcal_100),
            "prot_100": str(prot_100),
            "carb_100": str(carb_100),
            "grasa_100": str(grasa_100),
        })

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FOODS_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return {
        "nombre": nombre.strip(),
        "kcal_100": float(kcal_100),
        "prot_100": float(prot_100),
        "carb_100": float(carb_100),
        "grasa_100": float(grasa_100),
        "updated": updated,
    }


def add_meal(
    alimento: str, 
    cantidad_g: float, 
    fecha: Optional[date] = None,
    # Parámetros opcionales para alimentos personalizados (no en CSV)
    kcal_100: Optional[float] = None,
    prot_100: Optional[float] = None,
    carb_100: Optional[float] = None,
    grasa_100: Optional[float] = None
) -> Dict[str, float | str]:
    if cantidad_g <= 0:
        raise ValueError("cantidad_g debe ser > 0")
    
    # Si vienen macros custom, usar esos valores; sino buscar en CSV
    if all([kcal_100 is not None, prot_100 is not None, carb_100 is not None, grasa_100 is not None]):
        # Usar macros proporcionados (alimento personalizado)
        food = Food(
            nombre=alimento,
            kcal_100=kcal_100,
            prot_100=prot_100,
            carb_100=carb_100,
            grasa_100=grasa_100
        )
    else:
        # Buscar en alimentos base
        food = _find_food(alimento)
        if not food:
            raise LookupError("alimento no encontrado")
    
    fecha = fecha or date.today()
    factor = cantidad_g / 100.0
    kcal = round(food.kcal_100 * factor, 2)
    prot = round(food.prot_100 * factor, 2)
    carb = round(food.carb_100 * factor, 2)
    grasa = round(food.grasa_100 * factor, 2)


    path = meals_path()
    _upgrade_meals_csv_if_needed()
    meal_id = str(uuid.uuid4())
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([meal_id, fecha.isoformat(), food.nombre, cantidad_g, kcal, prot, carb, grasa])

    return {
        "id": meal_id,
        "fecha": fecha.isoformat(),
        "alimento": food.nombre,
        "cantidad_g": cantidad_g,
        "kcal": kcal,
        "prot": prot,
        "carb": carb,
        "grasa": grasa,
    }


def day_summary(fecha: Optional[date] = None) -> Dict[str, float | str | List[Dict[str, float | str]]]:
    fecha = fecha or date.today()
    path = meals_path()
    if not path.exists():
        return {"fecha": fecha.isoformat(), "kcal": 0.0, "prot": 0.0, "carb": 0.0, "grasa": 0.0, "comidas": []}

    total_kcal = total_prot = total_carb = total_grasa = 0.0
    comidas: List[Dict[str, float | str]] = []

    _upgrade_meals_csv_if_needed()
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("fecha") != fecha.isoformat():
                continue
            try:
                kcal = float(row["kcal"])
                prot = float(row["prot"])
                carb = float(row["carb"])
                grasa = float(row["grasa"])
                cantidad = float(row["cantidad_g"])
            except Exception:
                continue
            total_kcal += kcal
            total_prot += prot
            total_carb += carb
            total_grasa += grasa
            comidas.append({
                "id": row.get("id"),
                "fecha": row.get("fecha", fecha.isoformat()),
                "alimento": row.get("alimento", ""),
                "cantidad_g": cantidad,
                "kcal": kcal,
                "prot": prot,
                "carb": carb,
                "grasa": grasa,
            })

    return {
        "fecha": fecha.isoformat(),
        "kcal": round(total_kcal, 2),
        "prot": round(total_prot, 2),
        "carb": round(total_carb, 2),
        "grasa": round(total_grasa, 2),
        "comidas": comidas,
    }


def remove_meal(meal_id: str) -> bool:
    """Delete a meal by id. Returns True if a row was deleted."""
    path = meals_path()
    if not path.exists():
        return False
    _upgrade_meals_csv_if_needed()
    deleted = False
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
        headers = reader.fieldnames or MEALS_HEADERS
    kept: list[dict] = []
    for row in rows:
        if row.get("id") == meal_id:
            deleted = True
            continue
        kept.append(row)
    if not deleted:
        return False
    # Rewrite file with kept rows
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MEALS_HEADERS)
        writer.writeheader()
        for row in kept:
            writer.writerow({
                "id": row.get("id", str(uuid.uuid4())),
                "fecha": row.get("fecha", ""),
                "alimento": row.get("alimento", ""),
                "cantidad_g": row.get("cantidad_g", 0),
                "kcal": row.get("kcal", 0),
                "prot": row.get("prot", 0),
                "carb": row.get("carb", 0),
                "grasa": row.get("grasa", 0),
            })
    return True
