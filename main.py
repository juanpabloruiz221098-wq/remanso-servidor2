import asyncio
import json
import logging
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import time
from services.hydro_service import PORTS_CONFIG, get_port_hydro, get_port_history
from services.weather_service import get_real_weather
from services.solunar_service import get_solunar_windows
from services.bite_engine import compute_bite_index
from services.spots_service import list_spots, create_spot, delete_spot
from services.catalog_service import (
    list_species, list_rigs, list_checkpoints, create_checkpoint, delete_checkpoint,
    add_bite_feedback, get_bite_feedback_summary
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remanso")

app = FastAPI(title="Remanso - Telemetría Náutica & Pesca Deportiva")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/manifest.json")
async def get_manifest():
    return FileResponse(STATIC_DIR / "manifest.json", media_type="application/manifest+json")

@app.get("/sw.js")
async def get_service_worker():
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript")

@app.api_route("/download/remanso.apk", methods=["GET", "HEAD"])
@app.api_route("/download/apk", methods=["GET", "HEAD"])
async def download_apk():
    apk_path = STATIC_DIR / "remanso.apk"
    if apk_path.exists():
        return FileResponse(
            apk_path,
            filename="Remanso-Nautico.apk",
            media_type="application/vnd.android.package-archive"
        )
    return Response(content="APK no encontrado en el servidor", status_code=404)


TELEMETRY_CACHE = {}
CACHE_TIMESTAMPS = {}
CACHE_TTL = 75.0  # Segundos de vigencia para evitar sobrecarga de APIs externas

async def assemble_port_payload(port_id: str, force: bool = False):
    """Compila y evalúa todas las métricas en tiempo real para un puerto específico con cache en memoria."""
    cfg = PORTS_CONFIG.get(port_id)
    if not cfg:
        port_id = "rosario"
        cfg = PORTS_CONFIG["rosario"]

    now = time.time()
    if not force and port_id in TELEMETRY_CACHE:
        if now - CACHE_TIMESTAMPS.get(port_id, 0) < CACHE_TTL:
            cached = dict(TELEMETRY_CACHE[port_id])
            fb = get_bite_feedback_summary(port_id)
            cached["bite"]["feedback"] = fb
            return cached

    # 1. Telemetría de ríos (Prefectura Naval Argentina en vivo)
    hydro = await get_port_hydro(port_id)

    # 2. Clima y Barómetro en tiempo real (Open-Meteo satelital)
    weather = await get_real_weather(cfg["lat"], cfg["lon"])

    # 3. Solunar y Luna
    solunar = get_solunar_windows(cfg["lat"], cfg["lon"])

    # 4. Motor Heurístico de Pique
    bite = compute_bite_index(hydro, weather, solunar, ecosystem=cfg.get("ecosystem", "parana_medio"))

    # 5. Integración del Feedback Comunitario (Ajuste supervisado al puntaje de pique)
    feedback = get_bite_feedback_summary(port_id)
    raw_score = bite.get("score", 50)
    adjusted_score = max(5, min(100, raw_score + feedback.get("score_adjustment", 0)))
    bite["raw_score"] = raw_score
    bite["score"] = adjusted_score
    bite["feedback"] = feedback

    payload = {
        "port_id": port_id,
        "ecosystem_label": cfg.get("ecosystem", "").replace("_", " ").title(),
        "species": cfg.get("species", []),
        "hydro": hydro,
        "weather": weather,
        "solunar": solunar,
        "bite": bite,
        "cached_at": now
    }

    TELEMETRY_CACHE[port_id] = payload
    CACHE_TIMESTAMPS[port_id] = now
    return payload

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Sirve el Dashboard de Pique e Hidrometría en Tiempo Real."""
    html_path = BASE_DIR / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/api/ports")
async def list_ports():
    """Retorna la lista de pesqueros y puertos soportados."""
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "river": p["river"],
            "lat": p["lat"],
            "lon": p["lon"],
            "species": p["species"]
        }
        for p in PORTS_CONFIG.values()
    ]

@app.get("/api/metrics/{port_id}")
async def get_metrics(port_id: str):
    """Consulta síncrona REST para un puerto en tiempo real."""
    return await assemble_port_payload(port_id)

@app.get("/api/river-history/{port_id}")
async def get_river_history(port_id: str):
    """Retorna los registros de los últimos 7 días de Prefectura Naval."""
    return await get_port_history(port_id)

@app.get("/api/spots")
async def get_all_spots():
    """Retorna la lista de todos los puntos de pesca guardados."""
    return list_spots()

@app.post("/api/spots")
async def add_spot(request: Request):
    """Crea y persiste un nuevo punto de pesca."""
    body = await request.json()
    return create_spot(body)

@app.delete("/api/spots/{spot_id}")
async def remove_spot(spot_id: str):
    """Elimina un punto de pesca."""
    success = delete_spot(spot_id)
    return {"deleted": success, "id": spot_id}

@app.get("/api/spots/export/gpx")
async def export_spots_gpx():
    """Exporta los waypoints en formato GPX 1.1 compatible con Garmin, Lowrance y ecosondas náuticas."""
    spots = list_spots()
    from datetime import datetime, timezone
    
    gpx_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="Remanso - Telemetria Nautica y Pesca Deportiva" xmlns="http://www.topografix.com/GPX/1/1">',
        '  <metadata>',
        '    <name>Waypoints de Pesca - Remanso</name>',
        f'    <time>{datetime.now(timezone.utc).isoformat()}</time>',
        '  </metadata>'
    ]
    
    for s in spots:
        title = s.get("title", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        desc = f"Especie: {s.get('species', '')} | Aparejo: {s.get('technique', '')} | Notas: {s.get('notes', '')}".replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        sym = "Fishing Area" if s.get("category") == "spot" else ("Boat Ramp" if s.get("category") == "bajada_lancha" else "Waypoint")
        gpx_lines.append(f'  <wpt lat="{s["lat"]}" lon="{s["lng"]}">')
        gpx_lines.append(f'    <name>{title}</name>')
        gpx_lines.append(f'    <desc>{desc}</desc>')
        gpx_lines.append(f'    <sym>{sym}</sym>')
        gpx_lines.append('  </wpt>')
        
    gpx_lines.append('</gpx>')
    xml_content = "\n".join(gpx_lines)
    return Response(
        content=xml_content,
        media_type="application/gpx+xml",
        headers={"Content-Disposition": "attachment; filename=pesqueros-remanso.gpx"}
    )

@app.get("/api/species")
async def get_species():
    """Retorna el catálogo completo de especies de la cuenca."""
    return list_species()

@app.get("/api/tackle-rigs")
async def get_tackle_rigs():
    """Retorna las recomendaciones de armado de líneas y aparejos."""
    return list_rigs()

@app.get("/api/checkpoints")
async def get_checkpoints():
    """Retorna los checkpoints y anotaciones guardadas por el pescador."""
    return list_checkpoints()

@app.post("/api/checkpoints")
async def add_checkpoint(request: Request):
    """Crea y persiste un nuevo checkpoint o anotación."""
    body = await request.json()
    return create_checkpoint(body)

@app.delete("/api/checkpoints/{cp_id}")
async def remove_checkpoint(cp_id: str):
    """Elimina un checkpoint guardado."""
    success = delete_checkpoint(cp_id)
    return {"deleted": success, "id": cp_id}

@app.get("/api/feedback/{port_id}")
async def get_feedback(port_id: str):
    """Consulta el consenso comunitario de pique para un puerto."""
    return get_bite_feedback_summary(port_id)

@app.post("/api/feedback")
async def submit_feedback(request: Request):
    """Registra un reporte de pique para calibrar el motor de predicción."""
    body = await request.json()
    port_id = body.get("port_id", "rosario")
    rating = body.get("rating", "excelente")
    comment = body.get("comment", "")
    res = add_bite_feedback(port_id, rating, comment)
    if port_id in TELEMETRY_CACHE:
        del TELEMETRY_CACHE[port_id]
    return res

@app.post("/api/track/export/gpx")
async def export_track_gpx(request: Request):
    """Exporta el track náutico grabado en vivo en formato GPX 1.1 con velocidades en nudos y rumbo COG."""
    body = await request.json()
    points = body.get("points", [])
    name = body.get("name", "Deriva Náutica - Remanso")
    from datetime import datetime, timezone
    
    gpx_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="Remanso - Track Logger Nautico" xmlns="http://www.topografix.com/GPX/1/1">',
        '  <metadata>',
        f'    <name>{name}</name>',
        f'    <time>{datetime.now(timezone.utc).isoformat()}</time>',
        '  </metadata>',
        '  <trk>',
        f'    <name>{name}</name>',
        '    <trkseg>'
    ]
    for pt in points:
        lat = pt.get("lat")
        lon = pt.get("lng")
        time_iso = pt.get("time", datetime.now(timezone.utc).isoformat())
        speed_kts = pt.get("speed_knots", 0.0)
        cog = pt.get("cog", 0.0)
        gpx_lines.append(f'      <trkpt lat="{lat}" lon="{lon}">')
        gpx_lines.append(f'        <time>{time_iso}</time>')
        gpx_lines.append(f'        <extensions><speed_knots>{speed_kts}</speed_knots><cog>{cog}</cog></extensions>')
        gpx_lines.append('      </trkpt>')
        
    gpx_lines.append('    </trkseg>')
    gpx_lines.append('  </trk>')
    gpx_lines.append('</gpx>')
    
    return Response(
        content="\n".join(gpx_lines),
        media_type="application/gpx+xml",
        headers={"Content-Disposition": f"attachment; filename=deriva-remanso-{int(time.time())}.gpx"}
    )

@app.websocket("/ws/{port_id}")
async def websocket_endpoint(websocket: WebSocket, port_id: str):
    """
    Canal bidireccional WebSocket para telemetría en vivo.
    Emite actualizaciones periódicas cada 10 segundos y responde a cambios de puerto al instante.
    """
    await websocket.accept()
    current_port = port_id
    logger.info(f"Cliente WebSocket conectado a puerto: {current_port}")

    try:
        # Enviar payload inicial de inmediato
        initial_data = await assemble_port_payload(current_port)
        await websocket.send_text(json.dumps(initial_data))

        # Tarea de fondo que transmite actualizaciones periódicas
        async def telemetry_loop():
            nonlocal current_port
            while True:
                await asyncio.sleep(10)
                try:
                    fresh_data = await assemble_port_payload(current_port)
                    await websocket.send_text(json.dumps(fresh_data))
                except Exception as ex:
                    logger.debug(f"Error en loop de telemetría: {ex}")
                    break

        push_task = asyncio.create_task(telemetry_loop())

        # Escuchar peticiones o cambios de puerto del cliente
        while True:
            text = await websocket.receive_text()
            data = json.loads(text)
            action = data.get("action")
            
            if action == "change_port":
                new_port = data.get("port_id")
                if new_port in PORTS_CONFIG:
                    current_port = new_port
                    logger.info(f"Cambiando a puerto: {current_port}")
                    fresh_data = await assemble_port_payload(current_port)
                    await websocket.send_text(json.dumps(fresh_data))

            elif action == "refresh":
                fresh_data = await assemble_port_payload(current_port)
                await websocket.send_text(json.dumps(fresh_data))

    except WebSocketDisconnect:
        logger.info(f"Cliente desconectado de {current_port}")
    except Exception as e:
        logger.warning(f"Excepción en WebSocket: {e}")
    finally:
        if 'push_task' in locals() and not push_task.done():
            push_task.cancel()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
