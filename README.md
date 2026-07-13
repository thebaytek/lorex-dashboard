# Lorex Camera Dashboard

A simple web dashboard to view all your Lorex cameras at once. Snapshots auto-refresh every 2 seconds.

## Quick Start

### Linux / macOS
```bash
./start.sh
# or: python3 dashboard.py
```

### Windows
Double-click `start.bat` (Python 3 required from [python.org](https://python.org))

Then open **http://localhost:8888** in your browser.

## How It Works

The dashboard runs a small Python web server that:
1. Proxies snapshot requests to each camera (handles Digest authentication)
2. Serves a clean dark-themed HTML dashboard
3. Auto-refreshes all 3 camera feeds every 2 seconds

## Cameras

| Camera | IP Address |
|--------|------------|
| Camera 1 | `192.168.1.118` |
| Camera 2 | `192.168.1.121` |
| Camera 3 | `192.168.1.150` |

## Moving to a Different Network

If the cameras get different IPs on another network, edit the `CAMERAS` list at the top of `dashboard.py`.

## Requirements

- Python 3.6+
- `requests` library (auto-installed by launcher scripts)
