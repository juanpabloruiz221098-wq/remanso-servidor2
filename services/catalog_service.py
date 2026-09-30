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

# Catálogo completo de especies de la Cuenca Paraná-Carcarañá-San Lorenzo
# Catálogo completo de especies de la Cuenca Paraná-Carcarañá-San Lorenzo con fotos reales
SPECIES_CATALOG = [
    {
        "id": "spec-dorado",
        "common_name": "Dorado",
        "scientific_name": "Salminus brasiliensis",
        "family": "Characidae",
        "habitat": "Correderas de tosca, pilotes de puentes (Rosario-Victoria), remansos y desembocaduras de arroyos.",
        "description": "Apodado 'El Tigre de los Ríos'. Es el pez deportivo más combativo de la cuenca. De cuerpo musculoso, color amarillo dorado con reflejos anaranjados y potentes mandíbulas armadas con dientes cónicos cortantes. Realiza saltos acrobáticos violentos al ser clavado.",
        "seasonal_behavior": "Máxima actividad en primavera y verano (octubre a abril) con aguas templadas (21°C a 27°C). En invierno baja a los pozones profundos y caza en horas de siesta al sol.",
        "min_size_cm": 65.0,
        "regulation_note": "Captura y Devolución obligatoria en zonas de reserva. En Santa Fe rige veda de reproducción y cupo estricto.",
        "baits_natural": "Morena viva (la reina de las carnadas), anguila de río, cascarudo, boguita viva de 10-15cm, filet de sábalo.",
        "baits_artificial": "Señuelos Minnow paleta 1 y 2 (11 a 14 cm) tipo color cardenal o doradillo, Crankbaits de media agua, Spinnerbaits pesados y moscas streamers con ojos de plomo.",
        "image_url": "/static/species/dorado.jpg",
        "tag_color": "#eab308"
    },
    {
        "id": "spec-surubi-pintado",
        "common_name": "Surubí Pintado",
        "scientific_name": "Pseudoplatystoma corruscans",
        "family": "Pimelodidae",
        "habitat": "Pozones profundos del canal de navegación (San Lorenzo, Timbúes, Remanso Valerio) de 8 a 15 metros de profundidad.",
        "description": "El siluro predador de mayor porte de nuestra región. Cuerpo alargado sin escamas, cubierto de manchas circulares oscuras sobre fondo pardo-grisáceo. Dotado de largos barbillones táctiles y boca ancha succionadora para cazar forrajeros en el fondo.",
        "seasonal_behavior": "Especie de hábitos preferentemente crepusculares y nocturnos. Los meses calurosos son los más productivos para pesca anclada o al garete lento.",
        "min_size_cm": 85.0,
        "regulation_note": "Talla mínima 85 cm. Prohibida la extracción de reproductores superiores a 120 cm. Devolución altamente fomentada.",
        "baits_natural": "Morena grande encarnada viva, anguila clavada por la cola, posta fresca de sábalo, tripa de pollo fresca.",
        "baits_artificial": "Trolling con señuelos de paleta de profundidad (paleta 3 o Deep Diver) que golpeen el fondo de tosca a 8-10 metros.",
        "image_url": "/static/species/surubi_pintado.jpg",
        "tag_color": "#06b6d4"
    },
    {
        "id": "spec-surubi-atigrado",
        "common_name": "Surubí Atigrado",
        "scientific_name": "Pseudoplatystoma reticulatum",
        "family": "Pimelodidae",
        "habitat": "Veriles de islas del Paraná, desembocaduras de lagunas y lechos de arena y tosca.",
        "description": "Distinguible por sus llamativas franjas transversales oscuras en forma de cebra o tigre. De porte ligeramente más compacto que el pintado pero de aceleración explosiva en la primera corrida.",
        "seasonal_behavior": "Muy activo en primavera y verano. Suele cazar en correderas de poca profundidad durante la caída del sol.",
        "min_size_cm": 80.0,
        "regulation_note": "Talla mínima 80 cm. Veda reproductiva compartida de noviembre a diciembre.",
        "baits_natural": "Morena mediana viva, cascarudo, boguita entera o filet fresco de boga.",
        "baits_artificial": "Crankbaits de profundidad media, señuelos rattling o banana paleta 2.",
        "image_url": "/static/species/surubi_atigrado.jpg",
        "tag_color": "#0ea5e9"
    },
    {
        "id": "spec-tararira",
        "common_name": "Tararira (Tornasolada y Lagunera)",
        "scientific_name": "Hoplias malabaricus / argentinensis",
        "family": "Erythrinidae",
        "habitat": "Saltos y remansos de tosca del Río Carcarañá (Andino, Oliveros, Parque Sarmiento), riachos y lagunas de las islas entrerrianas (Charigüé).",
        "description": "Cazador implacable de emboscada. Posee una cabeza robusta, mandíbula inferior prominente con colmillos afilados como agujas y cuerpo cilíndrico. En el Carcarañá destaca por su bravura luchando entre las piedras y cascadas.",
        "seasonal_behavior": "Muy activa en días soleados de calor con agua quieta o remansos. Ataca agresivamente en superficie. Con temperaturas bajo 14°C entra en letargo invernal enterrándose en el fango.",
        "min_size_cm": 42.0,
        "regulation_note": "Veda reproductiva estricta (1 de noviembre al 31 de diciembre en Santa Fe). Se recomienda devolución total con señuelos sin rebaba.",
        "baits_natural": "Filet de dientudo fresco, tripa de pollo, mojarra viva, corazón vacuno cortado en tiritas.",
        "baits_artificial": "Ranas de goma huecas anti-enganche (hollow body frogs), Poppers de superficie, Paseantes 'Zara', señuelos articulados y cucharas ondulantes con trailer de goma.",
        "image_url": "/static/species/tararira.jpg",
        "tag_color": "#10b981"
    },
    {
        "id": "spec-boga",
        "common_name": "Boga de Piedra / Boga de Canal",
        "scientific_name": "Megaleporinus obtusidens",
        "family": "Anostomidae",
        "habitat": "Zonas de tosca, muelles, pilotes de puentes, barcos amarrados y veriles con correntada media en Rosario y San Lorenzo.",
        "description": "Una de las especies más divertidas y técnicas de pescar en el Gran Rosario. Dientes incisivos similares a los humanos capaces de cortar líneas y triturar caracoles. Combate con corridas vigorosas y cabeceos constantes que exigen equipos equilibrados.",
        "seasonal_behavior": "Especie típica de primavera y verano (octubre a abril). Pica mejor con agua templada y río estacionario o en bajante suave.",
        "min_size_cm": 45.0,
        "regulation_note": "Cupo máximo de 5 piezas por pescador con licencia al día. Talla mínima 45 cm.",
        "baits_natural": "Masa dulce cocida (harina de maíz, harina de trigo, vainilla, azúcar y queso rallado), maíz hervido fermentado, dados de corazón vacuno, caracol de tosca pisado, cubos de salame.",
        "baits_artificial": "Micro jigs, ninfas pesadas en fly fishing y pequeños vinilos de 1.5 pulgadas tocando fondo.",
        "image_url": "/static/species/boga.jpg",
        "tag_color": "#f59e0b"
    },
    {
        "id": "spec-pacu",
        "common_name": "Pacú del Paraná",
        "scientific_name": "Piaractus mesopotamicus",
        "family": "Serrasalmidae",
        "habitat": "Corredores de sauces e ingás en las islas, entradas de arroyos y remansos con árboles frutales.",
        "description": "El 'lechón del río'. Pez de cuerpo redondeado discoidal y mandíbula poderosa con dentición molariforme adaptada para romper frutos, caracoles y semillas. Pelea con fuerza descomunal en plano horizontal.",
        "seasonal_behavior": "Máxima actividad en pleno verano (diciembre a marzo). Se alimenta activamente cuando caen frutos de ingá o mora al agua.",
        "min_size_cm": 48.0,
        "regulation_note": "Talla mínima 48 cm. Especie protegida, pesca con devolución recomendada.",
        "baits_natural": "Fruto de ingá, quinotos al almíbar, masa de maíz con grasa, bolitas de queso o corazón vacuno.",
        "baits_artificial": "Moscas atadas simulando frutos (frutas de ciervo o foam) y señuelos crankbaits pequeños.",
        "image_url": "/static/species/pacu.jpg",
        "tag_color": "#d97706"
    },
    {
        "id": "spec-carpa",
        "common_name": "Carpa Común y Espejo",
        "scientific_name": "Cyprinus carpio",
        "family": "Cyprinidae",
        "habitat": "Aguas remansadas y pozones profundos del Río Carcarañá (Parque Sarmiento, Pueblo Andino) y arroyos como Saladillo y San Lorenzo.",
        "description": "Pez aclimatado de gran tamaño (habitualmente entre 4 y 12 kg). Cuerpo robusto, lomo arqueado, escamas doradas y dos barbillones sensoriales en la comisura de la boca protráctil. Ofrece peleas de fondo de extrema fuerza física y resistencia prolongada.",
        "seasonal_behavior": "Alimentación activa todo el año, intensificándose en verano. Succiona el sedimento buscando granos, insectos y materia vegetal.",
        "min_size_cm": 0.0,
        "regulation_note": "Especie exótica asilvestrada sin veda ni cupo restrictivo. Excelente para captura deportiva y extracción libre.",
        "baits_natural": "Masa de harinado para carpa (con polenta, harina de soja, esencia de vainilla y orégano), maíz dulce en conserva (lata), masa con dulce de batata, lombriz de tierra.",
        "baits_artificial": "Línea con mosca tipo Woolly Bugger o ninfas de quironómidos cuando se alimentan en superficie o veriles bajos.",
        "image_url": "/static/species/carpa.jpg",
        "tag_color": "#a855f7"
    },
    {
        "id": "spec-pati",
        "common_name": "Patí Gigante",
        "scientific_name": "Luciopimelodus pati",
        "family": "Pimelodidae",
        "habitat": "Grandes pozas y canal principal de navegación del Río Paraná en Rosario, San Lorenzo y Timbúes.",
        "description": "Siluriforme de color azulado plateado en el lomo y blanco en el vientre, de cuerpo fino y estilizado con aletas afiladas. Puede superar los 15 kg de peso en las canaletas profundas del Paraná.",
        "seasonal_behavior": "Especie de aguas frías a templadas. Pica intensamente tanto en invierno como en verano, especialmente de noche anclado en la canaleta.",
        "min_size_cm": 50.0,
        "regulation_note": "Talla mínima legal 50 cm en Santa Fe y Entre Ríos.",
        "baits_natural": "Sábalo podrido con fuerte olor ('filet de sábalo madurado'), tripa de sábalo fresca o fétida, anguila y corazón vacuno cortado en tiras.",
        "baits_artificial": "Rara vez ataca artificiales salvo jigs pesados raspando el lecho en deriva.",
        "image_url": "/static/species/pati.jpg",
        "tag_color": "#3b82f6"
    },
    {
        "id": "spec-manduvi",
        "common_name": "Manduví / Manduvé",
        "scientific_name": "Ageneiosus militaris / inermis",
        "family": "Auchenipteridae",
        "habitat": "Aguas correntosas de media agua, bocas de arroyos (San Lorenzo, Saladillo) y pasos entre islas.",
        "description": "Bagre cazador veloz de cuerpo alargado comprimido lateralmente, boca muy ancha y mandíbula provista de dientes finos. Su carne es blanca y muy codiciada gastronómicamente.",
        "seasonal_behavior": "Aparece con fuerza en los meses estivales. Caza en cardúmenes mojarras y forrajeros a media agua al anochecer.",
        "min_size_cm": 35.0,
        "regulation_note": "Respetar talla mínima de 35 cm.",
        "baits_natural": "Mojarra viva enhebrada de la cola, filet de dientudo o sardina de río.",
        "baits_artificial": "Cucharitas giratorias N° 3 y 4 con pluma roja, señuelos Minnows pequeños de 7 cm en media agua.",
        "image_url": "/static/species/manduvi.jpg",
        "tag_color": "#ec4899"
    },
    {
        "id": "spec-variada",
        "common_name": "Moncholo y Bagre Amarillo",
        "scientific_name": "Pimelodus albicans / maculatus",
        "family": "Pimelodidae",
        "habitat": "Toda la costa y lecho de fondo de Rosario, San Lorenzo, arroyos y el Río Carcarañá.",
        "description": "La variada de cuero más popular y tradicional de la costa santafesina. Provistos de espinas pectorales y dorsal aserradas punzantes que requieren precaución al manipularlos.",
        "seasonal_behavior": "Pesca constante todo el año. Pica con gran facilidad en jornadas familiares de costa o embarcado.",
        "min_size_cm": 30.0,
        "regulation_note": "Pesca libre con cupo reglamentario de 15 piezas variadas.",
        "baits_natural": "Lombriz rubia de tierra o dedo en racimo abundante, corazón, tripa de pollo, pasta de hígado.",
        "baits_artificial": "No aplica usualmente.",
        "image_url": "/static/species/bagre_amarillo.jpg",
        "tag_color": "#84cc16"
    }
]

# Catálogo completo de Armado de Líneas recomendadas
TACKLE_RIGS_CATALOG = [
    {
        "id": "rig-boga-rosario",
        "name": "Línea de Fondo Corrediza para Boga (Rosario & San Lorenzo)",
        "target_species": "Boga de Piedra, Pacú chico",
        "environment": "Zonas de tosca, muelles de Costa Alta, pilotes del puente y barcos",
        "modality": "Pesca de Fondo / Espera Técnica",
        "rod": "Caña de 2.10m a 2.40m, acción blanda a media, de 10-20 lbs (puntera sensible para detectar el sutil toque de la boga).",
        "reel": "Rotativo perfil bajo o frontal tamaño 2500 a 3000 con freno micrométrico suave.",
        "main_line": "Nylon 0.30mm a 0.35mm o Multifilamento 0.18mm con salida de nylon.",
        "leader": "Brazola de fluorocarbono de 40 a 60 cm de 0.30mm a 0.35mm.",
        "hook": "Anzuelo forjado corto y fuerte tipo Chinu N° 3 al 5 o Maruseigo N° 12 a 14.",
        "assembly_instructions": [
            "1. Enhebrar en la línea madre un plomo pasante corredizo (tipo torpedo u oliva) de 30 a 50 gramos.",
            "2. Colocar una perlita plástica amortiguadora para proteger el nudo.",
            "3. Atar un esmerillón micrométrico N° 7 u 8 con nudo Palomar o Grinner.",
            "4. Del otro extremo del esmerillón, atar la brazola de fluorocarbono (40-60 cm).",
            "5. Atar el anzuelo de boga y colocar una pequeña bolita de masa dulce compacta o enhebrar 2 granos de maíz blando hervido."
        ],
        "tips": "No dar tirones violentos al clavar. Dejar que la boga chupe el maíz/masa unos segundos y clavar con un movimiento firme y progresivo de la caña hacia arriba.",
        "icon": "boga"
    },
    {
        "id": "rig-dorado-bait",
        "name": "Línea de Baitcasting & Spinning para Dorado (Remanso Valerio)",
        "target_species": "Gran Dorado, Chafalote",
        "environment": "Correderas de tosca, remansos de puentes, bocas de arroyos",
        "modality": "Baitcasting / Spinning Activo",
        "rod": "Caña de 6 a 6.6 pies (1.80m - 1.98m), acción rápida, de 12-25 lbs (grafito IM7 o superior).",
        "reel": "Reel huevito rotativo de perfil bajo con alta relación de giro (7.1:1 o más) y buen freno de arrastre.",
        "main_line": "Multifilamento de 8 hebras 0.22mm a 0.28mm (30 a 40 lbs).",
        "leader": "Líder de alambre de acero termosellado de 25 a 30 cm de 30 lbs con mosquetón (snap) reforzado.",
        "hook": "Anzuelos triples reforzados 3X o 4X en el señuelo artificial.",
        "assembly_instructions": [
            "1. Conectar la línea madre al esmerillón del cable de acero mediante nudo Palomar reforzado.",
            "2. Utilizar un cable de acero termosellado de 30 lbs que soporte la dentadura aserrada del dorado.",
            "3. En el extremo inferior colocar un snap de alta resistencia sin esmerillón para dar libertad de nado al artificial.",
            "4. Colocar señuelo Minnow tipo paleta 1 o 2 (11 a 13 cm) o lipless vibrador."
        ],
        "tips": "En el Remanso Valerio y las barrancas de Baigorria, castear cruzado a la corriente y recoger a velocidad media con toques de punta de caña (twitching) para simular un sabalito herido.",
        "icon": "dorado"
    },
    {
        "id": "rig-surubi-pesado",
        "name": "Línea de Pozón Pesado para Surubí (Timbúes & San Lorenzo)",
        "target_species": "Surubí Pintado, Patí Gigante",
        "environment": "Pozones profundos del canal troncal (8 a 15 metros)",
        "modality": "Pesca Embarcada Anclada o Deriva Lenta",
        "rod": "Caña de 2.10m a 2.40m, acción pesada de 30 a 60 lbs.",
        "reel": "Rotativo pesado tipo Abu Garcia 6500 / Penn Squall con chicharra sonora de pique.",
        "main_line": "Nylon 0.50mm - 0.60mm de alta resistencia a la abrasión o multifilamento 0.35mm.",
        "leader": "Líder de acero multifilamento de 40 lbs de 50 cm de largo.",
        "hook": "Anzuelo Live Bait o Mustad O'Shaughnessy N° 7/0 al 9/0.",
        "assembly_instructions": [
            "1. Colocar en la línea madre un plomo corredizo pesado tipo perita de 80 a 140 gramos (según la fuerza de la correntada).",
            "2. Colocar protector de nudo de goma y esmerillón reforzado de 50 lbs.",
            "3. Atar el cable de acero de 40 lbs con nudo o tubito de crimpado doble.",
            "4. Enhebrar la Morena viva pasando el anzuelo cuidadosamente por el pedúnculo caudal o la boca sin dañarla para que nade en el lecho."
        ],
        "tips": "Activar la chicharra del reel con el freno abierto. El surubí toma la morena, nada unos metros para deglutirla y luego acelera; es en ese momento donde se cierra el freno y se clava firmemente.",
        "icon": "surubi"
    },
    {
        "id": "rig-tararira-carcarana",
        "name": "Línea Anti-Enganche de Tararira (Río Carcarañá & Charigüé)",
        "target_species": "Tararira de Tosca, Doradillo",
        "environment": "Correderas de tosca con saltos (Andino), vegetación y lagunas de isla",
        "modality": "Casting Liviano de Superficie / Subsuperficie",
        "rod": "Caña de 6 pies, medium-heavy de 10-20 lbs (permite clavar con potencia en mandíbula ósea).",
        "reel": "Rotativo liviano o frontal 2000 cargado con multi de 30 lbs.",
        "main_line": "Multifilamento 0.20mm a 0.24mm (resistencia a piedras y vegetación).",
        "leader": "Líder corto de acero flexible de 15 a 20 cm de 20 lbs con mosquetón pequeño.",
        "hook": "Anzuelo offset 3/0 o 4/0 montado en goma tipo Texas anti-enganche.",
        "assembly_instructions": [
            "1. Si se pesca con carnada: utilizar una boya tipo Plop mediana de madera balsa a 30 cm del anzuelo.",
            "2. Si se pesca con artificiales: conectar el multifilamento directo al líder de acero de 15 cm.",
            "3. Utilizar ranas de goma hueca (frog) con anzuelos pegados al cuerpo para pasar sobre la tosca y camalotales sin enganchar.",
            "4. En saltos de agua de Andino, arrojar justo tras la rompiente de agua blanca."
        ],
        "tips": "En el Carcarañá, no clavar inmediatamente al ver el ataque en superficie. Esperar 1 o 2 segundos a que la tararira cierre la mandíbula y baje la cabeza.",
        "icon": "tararira"
    },
    {
        "id": "rig-carpa-carcarana",
        "name": "Línea con Cebador Coreano para Carpas (Parque Sarmiento)",
        "target_species": "Carpa Gigante (+8kg), Boga grande",
        "environment": "Pozones de fondo fangoso-arenoso aguas abajo de saltos y diques",
        "modality": "Carpmag / Fondo de Espera",
        "rod": "Caña de 2.70m a 3.30m de dos tramos, acción pesada parabólica.",
        "reel": "Frontal con sistema Baitrunner (doble freno de carrete libre).",
        "main_line": "Nylon 0.35mm de bajo estiramiento o 0.40mm.",
        "leader": "Brazoladas cortas de 5 a 8 cm de hilo trenzado suave (Dacrón 0.25mm).",
        "hook": "Anzuelos de boca ancha forjados N° 4 o 6 tipo Chinu o Carp Hooks.",
        "assembly_instructions": [
            "1. Enhebrar un resorte espiral cebador con plomo interno de 40 a 60 gramos.",
            "2. Atar esmerillón triple y conectar 2 a 4 brazoladas ultra cortas de dacrón suave.",
            "3. Amasar una bola de harinado dulce compacto alrededor del resorte.",
            "4. Clavar suavemente los anzuelos (con 1 grano de maíz cada uno) en la superficie de la bocha de masa, dejando las puntas listas para que la carpa las succione."
        ],
        "tips": "La carpa absorbe el cebador y al tragar los granos se auto-clava con el peso del resorte. Mantener la caña en posacañas con la chicharra habilitada.",
        "icon": "carpa"
    },
    {
        "id": "rig-variada-costa",
        "name": "Línea Clásica de Fondo para Variada de Costa (San Lorenzo & Rosario)",
        "target_species": "Moncholo, Bagre Amarillo, Armado",
        "environment": "Costanera central, barrancas y playas de arena",
        "modality": "Pesca de Fondo Familiar / Recreativa",
        "rod": "Caña telescópica o de 2 tramos de 2.40m a 3.00m.",
        "reel": "Frontal clásico tamaño 3000 a 4000 con nylon 0.35mm.",
        "main_line": "Nylon monofilamento 0.35mm.",
        "leader": "Madre de línea de 1 metro de nylon 0.45mm con dos rotores plásticos.",
        "hook": "2 anzuelos garra de águila serie 1210 N° 2 o 3 con brazoladas de 25 cm.",
        "assembly_instructions": [
            "1. En una madre de 1 metro de nylon 0.45mm, colocar 2 rotores separados por 35 cm con perlitas y nudos corredizos.",
            "2. En el extremo inferior colocar un mosquetón con esmerillón para la plomada.",
            "3. En los rotores, atar brazoladas de nylon 0.30mm de 20 a 25 cm con los anzuelos.",
            "4. Colocar plomada tipo perita o cajón de 50 a 80 gramos según la correntada.",
            "5. Encarnar con abundante lombriz rubia de tierra viva en forma de racimo."
        ],
        "tips": "Ideal para pescar de noche en el Campo de la Gloria de San Lorenzo o en la Costanera rosarina. Pique franco que sacude la puntera.",
        "icon": "variada"
    }
]

def init_catalog_db():
    """Inicializa y siembra las tablas de catálogo y checkpoints del pescador."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Tabla de Especies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS species_catalog (
                id TEXT PRIMARY KEY,
                common_name TEXT NOT NULL,
                scientific_name TEXT NOT NULL,
                family TEXT,
                habitat TEXT,
                description TEXT,
                seasonal_behavior TEXT,
                min_size_cm REAL,
                regulation_note TEXT,
                baits_natural TEXT,
                baits_artificial TEXT,
                image_url TEXT,
                tag_color TEXT
            );
        """)

        # 2. Tabla de Aparejos / Rigs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tackle_rigs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                target_species TEXT NOT NULL,
                environment TEXT,
                modality TEXT,
                rod TEXT,
                reel TEXT,
                main_line TEXT,
                leader TEXT,
                hook TEXT,
                assembly_instructions TEXT, -- JSON Array
                tips TEXT,
                icon TEXT
            );
        """)

        # 3. Tabla de Checkpoints Guardados del Usuario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_checkpoints (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL, -- 'species_favorite', 'rig_note', 'custom_checkpoint', 'catch'
                reference_id TEXT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 4. Tabla de Feedback Comunitario de Pique
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bite_feedback (
                id TEXT PRIMARY KEY,
                port_id TEXT NOT NULL,
                rating TEXT NOT NULL, -- 'excelente', 'regular', 'flojo'
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Sincronizar catálogo de especies con fotos locales y especies completas
        for s in SPECIES_CATALOG:
            cursor.execute("""
                INSERT OR REPLACE INTO species_catalog 
                (id, common_name, scientific_name, family, habitat, description, seasonal_behavior, min_size_cm, regulation_note, baits_natural, baits_artificial, image_url, tag_color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["id"], s["common_name"], s["scientific_name"], s["family"], s["habitat"],
                s["description"], s["seasonal_behavior"], s["min_size_cm"], s["regulation_note"],
                s["baits_natural"], s["baits_artificial"], s["image_url"], s["tag_color"]
            ))

        # Cargar aparejos si está vacía
        cursor.execute("SELECT COUNT(*) FROM tackle_rigs")
        if cursor.fetchone()[0] == 0:
            import json
            for r in TACKLE_RIGS_CATALOG:
                cursor.execute("""
                    INSERT INTO tackle_rigs 
                    (id, name, target_species, environment, modality, rod, reel, main_line, leader, hook, assembly_instructions, tips, icon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["id"], r["name"], r["target_species"], r["environment"], r["modality"],
                    r["rod"], r["reel"], r["main_line"], r["leader"], r["hook"],
                    json.dumps(r["assembly_instructions"], ensure_ascii=False), r["tips"], r["icon"]
                ))

        conn.commit()

init_catalog_db()

def list_species() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM species_catalog ORDER BY common_name ASC")
        return [dict(row) for row in cursor.fetchall()]

def list_rigs() -> List[Dict[str, Any]]:
    import json
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tackle_rigs ORDER BY name ASC")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["assembly_instructions"] = json.loads(d["assembly_instructions"])
            except:
                d["assembly_instructions"] = []
            results.append(d)
        return results

def list_checkpoints() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_checkpoints ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def create_checkpoint(data: Dict[str, Any]) -> Dict[str, Any]:
    cp_id = str(uuid.uuid4())
    cp_type = data.get("type", "custom_checkpoint")
    ref_id = data.get("reference_id")
    title = data.get("title", "Anotación de Pesca")
    content = data.get("content", "")
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_checkpoints (id, type, reference_id, title, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cp_id, cp_type, ref_id, title, content, created_at))
        conn.commit()

    return {
        "id": cp_id,
        "type": cp_type,
        "reference_id": ref_id,
        "title": title,
        "content": content,
        "created_at": created_at
    }

def delete_checkpoint(cp_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_checkpoints WHERE id = ?", (cp_id,))
        conn.commit()
        return cursor.rowcount > 0

def add_bite_feedback(port_id: str, rating: str, comment: str = "") -> Dict[str, Any]:
    """Registra el feedback de pique reportado por un pescador."""
    fb_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bite_feedback (id, port_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (fb_id, port_id, rating, comment, created_at))
        conn.commit()
    return {"id": fb_id, "port_id": port_id, "rating": rating, "created_at": created_at}

def get_bite_feedback_summary(port_id: str) -> Dict[str, Any]:
    """Calcula el consenso comunitario de pique para un puerto (últimas 48 horas)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rating, COUNT(*) as count 
            FROM bite_feedback 
            WHERE port_id = ? 
            GROUP BY rating
        """, (port_id,))
        rows = cursor.fetchall()
        counts = {"excelente": 0, "regular": 0, "flojo": 0}
        total = 0
        for r in rows:
            counts[r["rating"]] = r["count"]
            total += r["count"]

        # Ajuste de confianza comunitaria (-15 a +15 pts)
        score_adj = 0
        if total > 0:
            pct_good = counts["excelente"] / total
            pct_bad = counts["flojo"] / total
            score_adj = int((pct_good - pct_bad) * 15)

        return {
            "port_id": port_id,
            "total_reports": total,
            "counts": counts,
            "score_adjustment": score_adj,
            "sentiment": "Muy Activo" if score_adj > 5 else ("Flojo" if score_adj < -5 else "Normal")
        }

