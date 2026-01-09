const CACHE_NAME = 'usumm-cache-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/feed_card_css.css',
  '/download_feed'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});
