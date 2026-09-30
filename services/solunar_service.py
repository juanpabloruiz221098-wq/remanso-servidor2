import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

def get_moon_phase(dt: datetime = None) -> Dict[str, Any]:
    """
    Calcula fase lunar, edad y porcentaje de iluminación utilizando
    fórmulas astronómicas simplificadas basadas en el ciclo sinódico (29.53058867 días).
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    # Fecha de referencia conocida: Luna nueva el 6 de Enero de 2000 a las 18:14 UTC
    ref_date = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    diff = (dt - ref_date).total_seconds()
    synodic_cycle = 29.53058867 * 86400  # segundos

    phase_sec = diff % synodic_cycle
    phase_ratio = phase_sec / synodic_cycle  # 0.0 a 1.0
    moon_age_days = phase_ratio * 29.53

    # Porcentaje de iluminación (0% nueva, 100% llena)
    illumination = round((1 - math.cos(phase_ratio * 2 * math.pi)) / 2 * 100, 1)

    # Identificación textual de fase
    if phase_ratio < 0.03 or phase_ratio > 0.97:
        phase_name = "Luna Nueva"
        icon = "🌑"
        rating = 90  # Excelente para pesca
    elif phase_ratio < 0.22:
        phase_name = "Luna Creciente"
        icon = "🌒"
        rating = 75
    elif phase_ratio < 0.28:
        phase_name = "Cuarto Creciente"
        icon = "🌓"
        rating = 70
    elif phase_ratio < 0.47:
        phase_name = "Gibosa Creciente"
        icon = "🌔"
        rating = 80
    elif phase_ratio < 0.53:
        phase_name = "Luna Llena"
        icon = "🌕"
        rating = 95  # Gran actividad de predadores nocturnos
    elif phase_ratio < 0.72:
        phase_name = "Gibosa Menguante"
        icon = "🌖"
        rating = 75
    elif phase_ratio < 0.78:
        phase_name = "Cuarto Menguante"
        icon = "🌗"
        rating = 65
    else:
        phase_name = "Luna Menguante"
        icon = "🌘"
        rating = 75

    return {
        "phase_ratio": round(phase_ratio, 3),
        "moon_age_days": round(moon_age_days, 1),
        "illumination_pct": illumination,
        "phase_name": phase_name,
        "icon": icon,
        "solunar_rating": rating
    }


def get_solunar_windows(lat: float, lon: float, dt: datetime = None) -> Dict[str, Any]:
    """
    Calcula ventanas de actividad solunar mayores y menores para una latitud y longitud dada.
    """
    if dt is None:
        # Hora local Argentina (UTC-3)
        dt = datetime.now(timezone(timedelta(hours=-3)))

    moon_info = get_moon_phase(dt)

    # Desplazamiento aproximado del tránsito lunar (la Luna se retrasa ~50 min por día respecto al Sol)
    day_offset_minutes = (moon_info["moon_age_days"] * 50.4) % 1440
    
    # Base local aproximada
    transit_hour = (12.0 + (day_offset_minutes / 60.0) - (lon / 15.0) + 3.0) % 24.0
    underfoot_hour = (transit_hour + 12.0) % 24.0

    # Formatear ventanas horarias
    def format_window(center_hour: float, duration_hours: float):
        start = (center_hour - duration_hours / 2) % 24
        end = (center_hour + duration_hours / 2) % 24
        return f"{int(start):02d}:{int((start % 1)*60):02d} - {int(end):02d}:{int((end % 1)*60):02d}"

    major_1 = format_window(transit_hour, 2.0)
    major_2 = format_window(underfoot_hour, 2.0)
    minor_1 = format_window((transit_hour - 6.0) % 24, 1.0)
    minor_2 = format_window((transit_hour + 6.0) % 24, 1.0)

    # Verificar si el horario actual está dentro de una ventana
    current_hour_decimal = dt.hour + (dt.minute / 60.0)
    
    def is_inside(center: float, half_dur: float):
        d = abs(current_hour_decimal - center)
        return d <= half_dur or (24 - d) <= half_dur

    is_major = is_inside(transit_hour, 1.0) or is_inside(underfoot_hour, 1.0)
    is_minor = is_inside((transit_hour - 6.0) % 24, 0.5) or is_inside((transit_hour + 6.0) % 24, 0.5)

    return {
        "moon": moon_info,
        "major_period_1": major_1,
        "major_period_2": major_2,
        "minor_period_1": minor_1,
        "minor_period_2": minor_2,
        "is_in_major": is_major,
        "is_in_minor": is_minor
    }
