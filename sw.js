// VoucherPro Service Worker — K-7 auto-update
// Estrategia: network-first para index.html (siempre busca la última versión),
// cache-first para assets estáticos. Notifica al cliente cuando hay update.

const CACHE_NAME = 'voucherpro-v1';
const APP_SHELL = ['./'];

self.addEventListener('install', (e) => {
  // Activate new SW immediately (no esperar a cerrar todas las pestañas)
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(APP_SHELL)));
});

self.addEventListener('activate', (e) => {
  // Tomar control de clientes existentes
  e.waitUntil(
    Promise.all([
      self.clients.claim(),
      caches.keys().then(keys => Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      ))
    ])
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  // Solo manejamos same-origin (no CDN, no APIs externas)
  if (url.origin !== self.location.origin) return;

  // Network-first para HTML (siempre buscamos última versión)
  if (e.request.mode === 'navigate' || e.request.destination === 'document') {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          // Cache para offline fallback
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request).then(r => r || caches.match('./')))
    );
    return;
  }
  // Cache-first para otros recursos
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});

self.addEventListener('message', (e) => {
  if (e.data === 'SKIP_WAITING') self.skipWaiting();
});
