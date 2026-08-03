/* ════════════════════════════════════════════════════════════════════════════
   NEXUS — Service Worker
   ======================================================================
   Strategy:
   • PRECACHE  — all same-origin assets (html/css/js/images) on install
   • NAVIGATION — network-first, fall back to cached index.html (offline)
   • SAME-ORIGIN static — cache-first with background refresh (SWR)
   • CROSS-ORIGIN (fonts) — cache-first, refreshed in background
   • Versioned cache: bump NX_CACHE when you change site files
   ════════════════════════════════════════════════════════════════════════════ */
"use strict";

const NX_CACHE = "nexus-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./404.html",
  "./manifest.webmanifest",
  "./robots.txt",
  "./sitemap.xml",
  "./css/style.css",
  "./js/main.js",
  "./assets/img/favicon.svg",
  "./assets/img/favicon.png",
  "./assets/img/avatar.webp",
  "./assets/img/avatar.jpg",
  "./assets/img/hero-bg.webp",
  "./assets/img/hero-bg.jpg",
  "./assets/img/og-cover.webp",
  "./assets/img/project-1.webp",
  "./assets/img/project-1.jpg",
  "./assets/img/project-2.webp",
  "./assets/img/project-2.jpg",
  "./assets/img/project-3.webp",
  "./assets/img/project-3.jpg",
  "./assets/img/project-4.webp",
  "./assets/img/project-4.jpg",
  "./assets/img/project-5.webp",
  "./assets/img/project-5.jpg",
  "./assets/img/project-6.webp",
  "./assets/img/project-6.jpg",
];

/* ── INSTALL: precache everything (tolerate individual failures) ── */
self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(NX_CACHE);
      // allSettled: a single flaky asset must not break the whole install
      await Promise.allSettled(ASSETS.map((url) => cache.add(url)));
      await self.skipWaiting();
    })()
  );
});

/* ── ACTIVATE: drop old caches, take control of open pages ── */
self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => k !== NX_CACHE).map((k) => caches.delete(k)));
      await self.clients.claim();
      // tell the page the offline cache is ready (client shows a toast)
      const clients = await self.clients.matchAll({ type: "window" });
      clients.forEach((client) =>
        client.postMessage({ type: "NX_OFFLINE_READY", version: NX_CACHE })
      );
    })()
  );
});

/* ── FETCH: routing ── */
self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);

  // only handle same-origin + our trusted font CDNs
  if (url.origin !== self.location.origin &&
      !/fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)) {
    return;
  }

  // Navigation: network-first, offline → cached index.html
  if (request.mode === "navigate") {
    event.respondWith(
      (async () => {
        try {
          const fresh = await fetch(request);
          const cache = await caches.open(NX_CACHE);
          cache.put("./index.html", fresh.clone());
          return fresh;
        } catch (_) {
          const cache = await caches.open(NX_CACHE);
          return (await cache.match("./index.html")) || Response.error();
        }
      })()
    );
    return;
  }

  // Static assets & fonts: cache-first + background refresh (SWR)
  event.respondWith(
    (async () => {
      const cache = await caches.open(NX_CACHE);
      const cached = await cache.match(request);
      const network = fetch(request)
        .then((response) => {
          if (response && response.ok) cache.put(request, response.clone());
          return response;
        })
        .catch(() => null);

      if (cached) return cached;
      return (await network) || Response.error();
    })()
  );
});
