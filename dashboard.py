#!/usr/bin/env python3
"""
Lorex Camera Dashboard
A simple self-contained server that proxies snapshot feeds from Lorex cameras
and displays them in a clean web dashboard.
Works on Linux, macOS, and Windows (just need Python 3).
"""

import http.server
import requests
import threading
import time
import sys
import os
from urllib.parse import urlparse

# ============ CONFIGURATION ============
CAMERAS = [
    {"name": "Camera 1", "ip": "192.168.1.118", "user": "admin", "pass": "Fitasafiddle"},
    {"name": "Camera 2", "ip": "192.168.1.121", "user": "admin", "pass": "Fitasafiddle"},
    {"name": "Camera 3", "ip": "192.168.1.150", "user": "admin", "pass": "Fitasafiddle"},
]
DASHBOARD_PORT = 8888
REFRESH_INTERVAL_MS = 2000
# =======================================

_auth_cache = {}
_auth_cache_lock = threading.Lock()


def get_digest_auth(url, user, password):
    now = time.time()
    with _auth_cache_lock:
        if url in _auth_cache:
            auth, expires = _auth_cache[url]
            if now < expires:
                return auth
    auth = requests.auth.HTTPDigestAuth(user, password)
    with _auth_cache_lock:
        _auth_cache[url] = (auth, now + 300)
    return auth


def fetch_snapshot(camera):
    url = f"http://{camera['ip']}/cgi-bin/snapshot.cgi"
    try:
        r = requests.get(url, auth=get_digest_auth(url, camera["user"], camera["pass"]), timeout=5)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lorex Camera Dashboard</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
    background: #0a0a0a;
    color: #fff;
    min-height: 100vh;
  }
  .header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 16px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid #0f3460;
    flex-wrap: wrap;
    gap: 10px;
  }
  .header h1 { font-size: 22px; font-weight: 600; letter-spacing: 0.5px; }
  .header h1 span { color: #e94560; }
  .header-status { font-size: 13px; color: #aaa; display: flex; align-items: center; gap: 16px; }
  .status-dot {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; background: #4ade80;
    animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 12px; padding: 12px;
    max-width: 1600px; margin: 0 auto;
  }
  @media (max-width: 480px) { .grid { grid-template-columns: 1fr; } }
  .cam-card {
    background: #111; border-radius: 10px; overflow: hidden;
    border: 1px solid #222; transition: border-color 0.3s; position: relative;
  }
  .cam-card:hover { border-color: #0f3460; }
  .cam-card.online { border-color: #0f3460; }
  .cam-header {
    padding: 10px 14px; background: #1a1a1a;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid #222;
  }
  .cam-name { font-size: 14px; font-weight: 500; }
  .cam-ip { font-size: 11px; color: #666; }
  .cam-badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
  .badge-online { background: #14532d; color: #4ade80; }
  .badge-offline { background: #450a0a; color: #f87171; }
  .cam-feed {
    width: 100%; aspect-ratio: 16/9;
    background: #000; display: flex;
    align-items: center; justify-content: center;
    overflow: hidden; position: relative;
  }
  .cam-feed img { width: 100%; height: 100%; object-fit: contain; display: block; }
  .cam-feed .placeholder { color: #333; font-size: 14px; text-align: center; padding: 20px; }
  .footer { text-align: center; padding: 20px; color: #444; font-size: 12px; }
</style>
</head>
<body>
<div class="header">
  <h1>Lorex <span>Dashboard</span></h1>
  <div class="header-status">
    <span><span class="status-dot"></span> Live</span>
    <span id="clock"></span>
  </div>
</div>
<div class="grid" id="cameraGrid"></div>
<div class="footer">Refresh every 2s</div>
<script>
const cameras = [
  { name: "Camera 1", ip: "192.168.1.118", id: 0 },
  { name: "Camera 2", ip: "192.168.1.121", id: 1 },
  { name: "Camera 3", ip: "192.168.1.150", id: 2 }
];
const grid = document.getElementById('cameraGrid');

function createCard(cam) {
  const card = document.createElement('div');
  card.className = 'cam-card';
  card.id = 'cam-' + cam.id;
  card.innerHTML = `
    <div class="cam-header">
      <div>
        <div class="cam-name">${cam.name}</div>
        <div class="cam-ip">${cam.ip}</div>
      </div>
      <span class="cam-badge badge-offline" id="badge-${cam.id}">Connecting...</span>
    </div>
    <div class="cam-feed" id="feed-${cam.id}">
      <div class="placeholder">Loading...</div>
    </div>`;
  return card;
}

cameras.forEach(cam => grid.appendChild(createCard(cam)));

function updateFeeds() {
  cameras.forEach(cam => {
    const img = new Image();
    img.onload = function() {
      const feed = document.getElementById('feed-' + cam.id);
      // Remove old content
      while (feed.firstChild) feed.removeChild(feed.firstChild);
      feed.appendChild(img);
      document.getElementById('cam-' + cam.id).className = 'cam-card online';
      const badge = document.getElementById('badge-' + cam.id);
      badge.className = 'cam-badge badge-online';
      badge.textContent = 'Live';
    };
    img.onerror = function() {
      const feed = document.getElementById('feed-' + cam.id);
      if (!feed.querySelector('img') || !feed.querySelector('img').complete) {
        feed.innerHTML = '<div class="placeholder">No Signal</div>';
        document.getElementById('cam-' + cam.id).className = 'cam-card';
        const badge = document.getElementById('badge-' + cam.id);
        badge.className = 'cam-badge badge-offline';
        badge.textContent = 'Offline';
      }
    };
    img.src = '/snapshot/' + cam.id + '?_=' + Date.now();
  });
}

function updateClock() {
  document.getElementById('clock').textContent = new Date().toLocaleTimeString();
}

updateFeeds();
setInterval(updateFeeds, """ + str(REFRESH_INTERVAL_MS) + """);
setInterval(updateClock, 1000);
updateClock();
</script>
</body>
</html>"""


class DashboardHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        if not args[0].startswith("GET /snapshot/"):
            print(f"[{self.log_date_time_string()}] {args[0]} {args[1]}")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))

        elif path.startswith("/snapshot/"):
            cam_id_str = path.split("/snapshot/")[-1].split("?")[0]
            try:
                cam_id = int(cam_id_str)
                if cam_id < 0 or cam_id >= len(CAMERAS):
                    self.send_error(404)
                    return
            except ValueError:
                self.send_error(400)
                return

            camera = CAMERAS[cam_id]
            data = fetch_snapshot(camera)

            if data:
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                # 1x1 grey pixel JPEG
                self.wfile.write(bytes([
                    0xFF,0xD8,0xFF,0xE0,0x00,0x10,0x4A,0x46,0x49,0x46,0x00,0x01,0x01,0x00,0x00,0x01,
                    0x00,0x01,0x00,0x00,0xFF,0xDB,0x00,0x43,0x00,0x08,0x06,0x06,0x07,0x06,0x05,0x08,
                    0x07,0x07,0x07,0x09,0x09,0x08,0x0A,0x0C,0x14,0x0D,0x0C,0x0B,0x0B,0x0C,0x19,0x12,
                    0x13,0x0F,0x14,0x1D,0x1A,0x1F,0x1E,0x1D,0x1A,0x1C,0x1C,0x20,0x24,0x2E,0x27,0x20,
                    0x22,0x2C,0x23,0x1C,0x1C,0x28,0x37,0x29,0x2C,0x30,0x31,0x34,0x34,0x34,0x1F,0x27,
                    0x39,0x3D,0x38,0x32,0x3C,0x2E,0x33,0x34,0x32,0xFF,0xC0,0x00,0x0B,0x08,0x00,0x01,
                    0x00,0x01,0x01,0x01,0x11,0x00,0xFF,0xC4,0x00,0x1F,0x00,0x00,0x01,0x05,0x01,0x01,
                    0x01,0x01,0x01,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x02,0x03,0x04,
                    0x05,0x06,0x07,0x08,0x09,0x0A,0x0B,0xFF,0xC4,0x00,0xB5,0x10,0x00,0x02,0x01,0x03,
                    0x03,0x02,0x04,0x03,0x05,0x05,0x04,0x04,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x02,
                    0x03,0x11,0x04,0x05,0x21,0x31,0x06,0x12,0x41,0x51,0x07,0x61,0x71,0x13,0x22,0x32,
                    0x81,0x08,0x14,0x42,0x91,0xA1,0xB1,0xC1,0x09,0x23,0x33,0x52,0xF0,0x15,0x62,0x72,
                    0xD1,0x0A,0x16,0x24,0x34,0xE1,0x25,0xF1,0x17,0x18,0x19,0x1A,0x26,0x27,0x28,0x29,
                    0x2A,0x35,0x36,0x37,0x38,0x39,0x3A,0x43,0x44,0x45,0x46,0x47,0x48,0x49,0x4A,0x53,
                    0x54,0x55,0x56,0x57,0x58,0x59,0x5A,0x63,0x64,0x65,0x66,0x67,0x68,0x69,0x6A,0x73,
                    0x74,0x75,0x76,0x77,0x78,0x79,0x7A,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8A,0x92,
                    0x93,0x94,0x95,0x96,0x97,0x98,0x99,0x9A,0xA2,0xA3,0xA4,0xA5,0xA6,0xA7,0xA8,0xA9,
                    0xAA,0xB2,0xB3,0xB4,0xB5,0xB6,0xB7,0xB8,0xB9,0xBA,0xC2,0xC3,0xC4,0xC5,0xC6,0xC7,
                    0xC8,0xC9,0xCA,0xD2,0xD3,0xD4,0xD5,0xD6,0xD7,0xD8,0xD9,0xDA,0xE1,0xE2,0xE3,0xE4,
                    0xE5,0xE6,0xE7,0xE8,0xE9,0xEA,0xF1,0xF2,0xF3,0xF4,0xF5,0xF6,0xF7,0xF8,0xF9,0xFA,
                    0xFF,0xDA,0x00,0x08,0x01,0x01,0x00,0x00,0x3F,0x00,0x7B,0x94,0x11,0x00,0x00,0x00,
                    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                    0x00,0x00,0x00,0x00,0x00,0x00,0xFF,0xD9
                ]))


def find_free_port(start=8888):
    import socket
    for port in range(start, start + 100):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("", port))
            sock.close()
            return port
        except OSError:
            sock.close()
    return start


if __name__ == "__main__":
    port = find_free_port(DASHBOARD_PORT)
    server = http.server.HTTPServer(("0.0.0.0", port), DashboardHandler)
    print()
    print("=" * 58)
    print("  Lorex Camera Dashboard")
    print("=" * 58)
    for i, cam in enumerate(CAMERAS):
        print(f"   Camera {i+1}:  {cam['ip']}")
    print(f"   Dashboard: http://localhost:{port}")
    print("   Press Ctrl+C to stop")
    print("=" * 58)
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
