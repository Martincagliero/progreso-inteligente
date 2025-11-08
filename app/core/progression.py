from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import csv
from typing import Iterable, List, Optional

CSV_HEADERS = ["ejercicio", "peso_actual", "reps", "fecha"]


def recomendar_proximo_peso(peso_actual: float, reps: int, rpe: int) -> float:
    """Reglas de progresión RPE + fallback reps."""
    if rpe <= 7 and reps == 10:
        return round(peso_actual + 5.0, 2)
    if rpe == 8 and reps == 10:
        return round(peso_actual + 2.5, 2)
    if rpe == 9:
        return round(peso_actual, 2)
    if rpe == 10:
        return round(peso_actual - 2.5, 2)
    if reps >= 10:
        return round(peso_actual + 2.5, 2)
    if reps >= 8:
        return round(peso_actual, 2)
    return round(peso_actual - 2.5, 2)


def historial_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "historial.csv"


def _asegurar_csv(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADERS)


def registrar(ejercicio: str, peso_actual: float, reps: int, fecha: date, *, path: Optional[Path] = None) -> None:
    path = path or historial_path()
    _asegurar_csv(path)
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([ejercicio, f"{peso_actual}", reps, fecha.isoformat()])


def _leer(path: Optional[Path] = None) -> List[dict]:
    path = path or historial_path()
    if not path.exists():
        return []
    rows: List[dict] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def _filtrar_semana(rows: Iterable[dict], ejercicio: str) -> List[dict]:
    hoy = date.today()
    hace_7 = hoy - timedelta(days=7)
    filtradas: List[dict] = []
    for r in rows:
        if r.get("ejercicio") != ejercicio:
            continue
        try:
            f = date.fromisoformat(r.get("fecha", ""))
        except Exception:
            continue
        if f >= hace_7:
            filtradas.append(r)
    return filtradas


def promedio_reps_semana(ejercicio: str, *, path: Optional[Path] = None) -> Optional[float]:
    rows = _leer(path)
    semana = _filtrar_semana(rows, ejercicio)
    if not semana:
        return None
    total = 0
    count = 0
    for r in semana:
        try:
            total += int(r.get("reps", 0))
            count += 1
        except ValueError:
            continue
    if count == 0:
        return None
    return round(total / count, 2)
