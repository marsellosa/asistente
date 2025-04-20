const CACHE_NAME = 'club-cache-v1';
const urlsToCache = [
    '/',
    '/static/AdminLTE/dist/css/adminlte.css',
    '/static/AdminLTE/dist/js/adminlte.js',
    '/static/web-app-manifest-192x192.png',
    '/static/web-app-manifest-512x512.png'
    // Agrega otros archivos estáticos esenciales
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});


self.addEventListener('fetch', event => {
event.respondWith(
    caches.match(event.request).then(resp => {
    return resp || fetch(event.request);
    })
);
});
  