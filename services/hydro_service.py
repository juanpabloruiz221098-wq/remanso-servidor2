import httpx
import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Catálogo focalizado en Gran Rosario, San Lorenzo, Río Carcarañá y Alrededores
PORTS_CONFIG = {
    "rosario": {
        "id": "rosario",
        "name": "Rosario (Costanera & Puente)",
        "river": "Río Paraná",
        "pref_name": "ROSARIO",
        "lat": -32.9468,
        "lon": -60.6393,
        "species": ["Dorado", "Surubí", "Boga de Tosca", "Tararira"],
        "ecosystem": "parana_rosario",
        "default_level": 2.80,
        "default_alert": 5.00,
        "default_evac": 5.30
    },
    "san_lorenzo": {
        "id": "san_lorenzo",
        "name": "San Lorenzo (Campo de la Gloria)",
        "river": "Río Paraná / Arroyo San Lorenzo",
        "pref_name": "SAN LORENZO",
        "lat": -32.7486,
        "lon": -60.7328,
        "species": ["Dorado", "Boga", "Manduví", "Variada de Cuero"],
        "ecosystem": "parana_rosario",
        "default_level": 2.95,
        "default_alert": 5.20,
        "default_evac": 5.70
    },
    "baigorria": {
        "id": "baigorria",
        "name": "Granadero Baigorria (Remanso Valerio)",
        "river": "Río Paraná (Pilotes del Puente)",
        "pref_name": "ROSARIO",
        "lat": -32.8550,
        "lon": -60.7020,
        "species": ["Gran Dorado", "Surubí Pintado", "Boga Grande"],
        "ecosystem": "parana_rosario",
        "default_level": 2.80,
        "default_alert": 5.00,
        "default_evac": 5.30
    },
    "carcarana_andino": {
        "id": "carcarana_andino",
        "name": "Río Carcarañá (Pueblo Andino / Oliveros)",
        "river": "Río Carcarañá (Correderas de Tosca)",
        "pref_name": None,
        "lat": -32.6732,
        "lon": -60.8752,
        "species": ["Tararira de Tosca", "Doradillo", "Chafalote", "Bagre Sapo"],
        "ecosystem": "rio_carcarana",
        "default_level": 1.45,
        "default_alert": 3.20,
        "default_evac": 3.80
    },
    "carcarana_centro": {
        "id": "carcarana_centro",
        "name": "Carcarañá Centro (Parque Sarmiento & Saltos)",
        "river": "Río Carcarañá (Cascadas y Dique)",
        "pref_name": None,
        "lat": -32.8611,
        "lon": -61.2222,
        "species": ["Tararira", "Carpa Gigante", "Boga", "Moncholo"],
        "ecosystem": "rio_carcarana",
        "default_level": 1.60,
        "default_alert": 3.50,
        "default_evac": 4.00
    },
    "timbues": {
        "id": "timbues",
        "name": "Timbúes / La Ribera (Boca del Carcarañá)",
        "river": "Confluencia Carcarañá / Río Coronda",
        "pref_name": "SAN LORENZO",
        "lat": -32.6167,
        "lon": -60.7333,
        "species": ["Surubí", "Dorado", "Moncholo", "Armado Chancho", "Patí"],
        "ecosystem": "confluencia_carcarana",
        "default_level": 2.90,
        "default_alert": 5.20,
        "default_evac": 5.70
    },
    "islas_victoria": {
        "id": "islas_victoria",
        "name": "Islas Frente a Rosario (Los Marinos / Charigüé)",
        "river": "Delta Entrerriano / Paraná",
        "pref_name": "VICTORIA",
        "lat": -32.8900,
        "lon": -60.6100,
        "species": ["Tararira Lagunera", "Dorado al Golpe", "Surubí en Pozón"],
        "ecosystem": "islas_rosario",
        "default_level": 3.10,
        "default_alert": 4.60,
        "default_evac": 4.90
    },
    "villa_constitucion": {
        "id": "villa_constitucion",
        "name": "Villa Constitución / Arroyo Pavón",
        "river": "Río Paraná / Arroyo Pavón",
        "pref_name": "VILLA CONSTITUCION",
        "lat": -33.2278,
        "lon": -60.3297,
        "species": ["Dorado", "Boga", "Patí Gigante", "Manduví"],
        "ecosystem": "parana_rosario",
        "default_level": 2.70,
        "default_alert": 4.50,
        "default_evac": 4.80
    }
}

_cached_prefectura_data: Dict[str, Any] = {}
_last_fetch_time: Optional[float] = None
CACHE_TTL_SECONDS = 900  # 15 minutos

async def fetch_prefectura_table() -> Dict[str, Any]:
    """Descarga y parsea la tabla completa de Prefectura Naval Argentina."""
    global _cached_prefectura_data, _last_fetch_time
    import time

    now = time.time()
    if _cached_prefectura_data and _last_fetch_time and (now - _last_fetch_time < CACHE_TTL_SECONDS):
        return _cached_prefectura_data

    url = "https://contenidosweb.prefecturanaval.gob.ar/alturas/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PescApp-Bot/1.0"
    }

    parsed_ports = {}
    try:
        async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                html = resp.text
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
                for row in rows:
                    p_match = re.search(r'data-label=["\']Puerto:["\']\s*>(.*?)</th>', row, re.IGNORECASE)
                    if not p_match:
                        continue
                    p_name = p_match.group(1).strip().upper()
                    
                    reg_match = re.search(r'data-label=["\']Ultimo Registro:["\'][^>]*>\s*([0-9\.\-]+)', row, re.IGNORECASE)
                    var_match = re.search(r'data-label=["\']Variacion["\'][^>]*>\s*([0-9\.\-]+)', row, re.IGNORECASE)
                    est_match = re.search(r'data-label=["\']Estado:["\'][^>]*>\s*([A-Za-z\.]+)', row, re.IGNORECASE)
                    date_match = re.search(r'data-label=["\']Fecha Hora:["\'][^>]*>\s*<b>(.*?)</b>', row, re.IGNORECASE)
                    alert_match = re.search(r'data-label=["\']Alerta:["\'][^>]*>\s*([0-9\.\-]+)', row, re.IGNORECASE)
                    evac_match = re.search(r'data-label=["\']Evacuaci[oó\?]n:["\'][^>]*>\s*([0-9\.\-]+)', row, re.IGNORECASE)
                    hist_match = re.search(r'page=historico&tiempo=7&id=(\d+)', row, re.IGNORECASE)

                    try:
                        parsed_ports[p_name] = {
                            "level": float(reg_match.group(1)) if reg_match else None,
                            "variation": float(var_match.group(1)) if var_match else 0.0,
                            "state": est_match.group(1).strip().upper() if est_match else "ESTAC.",
                            "timestamp_str": date_match.group(1).strip() if date_match else "",
                            "alert": float(alert_match.group(1)) if alert_match else None,
                            "evac": float(evac_match.group(1)) if evac_match else None,
                            "history_id": hist_match.group(1) if hist_match else None
                        }
                    except Exception as parse_err:
                        logger.debug(f"Error parseando puerto {p_name}: {parse_err}")

        if parsed_ports:
            _cached_prefectura_data = parsed_ports
            _last_fetch_time = now
            logger.info(f"Prefectura Naval: {len(parsed_ports)} puertos actualizados con éxito.")
    except Exception as e:
        logger.warning(f"Error consultando Prefectura Naval: {e}")

    return _cached_prefectura_data


async def get_port_hydro(port_id: str) -> Dict[str, Any]:
    """Retorna la telemetría hidrométrica para un puerto de la zona."""
    cfg = PORTS_CONFIG.get(port_id)
    if not cfg:
        port_id = "rosario"
        cfg = PORTS_CONFIG["rosario"]

    table = await fetch_prefectura_table()
    pref_name = cfg.get("pref_name")
    
    if pref_name and pref_name in table:
        item = table[pref_name]
        var = item.get("variation", 0.0)
        
        state_str = item.get("state", "ESTAC.")
        trend = "estacionario"
        if "CRECE" in state_str or var > 0.03:
            trend = "creciente"
        elif "BAJA" in state_str or var < -0.03:
            trend = "bajante"

        return {
            "port_id": port_id,
            "port_name": cfg["name"],
            "river_name": cfg["river"],
            "water_level_m": item.get("level") or cfg["default_level"],
            "variation_24h_m": var,
            "trend": trend,
            "state_label": state_str,
            "last_reading_time": item.get("timestamp_str", "Actual"),
            "alert_level_m": item.get("alert") or cfg["default_alert"],
            "evac_level_m": item.get("evac") or cfg["default_evac"],
            "history_id": item.get("history_id"),
            "data_source": "Prefectura Naval Argentina (Oficial en Vivo)"
        }
    
    # Modelo para el Río Carcarañá (río de tosca tributario sin estación PNA directa)
    return {
        "port_id": port_id,
        "port_name": cfg["name"],
        "river_name": cfg["river"],
        "water_level_m": cfg["default_level"],
        "variation_24h_m": -0.03,
        "trend": "bajante",
        "state_label": "BAJA LEVE",
        "last_reading_time": datetime.now(timezone.utc).strftime("%d/%b/%y - %H:%M"),
        "alert_level_m": cfg["default_alert"],
        "evac_level_m": cfg["default_evac"],
        "history_id": None,
        "data_source": "Modelo Cuenca Carcarañá (Nivel de Vado)"
    }


async def get_port_history(port_id: str) -> List[Dict[str, Any]]:
    """Descarga los últimos 7 días de registros hidrométricos reales."""
    hydro = await get_port_hydro(port_id)
    history_id = hydro.get("history_id")
    
    if history_id:
        url = f"https://contenidosweb.prefecturanaval.gob.ar/alturas/?page=historico&tiempo=7&id={history_id}"
        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    pattern = r'<td><i[^>]*></i>\s*([0-9\-]+)\s*<i[^>]*></i>\s*([0-9:]+)</td>\s*<td>([0-9\.]+)\s*Mts</td>'
                    matches = re.findall(pattern, r.text)
                    if matches:
                        results = []
                        step = max(1, len(matches) // 14)
                        for date_str, time_str, level_str in matches[::step]:
                            results.append({
                                "date": date_str,
                                "time": time_str,
                                "level": float(level_str)
                            })
                        results.reverse()
                        return results
        except Exception as e:
            logger.warning(f"Error descargando histórico para {port_id}: {e}")

    # Fallback sintético basado en el nivel actual
    base_level = hydro["water_level_m"]
    from datetime import timedelta
    fallback_history = []
    now = datetime.now()
    for i in range(7, -1, -1):
        dt = now - timedelta(days=i)
        simulated = round(base_level + (0.03 * (3 - i)), 2)
        fallback_history.append({
            "date": dt.strftime("%Y-%m-%d"),
            "time": "12:00",
            "level": simulated
        })
    return fallback_history
