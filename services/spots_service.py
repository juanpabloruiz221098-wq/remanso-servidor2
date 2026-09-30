import sqlite3
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "pescapp.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

# Pesqueros auténticos y emblemáticos de Rosario, San Lorenzo, Carcarañá y Alrededores
REGIONAL_SEED_SPOTS = [
    (
        "spot-ros-01",
        "Remanso Valerio (Granadero Baigorria)",
        "Gran Dorado y Surubí Pintado",
        "Baitcasting / Fondo con Morena o Anguila",
        9.5,
        "Pilotes del Puente Rosario-Victoria. Fondo de toscas profundas y remansos violentos donde cazan grandes dorados. Cuidado con el enganche en las piedras basales.",
        "spot",
        -32.8550,
        -60.7020
    ),
    (
        "spot-ros-02",
        "La Florida & Costa Alta (Rosario Norte)",
        "Boga de Piedra y Dorado",
        "Masa de harina de maíz/vainilla y señuelos flotantes",
        4.0,
        "Famosa zona de pesca de boga de gran porte en los muelles y veriles de arena. Bajada de lanchas municipal y guarderías náuticas.",
        "bajada_lancha",
        -32.8835,
        -60.6860
    ),
    (
        "spot-ros-03",
        "Boca del Riacho Los Marinos (Islas Rosario)",
        "Dorado al Golpe y Tararira",
        "Spinning / Señuelos de media agua tipo Minnow",
        3.2,
        "Cruce de aguas claras del riacho isleño con el cauce del Paraná. Excelente para castear pegado a las barrancas y camalotales en primavera y verano.",
        "spot",
        -32.8890,
        -60.6280
    ),
    (
        "spot-sl-01",
        "Desembocadura Arroyo San Lorenzo",
        "Doradillo, Manduví y Boga",
        "Baitcasting liviano y fondo con lombriz / tripa de pollo",
        3.8,
        "Confluencia del Arroyo San Lorenzo con el Río Paraná frente a los muelles portuarios. Gran concentración de forrajeros (mojarras y sabalitos).",
        "spot",
        -32.7486,
        -60.7280
    ),
    (
        "spot-sl-02",
        "Campo de la Gloria (Costanera San Lorenzo)",
        "Boga, Bagre Amarillo y Moncholo",
        "Línea de fondo de 2 anzuelos con plomo corredizo",
        5.2,
        "Clásica pesca de costa santafesina. Buen rendimiento nocturno para variada de piel con lombriz rubia y carnada blanca.",
        "spot",
        -32.7445,
        -60.7295
    ),
    (
        "spot-carc-01",
        "Saltos de Tosca de Pueblo Andino (Río Carcarañá)",
        "Tararira de Tosca y Doradillo",
        "Spinning / Baitcasting con señuelos blandos (gomas anti-enganche)",
        1.8,
        "Correderas rocosas de tosca con aguas rápidas muy oxigenadas sobre el Río Carcarañá. Gran combatividad de las tarariras tornasoladas en los remansos de piedra.",
        "spot",
        -32.6732,
        -60.8752
    ),
    (
        "spot-carc-02",
        "Cascadas del Parque Sarmiento (Carcarañá Centro)",
        "Tararira, Carpa Gigante y Chafalote",
        "Fly Cast / Harinados (línea coreana) / Señuelos de flote",
        2.2,
        "Pozón profundo aguas abajo de la caída y compuertas del Dique Carcarañá. Muy concurrido los fines de semana. Ejemplares de carpas de más de 8 kg.",
        "spot",
        -32.8611,
        -61.2222
    ),
    (
        "spot-timb-01",
        "La Ribera / Timbúes (Boca del Río Carcarañá)",
        "Surubí, Patí Gigante y Moncholo",
        "Pesca pesada de fondo anclado en el veril",
        7.5,
        "Desembocadura del Río Carcarañá en el Río Coronda. La mezcla de nutrientes convierte a este punto en un imán para grandes surubíes y patíes en los pozones.",
        "spot",
        -32.6167,
        -60.7333
    ),
    (
        "spot-ros-04",
        "Desembocadura Arroyo Saladillo (Rosario Sur)",
        "Boga y Variada Pesada",
        "Fondo con plomada pesada y masa dulce",
        6.0,
        "Pesquero histórico del sur rosarino. Veril profundo de tosca con buena presencia de bogas y armados.",
        "spot",
        -33.0030,
        -60.6080
    ),
    (
        "spot-islas-01",
        "Laguna del Charigüé (Frente a Rosario)",
        "Tararira con señuelo de superficie (Popper/Paseante)",
        "Kayak Fishing / Vadeo de costa",
        1.2,
        "Espejo de agua interior en las islas entrerrianas. Aguas calmas transparentes con vegetación donde la tararira ataca en superficie violentamente.",
        "camping",
        -32.9250,
        -60.5900
    )
]

def init_db(force_reload: bool = False):
    """Inicializa la tabla y carga los pesqueros de Rosario, San Lorenzo y Carcarañá."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fishing_spots (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                species TEXT NOT NULL,
                technique TEXT,
                depth_m REAL,
                notes TEXT,
                category TEXT DEFAULT 'spot',
                lat REAL NOT NULL,
                lng REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        if force_reload:
            cursor.execute("DELETE FROM fishing_spots")
            cursor.executemany("""
                INSERT INTO fishing_spots (id, title, species, technique, depth_m, notes, category, lat, lng)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, REGIONAL_SEED_SPOTS)
            conn.commit()
        else:
            cursor.execute("SELECT COUNT(*) FROM fishing_spots")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.executemany("""
                    INSERT INTO fishing_spots (id, title, species, technique, depth_m, notes, category, lat, lng)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, REGIONAL_SEED_SPOTS)
                conn.commit()

# Cargar pesqueros regionales actualizados
init_db(force_reload=True)

def list_spots() -> List[Dict[str, Any]]:
    """Retorna todos los puntos de pesca guardados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fishing_spots ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def create_spot(data: Dict[str, Any]) -> Dict[str, Any]:
    """Crea y persiste un nuevo punto de pesca."""
    spot_id = str(uuid.uuid4())
    title = data.get("title", "Pesquero sin nombre")
    species = data.get("species", "Variada de Río")
    technique = data.get("technique", "No especificada")
    depth_m = data.get("depth_m")
    notes = data.get("notes", "")
    category = data.get("category", "spot")
    lat = float(data["lat"])
    lng = float(data["lng"])
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fishing_spots (id, title, species, technique, depth_m, notes, category, lat, lng, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (spot_id, title, species, technique, depth_m, notes, category, lat, lng, created_at))
        conn.commit()

    return {
        "id": spot_id,
        "title": title,
        "species": species,
        "technique": technique,
        "depth_m": depth_m,
        "notes": notes,
        "category": category,
        "lat": lat,
        "lng": lng,
        "created_at": created_at
    }

def delete_spot(spot_id: str) -> bool:
    """Elimina un punto de pesca por su ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fishing_spots WHERE id = ?", (spot_id,))
        conn.commit()
        return cursor.rowcount > 0
