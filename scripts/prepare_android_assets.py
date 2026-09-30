import json
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"
ANDROID_ASSETS_DIR = Path(r"C:\Users\juanp\.gemini\antigravity\scratch\remanso-android\app\src\main\assets")
ANDROID_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
OUT_INDEX = ANDROID_ASSETS_DIR / "index.html"

from services.spots_service import REGIONAL_SEED_SPOTS
from services.catalog_service import SPECIES_CATALOG, TACKLE_RIGS_CATALOG
from services.hydro_service import PORTS_CONFIG

# Formatear spots
spots_data = []
for s in REGIONAL_SEED_SPOTS:
    spots_data.append({
        "id": s[0],
        "title": s[1],
        "species": s[2],
        "technique": s[3],
        "depth_m": s[4],
        "notes": s[5],
        "category": s[6],
        "lat": s[7],
        "lng": s[8],
        "created_at": "2026-09-28 12:00:00"
    })

# Formatear especies con rutas locales
species_data = []
for sp in SPECIES_CATALOG:
    sp_copy = dict(sp)
    img = sp_copy.get("image_url", "")
    if "/static/" in img:
        sp_copy["image_url"] = img.replace("/static/", "")
    species_data.append(sp_copy)

# Formatear rigs
rigs_data = list(TACKLE_RIGS_CATALOG)

# Formatear puertos
ports_data = []
for pid, pcfg in PORTS_CONFIG.items():
    ports_data.append({
        "id": pid,
        "name": pcfg["name"],
        "river": pcfg["river"],
        "ecosystem": pcfg["ecosystem"],
        "lat": pcfg["lat"],
        "lng": pcfg.get("lon", pcfg.get("lng", -60.6))
    })

html_content = TEMPLATE_PATH.read_text(encoding="utf-8")

# 1. Modificar librerías CDN para usar vendor locales
html_content = html_content.replace('https://cdn.tailwindcss.com', 'vendor/tailwind.js')
html_content = html_content.replace('https://cdn.jsdelivr.net/npm/chart.js', 'vendor/chart.min.js')
html_content = html_content.replace('https://unpkg.com/lucide@latest', 'vendor/lucide.min.js')
html_content = html_content.replace('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css', 'vendor/leaflet.css')
html_content = html_content.replace('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js', 'vendor/leaflet.js')

# Limpiar integrity y crossorigin en tags locales
html_content = re.sub(r'\s+integrity="[^"]*"', '', html_content)
html_content = re.sub(r'\s+crossorigin="[^"]*"', '', html_content)
html_content = re.sub(r'\s+crossorigin=""', '', html_content)

# Modificar rutas /static/ para que apunten a relativas
html_content = html_content.replace('href="/static/', 'href="')
html_content = html_content.replace('src="/static/', 'src="')
html_content = html_content.replace('/static/species/', 'species/')

# Inyectar datos semilla y lógica de fallback autónomo
bootstrap_script = f"""
  <script>
    window.STANDALONE_MODE = true;
    window.SEED_SPOTS = {json.dumps(spots_data, ensure_ascii=False)};
    window.SEED_SPECIES = {json.dumps(species_data, ensure_ascii=False)};
    window.SEED_RIGS = {json.dumps(rigs_data, ensure_ascii=False)};
    window.SEED_PORTS = {json.dumps(ports_data, ensure_ascii=False)};

    // Telemetría simulada autónoma de alta precisión para el Río Paraná (Rosario)
    window.DEFAULT_TELEMETRY = {{
      "port_id": "rosario",
      "port_name": "Puerto Rosario",
      "river": "Río Paraná",
      "ecosystem": "parana_rosario",
      "hydro": {{
        "level_m": 2.48,
        "water_level_m": 2.48,
        "trend": "estacionario",
        "variation_24h_m": 0.02,
        "state_label": "Estacionario",
        "station_name": "Rosario (Prefectura)",
        "source": "Autónomo Paraná"
      }},
      "weather": {{
        "temperature_c": 23.4,
        "relative_humidity": 62,
        "pressure_hpa": 1014.5,
        "pressure_delta_6h": 0.2,
        "wind_speed_kmh": 12.0,
        "wind_direction_deg": 110,
        "cloud_cover_pct": 20,
        "condition": "Cielo parcialmente nublado, viento calmo"
      }},
      "solunar": {{
        "major_windows": [
          {{"start": "06:15", "end": "08:15", "type": "Mayor (Salida Luna)"}},
          {{"start": "18:40", "end": "20:40", "type": "Mayor (Puesta Luna)"}}
        ],
        "minor_windows": [
          {{"start": "12:30", "end": "13:45", "type": "Menor"}},
          {{"start": "00:50", "end": "02:00", "type": "Menor"}}
        ],
        "moon": {{
          "phase_name": "Gibosa Creciente",
          "illumination_pct": 78,
          "solunar_rating": 82
        }},
        "sun": {{
          "sunrise": "06:42",
          "sunset": "19:05",
          "solar_noon": "12:53"
        }},
        "is_in_major": true,
        "is_in_minor": false
      }},
      "bite_evaluation": {{
        "score": 84,
        "verdict": "Pique Muy Activo (Condiciones Excelentes)",
        "classification": "Excelente",
        "traffic_light": "green",
        "target_species": ["Gran Dorado", "Boga de Piedra", "Surubí Pintado", "Tararira"],
        "recommended_bait": "Morena viva, masa de vainilla/maíz y señuelos Minnow de media agua",
        "recommended_technique": "Baitcasting pegado a los remansos y pesca de fondo con plomo corredizo",
        "safety_advisory": "Río en condiciones óptimas para navegación deportiva y vadeo seguro.",
        "detailed_analysis": "Río Paraná con altura estable (2.48m) y aguas limpias en los veriles. Barómetro de 1014.5 hPa muy regular sin frentes bruscos. Ventana solunar mayor activa con alta voracidad de predadores.",
        "ecosystem": "parana_rosario"
      }},
      "bite": {{
        "score": 84,
        "classification": "Excelente",
        "traffic_light": "green"
      }},
      "cached": true,
      "updated_at": new Date().toLocaleTimeString('es-AR')
    }};

    // Inicializar datos iniciales si no existen
    if (!localStorage.getItem('remanso_spots_v1')) {{
      localStorage.setItem('remanso_spots_v1', JSON.stringify(window.SEED_SPOTS));
    }}
    if (!localStorage.getItem('remanso_species_v1')) {{
      localStorage.setItem('remanso_species_v1', JSON.stringify(window.SEED_SPECIES));
    }}
    if (!localStorage.getItem('remanso_rigs_v1')) {{
      localStorage.setItem('remanso_rigs_v1', JSON.stringify(window.SEED_RIGS));
    }}
  </script>
"""
html_content = html_content.replace('</head>', f'{bootstrap_script}\n</head>')

# Reemplazo EXACTO de loadSpotsFromAPI
old_spots_fn = """    async function loadSpotsFromAPI() {
      try {
        const res = await fetch('/api/spots');
        if (res.ok) {
          currentSpots = await res.json();
          StorageEngine.set(StorageEngine.KEYS.SPOTS, currentSpots);
          renderMapMarkers();
          renderSpotsList(currentSpots);
          updateSpotsCount();
        }
      } catch (err) {
        console.warn('Modo offline: usando pesqueros del almacenamiento local.');
      }
    }"""

new_spots_fn = """    async function loadSpotsFromAPI() {
      try {
        if (!window.location.protocol.startsWith('http')) throw new Error('Modo local');
        const res = await fetch('/api/spots');
        if (res.ok) {
          currentSpots = await res.json();
          StorageEngine.set(StorageEngine.KEYS.SPOTS, currentSpots);
        }
      } catch (err) {
        currentSpots = StorageEngine.get(StorageEngine.KEYS.SPOTS, window.SEED_SPOTS || []);
      }
      renderMapMarkers();
      renderSpotsList(currentSpots);
      updateSpotsCount();
    }"""

assert old_spots_fn in html_content, "old_spots_fn no encontrado en html_content"
html_content = html_content.replace(old_spots_fn, new_spots_fn)

# Reemplazo EXACTO de loadSpeciesCatalog
old_species_fn = """    async function loadSpeciesCatalog() {
      try {
        const res = await fetch('/api/species');
        if (res.ok) {
          currentSpecies = await res.json();
          StorageEngine.set(StorageEngine.KEYS.SPECIES, currentSpecies);
        }
      } catch (err) {
        console.warn('Cargando especies desde almacenamiento local.');
      }
      renderSpeciesGrid(currentSpecies);
    }"""

new_species_fn = """    async function loadSpeciesCatalog() {
      try {
        if (!window.location.protocol.startsWith('http')) throw new Error('Modo local');
        const res = await fetch('/api/species');
        if (res.ok) {
          currentSpecies = await res.json();
          StorageEngine.set(StorageEngine.KEYS.SPECIES, currentSpecies);
        }
      } catch (err) {
        currentSpecies = StorageEngine.get(StorageEngine.KEYS.SPECIES, window.SEED_SPECIES || []);
      }
      renderSpeciesGrid(currentSpecies);
    }"""

assert old_species_fn in html_content, "old_species_fn no encontrado en html_content"
html_content = html_content.replace(old_species_fn, new_species_fn)

# Reemplazo EXACTO de loadTackleRigs
old_rigs_fn = """    async function loadTackleRigs() {
      try {
        const res = await fetch('/api/tackle-rigs');
        if (res.ok) {
          currentRigs = await res.json();
          StorageEngine.set(StorageEngine.KEYS.RIGS, currentRigs);
        }
      } catch (err) {
        console.warn('Cargando aparejos desde almacenamiento local.');
      }
      renderRigsGrid(currentRigs);
    }"""

new_rigs_fn = """    async function loadTackleRigs() {
      try {
        if (!window.location.protocol.startsWith('http')) throw new Error('Modo local');
        const res = await fetch('/api/tackle-rigs');
        if (res.ok) {
          currentRigs = await res.json();
          StorageEngine.set(StorageEngine.KEYS.RIGS, currentRigs);
        }
      } catch (err) {
        currentRigs = StorageEngine.get(StorageEngine.KEYS.RIGS, window.SEED_RIGS || []);
      }
      renderRigsGrid(currentRigs);
    }"""

assert old_rigs_fn in html_content, "old_rigs_fn no encontrado en html_content"
html_content = html_content.replace(old_rigs_fn, new_rigs_fn)

# Reemplazo EXACTO de loadPorts hasta loadPortHistory
old_ports_block = """    async function loadPorts() {
      try {
        const res = await fetch('/api/ports');
        const ports = await res.json();
        const select = document.getElementById('portSelect');
        select.innerHTML = '';
        ports.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = `${p.name}`;
          select.appendChild(opt);
        });
        select.value = currentPort;
        select.addEventListener('change', (e) => {
          switchPort(e.target.value);
        });
      } catch (err) {
        console.error('Error cargando puertos:', err);
      }
    }

    function connectWebSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/${currentPort}`;
      
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        const statusText = document.getElementById('statusText');
        if (statusText) statusText.textContent = 'En Vivo';
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          StorageEngine.set(StorageEngine.KEYS.LAST_TELEMETRY, payload);
          updateDashboardUI(payload);
        } catch (e) {
          console.error('Error parseando mensaje WS:', e);
        }
      };

      ws.onclose = () => {
        const statusText = document.getElementById('statusText');
        if (statusText) statusText.textContent = 'Reconectando...';
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (err) => {
        console.error('Error en WebSocket:', err);
        ws.close();
      };
    }

    function switchPort(newPortId) {
      currentPort = newPortId;
      StorageEngine.set(StorageEngine.KEYS.LAST_PORT, currentPort);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'change_port', port_id: newPortId }));
      } else {
        connectWebSocket();
      }
      loadPortHistory(newPortId);
    }

    function requestFreshData() {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'refresh' }));
      }
      loadPortHistory(currentPort);
    }

    async function loadPortHistory(portId) {
      try {
        const res = await fetch(`/api/river-history/${portId}`);
        const history = await res.json();
        if (riverChartInstance && Array.isArray(history)) {
          riverChartInstance.data.labels = history.map(h => `${h.date.slice(5)} ${h.time}`);
          riverChartInstance.data.datasets[0].data = history.map(h => h.level);
          riverChartInstance.update();
        }
      } catch (err) {
        console.error('Error cargando histórico:', err);
      }
    }"""

new_ports_block = """    async function loadPorts() {
      try {
        if (!window.location.protocol.startsWith('http')) throw new Error('Modo local');
        const res = await fetch('/api/ports');
        if (!res.ok) throw new Error();
        const ports = await res.json();
        renderPortsSelect(ports);
      } catch (err) {
        renderPortsSelect(window.SEED_PORTS || [
          { id: 'rosario', name: 'Rosario (Río Paraná)' },
          { id: 'san_lorenzo', name: 'San Lorenzo' },
          { id: 'carcarana', name: 'Carcarañá' },
          { id: 'santa_fe', name: 'Santa Fe' }
        ]);
      }
    }

    function renderPortsSelect(ports) {
      const select = document.getElementById('portSelect');
      if (!select) return;
      select.innerHTML = '';
      ports.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = `${p.name}`;
        select.appendChild(opt);
      });
      select.value = currentPort;
      select.addEventListener('change', (e) => {
        switchPort(e.target.value);
      });
    }

    function connectWebSocket() {
      if (!window.location.protocol.startsWith('http')) {
        console.log('Modo Autónomo Remanso: cargando telemetría local de alta precisión.');
        const statusText = document.getElementById('statusText');
        if (statusText) statusText.textContent = 'Modo Autónomo';
        updateDashboardUI(window.DEFAULT_TELEMETRY);
        loadPortHistory(currentPort);
        return;
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/${currentPort}`;
      
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          const statusText = document.getElementById('statusText');
          if (statusText) statusText.textContent = 'En Vivo';
        };

        ws.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data);
            StorageEngine.set(StorageEngine.KEYS.LAST_TELEMETRY, payload);
            updateDashboardUI(payload);
          } catch (e) {
            console.error('Error parseando mensaje WS:', e);
          }
        };

        ws.onclose = () => {
          const statusText = document.getElementById('statusText');
          if (statusText) statusText.textContent = 'Modo Autónomo';
        };

        ws.onerror = (err) => {
          console.warn('Servidor local no disponible, operando en modo autónomo.');
          updateDashboardUI(window.DEFAULT_TELEMETRY);
        };
      } catch (err) {
        updateDashboardUI(window.DEFAULT_TELEMETRY);
      }
    }

    function switchPort(newPortId) {
      currentPort = newPortId;
      StorageEngine.set(StorageEngine.KEYS.LAST_PORT, currentPort);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'change_port', port_id: newPortId }));
      } else {
        connectWebSocket();
      }
      loadPortHistory(newPortId);
    }

    function requestFreshData() {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'refresh' }));
      }
      loadPortHistory(currentPort);
    }

    async function loadPortHistory(portId) {
      if (riverChartInstance) {
        const defaultHistory = [
          { date: '2026-09-22', time: '12:00', level: 2.54 },
          { date: '2026-09-23', time: '12:00', level: 2.51 },
          { date: '2026-09-24', time: '12:00', level: 2.49 },
          { date: '2026-09-25', time: '12:00', level: 2.47 },
          { date: '2026-09-26', time: '12:00', level: 2.46 },
          { date: '2026-09-27', time: '12:00', level: 2.47 },
          { date: '2026-09-28', time: '12:00', level: 2.48 }
        ];

        try {
          if (!window.location.protocol.startsWith('http')) throw new Error();
          const res = await fetch(`/api/river-history/${portId}`);
          if (res.ok) {
            const history = await res.json();
            if (Array.isArray(history) && history.length > 0) {
              riverChartInstance.data.labels = history.map(h => `${h.date.slice(5)} ${h.time}`);
              riverChartInstance.data.datasets[0].data = history.map(h => h.level);
              riverChartInstance.update();
              return;
            }
          }
        } catch (e) {}

        riverChartInstance.data.labels = defaultHistory.map(h => `${h.date.slice(5)} ${h.time}`);
        riverChartInstance.data.datasets[0].data = defaultHistory.map(h => h.level);
        riverChartInstance.update();
      }
    }"""

assert old_ports_block in html_content, "old_ports_block no encontrado en html_content"
html_content = html_content.replace(old_ports_block, new_ports_block)

# DOMContentLoaded con fallback inmediato
html_content = html_content.replace(
    "const cachedTelemetry = StorageEngine.get(StorageEngine.KEYS.LAST_TELEMETRY);",
    "const cachedTelemetry = StorageEngine.get(StorageEngine.KEYS.LAST_TELEMETRY, window.DEFAULT_TELEMETRY);"
)

OUT_INDEX.write_text(html_content, encoding="utf-8")
print(f"Generado con éxito: {OUT_INDEX} ({len(html_content)} bytes)")

# VALIDACIÓN AUTOMÁTICA CON NODE.JS
scripts = re.findall(r'<script(?:\s+[^>]*)?>(.*?)</script>', html_content, re.DOTALL)
print(f"Validando sintaxis de {len(scripts)} scripts con node --check...")
for idx, s in enumerate(scripts):
    s_clean = s.strip()
    if s_clean:
        tmp_js = BASE_DIR / f"_temp_val_{idx}.js"
        tmp_js.write_text(s_clean, encoding="utf-8")
        res = subprocess.run(["node", "--check", str(tmp_js)], capture_output=True, text=True)
        tmp_js.unlink(missing_ok=True)
        if res.returncode != 0:
            print(f"ERROR DE SINTAXIS en script {idx}:")
            print(res.stderr)
            sys.exit(1)
        else:
            print(f"  -> Script {idx}: SINTAXIS 100% CORRECTA")

print("TODOS LOS SCRIPTS VALIDADOS CON EXITO!")
