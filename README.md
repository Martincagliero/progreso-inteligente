# Progressive Overload Helper

Single-developer fitness side-project: a CLI + minimal web API that recommends next training weight using reps + RPE, and keeps a lightweight weekly history. Built to showcase clean Python, simple data persistence, and an easy path to a future Render deployment.

## Features

CLI & API both share the same core logic:
- Input: ejercicio, peso actual (kg), reps, RPE (1–10).
- Next-weight rules:
  - RPE ≤ 7 & 10 reps → +5.0 kg
  - RPE = 8 & 10 reps → +2.5 kg
  - RPE = 9 → mantener
  - RPE = 10 → −2.5 kg
  - Fallback (6–10 reps model): 10+ → +2.5 / 8–9 → mantener / <8 → −2.5
- Historial plano en `historial.csv` (append). Muestra promedio de reps últimos 7 días por ejercicio.
- API FastAPI (`/session`, `/health`) + frontend estático básico.

## Run (CLI)

Requiere Python 3.8+.

```powershell
python .\base.py
```

## Run (API local)

Instala dependencias y levanta el servidor.

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Visita: http://localhost:8000 para el formulario, o prueba `POST /session` con JSON.

## Concepto: Progressive Overload con RPE

Progressive Overload = incremento gradual del estímulo. El uso de RPE agrega autoregulación: días fáciles → saltos mayores; días duros → mantener o bajar; evita estancamientos y sobrecarga subjetiva.

## Arquitectura breve

- `app/core/progression.py`: lógica desacoplada (recomendación + historial).
- `app/main.py`: capa API FastAPI.
- `app/frontend/index.html`: UI mínima vanilla JS.
- `base.py`: CLI legacy que reutiliza el core.

Esto permite extender a: base de datos real, auth, dashboards.

## Deploy en Render (gratis)

1. **Sube tu código a GitHub**:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit: Progreso Inteligente"
   git branch -M main
   git remote add origin https://github.com/Martincagliero/progreso-inteligente.git
   git push -u origin main
   ```

2. **Conecta con Render**:
   - Entrá a [render.com](https://render.com) y logueate con GitHub
   - Click en "New +" → "Web Service"
   - Conectá tu repo `Martincagliero/progreso-inteligente`
   - Render detecta automáticamente `render.yaml`
   - Click "Create Web Service"

3. **Listo!** En ~3 minutos tenés tu app en:
   `https://progreso-inteligente.onrender.com`

**Tip LinkedIn**: Compartí el link + screenshot + mini descripción:
> "🏋️ Progreso Inteligente: Mi primer proyecto full-stack.
> Sistema de recomendación de peso para gym usando RPE + FastAPI.
> Stack: Python, FastAPI, vanilla JS, deploy en Render.
> Probalo acá 👉 [tu-link]
> Repo: github.com/Martincagliero/progreso-inteligente"

### Notas importantes deploy

- El plan gratuito de Render hiberna después de 15 min sin uso (primer request puede tardar 30-60s).
- `historial.csv` se pierde en cada deploy (sistema de archivos efímero). Para persistencia real, migrar a Postgres (Render lo ofrece gratis también).
- CORS ya está configurado para cualquier origen.

## Roadmap (próximo año)

- Increments configurables (micro-plates, percent-based).
- Métricas: volumen semanal, RPE promedio, tendencia de carga.
- Tags por tipo de ejercicio (push/pull/lower) y agrupación.
- OAuth + cuenta personal en nube (Render + Postgres).
- Export gráfico (SVG/PNG) y compartir progreso.
- Tests automáticos + CI.

## Por qué en LinkedIn

Muestra: modularización, tipado, FastAPI, frontend simple, buenas prácticas de portabilidad. Escalable sin rehacer lógica central.

---

Hecho con foco en aprendizaje y mejora incremental. Abierto a ideas y colaboración.