// Remanso Service Worker - Cache & Offline Navigation
const CACHE_NAME = 'remanso-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json',
  '/static/icon-192.svg',
  '/static/icon-512.svg',
  '/static/species/dorado.jpg',
  '/static/species/surubi_pintado.jpg',
  '/static/species/surubi_atigrado.jpg',
  '/static/species/tararira.jpg',
  '/static/species/boga.jpg',
  '/static/species/pacu.jpg',
  '/static/species/carpa.jpg',
  '/static/species/pati.jpg',
  '/static/species/manduvi.jpg',
  '/static/species/bagre_amarillo.jpg',
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://unpkg.com/lucide@latest',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Remanso SW] Pre-caching offline assets');
      return cache.addAll(ASSETS_TO_CACHE).catch(err => {
        console.warn('[Remanso SW] Failed some pre-cache entries, proceeding:', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[Remanso SW] Limpiando cache viejo:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // WebSocket y solicitudes no GET no se cachean
  if (request.method !== 'GET' || url.protocol.startsWith('ws')) {
    return;
  }

  // Rutas de API: Network first, con fallback a cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Rutas estáticas y HTML: Stale-while-revalidate
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      const fetchPromise = fetch(request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return networkResponse;
      }).catch(() => cachedResponse);

      return cachedResponse || fetchPromise;
    })
  );
});
