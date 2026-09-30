# Remanso - Telemetría Náutica & Pesca Deportiva

Plataforma profesional en tiempo real para pescadores deportivos y navegantes de Argentina, especializada en el corredor **Gran Rosario, San Lorenzo y la Cuenca del Río Carcarañá** (Andino, Oliveros, Timbúes, Baigorria, Charigüé y Paso Destilería).

---

## Características Principales

1. **Telemetría Oficial Prefectura Naval Argentina en Vivo:**
   - Altura de ríos en metros, tendencia (Creciente, Bajante, Estacionario), variación en 24h y nivel de alerta oficial.
   - Histórico de 7 días con gráfico de nivel interactivo (Chart.js).

2. **Meteorología & Barómetro Satelital de Precisión (Open-Meteo):**
   - Presión atmosférica en hPa, delta barométrico ($\Delta P$) en 6 horas (estabilidad vs. frentes).
   - Velocidad y rumbo del viento en tiempo real, temperatura y humedad.
   - Diagnóstico específico de efectos de viento local (Sudestada, Pampero, Viento Norte).

3. **Cálculo Solunar & Fases Lunares Autónomo:**
   - Algoritmo astronómico que calcula fase, porcentaje de iluminación y ventanas de alimentación **Mayor** (2 horas) y **Menor** (1 hora) sin depender de APIs externas.

4. **Motor Heurístico de Índice de Pique Remanso (0% a 100%):**
   - Diagnóstico ponderado: Estabilidad barométrica (35%), tendencia hidrométrica (25%), viento y oleaje (20%), y solunar (20%).
   - Clasificación semafórica: *Excelente, Muy Favorable, Moderado, Difícil*.

5. **Mapa Interactivo con Waypoints Náuticos Persistentes:**
   - Cartografía dual: Esri Satelital HD + OpenStreetMap.
   - 10 pesqueros precargados con coordenadas exactas, especies objetivo y técnicas recomendadas.
   - Marcación de nuevos pesqueros con 1 click sobre el mapa o formulario.
   - **Exportación GPX 1.1:** Descarga directa de waypoints compatible con ecosondas náuticas Garmin, Lowrance, Simrad y Humminbird.

6. **Catálogo de Especies & Aparejos / Rigs:**
   - 8 especies emblemáticas (Dorado, Surubí, Boga, Tararira, Pacú, Mandubí, Patí, Carpa) con carnadas naturales, señuelos, hábitat y tallas mínimas reglamentarias.
   - 6 líneas técnicas ilustradas con especificaciones de caña, reel, línea madre, líder de acero y anzuelos.

7. **Centro de Seguridad Náutica & SOS Prefectura (Línea 106):**
   - Coordenadas GPS en formato Grados, Minutos y Segundos (DMS) listas para dictar por **Radio VHF Marino Canal 16 (156.800 MHz)**.
   - Llamada directa a Emergencias Náuticas 106 y destacamentos locales de Rosario y San Lorenzo.

8. **Ficha de Captura Digital (Certificado para WhatsApp e Instagram):**
   - Generador gráfico en HTML5 Canvas (resolución HD 4:5 / Story).
   - Estampa automáticamente la especie, peso, talla, pesquero, modalidad (Pesca & Devolución) y la **telemetría oficial del río en el momento exacto**.
   - Descarga directa en PNG y botón de compartir en redes sociales.

9. **Soporte PWA (Progressive Web App) & Offline-First:**
   - Manifiesto e iconos vectoriales SVG listos para "Instalar en pantalla de inicio" en Android e iOS.
   - Service Worker (`sw.js`) con estrategia stale-while-revalidate para navegar y consultar pesqueros aún sin cobertura de datos móviles en la isla.
   - Doble capa de persistencia: Base de datos SQLite (`data/pescapp.db`) + `localStorage`.

10. **Sintetizador Web Audio de Campana de Pique:**
    - Sonido armónico de campanilla de caña generado por código con la Web Audio API (sin archivos de audio externos).

---

## Cómo Ejecutar el Proyecto

### 1. Iniciar el Servidor Uvicorn
Desde la raíz del proyecto:
```powershell
cd C:\Users\juanp\.gemini\antigravity\scratch\pescapp-realtime
.\.venv\Scripts\uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Abrir en el Navegador
Accede a:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## Endpoints de la API REST & WebSocket

- `GET /` : Aplicación Web Remanso (PWA).
- `GET /manifest.json` : Manifiesto PWA para instalación en móviles.
- `GET /sw.js` : Service Worker con cache offline.
- `GET /api/ports` : Lista de pesqueros y puertos configurados en la cuenca.
- `GET /api/metrics/{port_id}` : Telemetría consolidada en vivo e Índice de Pique.
- `GET /api/river-history/{port_id}` : Histórico de 7 días de Prefectura Naval.
- `GET /api/spots` : Lista de pesqueros guardados en SQLite.
- `POST /api/spots` : Crear nuevo pesquero persistente.
- `DELETE /api/spots/{id}` : Eliminar pesquero.
- `GET /api/spots/export/gpx` : Exportar waypoints en formato GPX 1.1 para ecosondas.
- `GET /api/species` : Catálogo de especies autóctonas.
- `GET /api/tackle-rigs` : Catálogo de armado de líneas y aparejos.
- `GET /api/checkpoints` : Bitácora de anotaciones y capturas.
- `POST /api/checkpoints` : Registrar nuevo checkpoint o captura.
- `DELETE /api/checkpoints/{id}` : Eliminar checkpoint.
- `WS /ws/{port_id}` : Flujo en tiempo real con latido continuo cada 10s.
