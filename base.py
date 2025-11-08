from __future__ import annotations

from datetime import date
from typing import Optional, Tuple

# Reusar lógica y funciones desde el paquete web para evitar duplicación.
try:
    from app.core.progression import (
        recomendar_proximo_peso,
        registrar as registrar_entrada,
        promedio_reps_semana as promedio_reps_ultima_semana,
    )
except ImportError:
    # Fallback si el paquete no está disponible (entorno minimalista CLI)
    from pathlib import Path
    import csv
    from datetime import timedelta
    from typing import Iterable, List

    CSV_HEADERS = ["ejercicio", "peso_actual", "reps", "fecha"]

    def recomendar_proximo_peso(peso_actual: float, reps: int, rpe: int) -> float:
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

    def _historial_path() -> Path:
        return Path(__file__).with_name("historial.csv")

    def _asegurar_csv_con_encabezado(path: Path) -> None:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(CSV_HEADERS)

    def registrar_entrada(ejercicio: str, peso_actual: float, reps: int, fecha: date, *, path: Optional[Path] = None) -> None:
        path = path or _historial_path()
        _asegurar_csv_con_encabezado(path)
        with path.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([ejercicio, f"{peso_actual}", reps, fecha.isoformat()])

    def _leer_historial(path: Optional[Path] = None):
        path = path or _historial_path()
        if not path.exists():
            return []
        rows = []
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows

    def _filtrar_ultima_semana(rows: Iterable[dict], ejercicio: str):
        ahora = date.today()
        hace_7 = ahora - timedelta(days=7)
        filtradas = []
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

    def promedio_reps_ultima_semana(ejercicio: str, *, path: Optional[Path] = None) -> Optional[float]:
        rows = _leer_historial(path)
        semana = _filtrar_ultima_semana(rows, ejercicio)
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


# =====================
# Cálculo de progresión
# =====================
    # Ya importado arriba o definido en fallback.


# =====================
# Entrada de usuario
# =====================
def _prompt_text(prompt: str) -> str:
    """Pide un texto al usuario asegurando que no esté vacío."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Por favor ingresa un valor.")


def _prompt_float(prompt: str) -> float:
    """Pide un número decimal al usuario."""
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            print("Ingresa un número válido (usa punto o coma para decimales).")


def _prompt_int(prompt: str, *, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    """Pide un entero al usuario, con límites opcionales."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Ingresa un número entero válido.")
            continue

        if min_value is not None and value < min_value:
            print(f"Debe ser >= {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Debe ser <= {max_value}.")
            continue
        return value


def obtener_datos_usuario() -> Tuple[str, float, int, int]:
    """Solicita al usuario ejercicio, peso, reps y RPE.

    Returns:
        Tupla (ejercicio, peso_actual, reps, rpe).
    """
    print("=== Progressive Overload Helper ===")
    ejercicio = _prompt_text("Ejercicio: ")
    peso_actual = _prompt_float("Peso actual (kg): ")
    reps = _prompt_int("Reps logradas hoy: ", min_value=1)
    rpe = _prompt_int("RPE (1-10): ", min_value=1, max_value=10)
    return ejercicio, peso_actual, reps, rpe


# =====================
# Historial CSV
# =====================
CSV_HEADERS = ["ejercicio", "peso_actual", "reps", "fecha"]


    # Reutiliza registrar_entrada y promedio_reps_ultima_semana del paquete o fallback.


# =====================
# Orquestación
# =====================
def main() -> None:
    """Flujo principal: pide datos, recomienda peso, registra historial y muestra promedio semanal."""
    ejercicio, peso_actual, reps, rpe = obtener_datos_usuario()

    nuevo_peso = recomendar_proximo_peso(peso_actual, reps, rpe)

    # Registrar historial
    hoy = date.today()
    registrar_entrada(ejercicio, peso_actual, reps, hoy)

    # Mostrar resultados
    print(f"\nPara tu próximo día de {ejercicio}:")
    print(f"Deberías usar: {nuevo_peso} kg")

    # Promedio de reps última semana para este ejercicio
    promedio = promedio_reps_ultima_semana(ejercicio)
    if promedio is None:
        print("\nAún no hay suficientes datos de la última semana para calcular un promedio de reps.")
    else:
        print(f"\nPromedio de reps en la última semana para {ejercicio}: {promedio}")


if __name__ == "__main__":
    main()
