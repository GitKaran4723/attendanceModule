/**
 * Service Worker for PWA
 * Handles caching and offline functionality
 */

const CACHE_NAME = 'bca-bub-pwa-v4';
const urlsToCache = [
  '/',
  '/welcome',
  '/admissions',
  '/about',
  '/login',
  '/static/css/style.css',
  '/static/css/public.css',
  '/static/js/app.js',
  '/static/js/public.js',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://fonts.googleapis.com/icon?family=Material+Icons',
  'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
];


/**
 * Install Event
 * Caches essential files when service worker is installed
 */
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching files');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

/**
 * Activate Event
 * Cleans up old caches when a new service worker activates
 */
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');

  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache');
            return caches.delete(cache);
          }
        })
      );
    })
  );

  return self.clients.claim();
});

/**
 * Fetch Event
 * Intercepts network requests and serves cached content when offline
 * Strategy: Network First, falling back to Cache
 */
self.addEventListener('fetch', event => {
  // Skip POST requests - they should go directly to server
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip API requests - they should always be fresh
  if (event.request.url.includes('/api/')) {
    return;
  }

  // Handle Google Fonts and Material Icons
  if (event.request.url.includes('fonts.googleapis.com') ||
    event.request.url.includes('fonts.gstatic.com')) {
    event.respondWith(
      caches.match(event.request).then(response => {
        return response || fetch(event.request).then(fetchResponse => {
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, fetchResponse.clone());
            return fetchResponse;
          });
        });
      })
    );
    return;
  }

  // Skip other cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Clone the response
        const responseClone = response.clone();

        // Cache the fetched response
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, responseClone);
        });

        return response;
      })
      .catch(() => {
        // If network fails, try to return cached version
        return caches.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }

          // If no cache available, return a custom offline page (optional)
          // You can create an offline.html page for this
          return caches.match('/');
        });
      })
  );
});

/**
 * Background Sync Event (optional)
 * Handles syncing data when connection is restored
 */
self.addEventListener('sync', event => {
  if (event.tag === 'sync-attendance') {
    event.waitUntil(syncAttendance());
  }
});

/**
 * Function to sync attendance data when back online
 */
function syncAttendance() {
  // Implement your sync logic here
  console.log('Syncing attendance data...');
  return Promise.resolve();
}

/**
 * Push Notification Event (optional)
 * Handles push notifications
 */
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'BCA BUB Notification';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200]
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

/**
 * Notification Click Event
 * Handles what happens when user clicks on a notification
 */
self.addEventListener('notificationclick', event => {
  event.notification.close();

  event.waitUntil(
    clients.openWindow('/')
  );
});
