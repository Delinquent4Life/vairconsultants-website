// VAIR Card: keeps the card working without signal (VAIR Website, 22 Oct 2026)
const C = "vair-card-1";
const FILES = ["/card/", "/card/qr.png", "/card/icon-192.png", "/card/manifest.webmanifest"];
self.addEventListener("install", e => e.waitUntil(caches.open(C).then(c => c.addAll(FILES))));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== C).map(x => caches.delete(x))))));
self.addEventListener("fetch", e => {
  if (!e.request.url.includes("/card/")) return;
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(C).then(c => c.put(e.request, copy)); return r; }).catch(() => caches.match(e.request)));
});
