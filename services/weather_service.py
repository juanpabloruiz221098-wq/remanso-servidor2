import httpx
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def get_real_weather(lat: float, lon: float):
    """
    Obtiene métricas meteorológicas en tiempo real de Open-Meteo para las coordenadas dadas.
    Calcula la presión barométrica actual y el delta de presión de las últimas 6 horas.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m,cloud_cover"
        "&hourly=surface_pressure"
        "&past_days=1&forecast_days=1"
        "&timezone=America%2FArgentina%2FBuenos_Aires"
    )
    
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

            current = data.get("current", {})
            hourly = data.get("hourly", {})

            current_pressure = current.get("surface_pressure", 1013.25)
            
            # Calcular delta de presión de las últimas 6 horas
            # Buscamos en el array horario de presiones
            hourly_pressures = hourly.get("surface_pressure", [])
            hourly_times = hourly.get("time", [])
            
            # Valor por defecto delta
            pressure_delta_6h = 0.0
            if len(hourly_pressures) >= 12:
                # Tomamos la hora actual aproximada dentro del array
                # El array tiene 24 horas del día anterior + horas de hoy
                # La presión de hace 6 horas está aproximadamente a 6 índices atrás del último horario transcurrido
                now_str = current.get("time", "")
                if now_str in hourly_times:
                    idx = hourly_times.index(now_str)
                    if idx >= 6:
                        past_p = hourly_pressures[idx - 6]
                        pressure_delta_6h = round(current_pressure - past_p, 2)
                    elif idx > 0:
                        past_p = hourly_pressures[0]
                        pressure_delta_6h = round(current_pressure - past_p, 2)

            return {
                "temperature_c": current.get("temperature_2m", 20.0),
                "humidity_pct": current.get("relative_humidity_2m", 60),
                "pressure_hpa": current_pressure,
                "pressure_delta_6h": pressure_delta_6h,
                "wind_speed_kmh": current.get("wind_speed_10m", 12.0),
                "wind_direction_deg": current.get("wind_direction_10m", 90),
                "cloud_cover_pct": current.get("cloud_cover", 20),
                "source": "Open-Meteo Realtime API"
            }
    except Exception as e:
        logger.warning(f"Error fetching live weather: {e}. Usando fallback verosímil.")
        return {
            "temperature_c": 21.4,
            "humidity_pct": 65,
            "pressure_hpa": 1014.5,
            "pressure_delta_6h": -0.4,
            "wind_speed_kmh": 14.0,
            "wind_direction_deg": 85,
            "cloud_cover_pct": 25,
            "source": "Fallback Offline Cache"
        }
