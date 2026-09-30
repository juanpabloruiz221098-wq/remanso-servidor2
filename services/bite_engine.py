from typing import Dict, Any

def compute_bite_index(
    hydro_data: Dict[str, Any],
    weather_data: Dict[str, Any],
    solunar_data: Dict[str, Any],
    ecosystem: str = "parana_medio"
) -> Dict[str, Any]:
    """
    Motor Heurístico PescApp Argentina:
    Calcula el Índice de Pique integral (0 a 100), semáforo y análisis cualitativo.
    """
    # 1. Componente Barométrico (35%)
    p_delta = weather_data.get("pressure_delta_6h", 0.0)
    p_current = weather_data.get("pressure_hpa", 1013.0)

    if abs(p_delta) <= 0.8:
        s_baro = 95.0  # Presión muy estable, pique regular y predecible
    elif -2.5 <= p_delta < -0.8:
        s_baro = 85.0  # Caída moderada previa a frente (buen pique inicial)
    elif p_delta < -2.5:
        s_baro = 25.0  # Caída violenta (frente de tormenta severo, peces inactivos)
    elif p_delta > 2.0:
        s_baro = 30.0  # Entrada violenta de alta presión / pampero frío
    else:
        s_baro = 65.0

    # Ajuste por valor absoluto de presión
    if p_current < 1005:
        s_baro = max(20.0, s_baro - 15)  # Depresión muy baja
    elif p_current > 1022:
        s_baro = max(30.0, s_baro - 10)

    # 2. Componente Hidrométrico (25%)
    trend = hydro_data.get("trend", "estacionario")
    var_24h = hydro_data.get("variation_24h_m", 0.0)

    if ecosystem in ["parana_rosario", "parana_medio", "parana_alto", "rio_uruguay"]:
        if trend == "bajante":
            # La bajante moderada en el Paraná aclara el agua y favorece el pique de Dorado y Boga
            s_hydro = 95.0 if abs(var_24h) < 0.20 else 60.0
        elif trend == "estacionario":
            s_hydro = 80.0
        else: # creciente
            s_hydro = 45.0 if var_24h > 0.25 else 60.0
    elif ecosystem == "rio_carcarana":
        # El Carcarañá es un río de tosca y saltos: agua clara y nivel bajo/estable es el momento ideal para Tarariras
        if trend == "bajante":
            s_hydro = 95.0
        elif trend == "estacionario":
            s_hydro = 85.0
        else: # creciente violenta arrastra sedimentos y reduce el pique en artificiales
            s_hydro = 35.0 if var_24h > 0.15 else 50.0
    elif ecosystem == "confluencia_carcarana":
        # Timbúes / La Ribera: confluencia Carcarañá y Coronda
        s_hydro = 90.0 if trend in ["bajante", "estacionario"] else 55.0
    elif ecosystem == "islas_rosario":
        # Arroyos y lagunas isleñas del Delta frente a Rosario
        s_hydro = 90.0 if abs(var_24h) < 0.10 else 65.0
    elif ecosystem == "lagunas_bonaerenses":
        s_hydro = 85.0 if abs(var_24h) < 0.05 else 60.0
    else:
        s_hydro = 70.0

    # 3. Componente de Viento (20%)
    wind_kmh = weather_data.get("wind_speed_kmh", 12.0)
    wind_dir = weather_data.get("wind_direction_deg", 90)

    if ecosystem == "lagunas_bonaerenses":
        # Las lagunas necesitan viento moderado para pescar al garete
        if 12.0 <= wind_kmh <= 24.0:
            s_wind = 100.0
        elif wind_kmh < 8.0:
            s_wind = 50.0  # Planchada, difícil engañar pejerreyes
        elif wind_kmh > 35.0:
            s_wind = 20.0  # Peligro de oleaje
        else:
            s_wind = 70.0
    elif ecosystem == "patagonia_cordillera":
        # Viento fuerte en Patagonia anula el casteo
        if wind_kmh < 15.0:
            s_wind = 95.0
        elif wind_kmh < 30.0:
            s_wind = 65.0
        else:
            s_wind = 15.0
    else:
        # Litoral / Ríos Paraná y Uruguay
        if wind_kmh <= 18.0:
            s_wind = 95.0
        elif wind_kmh <= 30.0:
            s_wind = 65.0
        else:
            s_wind = 25.0

    # 4. Componente Solunar y Lunar (20%)
    moon = solunar_data.get("moon", {})
    moon_base = moon.get("solunar_rating", 70)
    
    if solunar_data.get("is_in_major"):
        s_solunar = 100.0
    elif solunar_data.get("is_in_minor"):
        s_solunar = 85.0
    else:
        s_solunar = moon_base * 0.65

    # Ponderación total
    total_score = int(
        (s_baro * 0.35) +
        (s_hydro * 0.25) +
        (s_wind * 0.20) +
        (s_solunar * 0.20)
    )
    total_score = max(5, min(99, total_score))

    # Semáforo
    if total_score >= 75:
        traffic_light = "verde"
        classification = "Condición Excelente"
        color_hex = "#10b981"  # Emerald 500
    elif total_score >= 50:
        traffic_light = "amarillo"
        classification = "Condición Buena / Moderada"
        color_hex = "#f59e0b"  # Amber 500
    else:
        traffic_light = "rojo"
        classification = "Condición Regular / Desfavorable"
        color_hex = "#ef4444"  # Red 500

    # Resumen contextual
    trend_desc = {
        "bajante": f"en suave bajante ({var_24h:+.2f}m en 24h), favoreciendo el agua clara",
        "creciente": f"en creciente ({var_24h:+.2f}m en 24h), agua con mayor sedimento",
        "estacionario": "estacionario, manteniendo niveles estables"
    }.get(trend, "estable")

    solunar_state = "¡Estás en plena ventana de mayor actividad!" if solunar_data.get("is_in_major") else (
        "Ventana menor de actividad activa." if solunar_data.get("is_in_minor") else "Próxima ventana mayor indicada abajo."
    )

    summary = (
        f"Índice del {total_score}% ({classification}). "
        f"El {hydro_data.get('river_name', 'río')} se encuentra {trend_desc}. "
        f"Presión barométrica en {p_current:.1f} hPa ({'estable' if abs(p_delta) <= 1.0 else f'variación {p_delta:+.1f} hPa en 6h'}). "
        f"Viento actual de {wind_kmh:.0f} km/h. {solunar_state}"
    )

    return {
        "score": total_score,
        "classification": classification,
        "traffic_light": traffic_light,
        "color_hex": color_hex,
        "summary": summary,
        "breakdown": {
            "barometric_score": round(s_baro, 1),
            "hydro_score": round(s_hydro, 1),
            "wind_score": round(s_wind, 1),
            "solunar_score": round(s_solunar, 1)
        }
    }
