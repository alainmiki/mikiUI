# Deployment Guide

This guide covers deploying MikiUI applications to production. It includes
Docker, reverse proxies, process management, HTTPS, and performance tuning.

## Table of Contents

- [Environment Configuration](#environment-configuration)
- [Docker Setup](#docker-setup)
- [Reverse Proxy (Nginx / Caddy)](#reverse-proxy)
- [Process Management](#process-management)
- [HTTPS Setup](#https-setup)
- [Database Placeholder](#database-placeholder)
- [Performance Tuning](#performance-tuning)
- [Monitoring and Logging](#monitoring-and-logging)

---

## Environment Configuration

### Environment Variables

MikiUI respects the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MIKIUI_HOST` | Bind address | `0.0.0.0` |
| `MIKIUI_PORT` | Bind port | `8000` |
| `MIKIUI_WORKERS` | Uvicorn worker count | `1` |
| `MIKIUI_LOG_LEVEL` | Logging level | `info` |
| `MIKIUI_RUNTIME` | JS runtime mode | `local` |

### Configuring via Python

```python
import os
from mikiui import MikiApp
from mikiui.backend import create_app

app = MikiApp(
    title="Production App",
    lang="en",
)

fastapi_app = create_app(
    app,
    runtime=os.getenv("MIKIUI_RUNTIME", "local"),
    cors_origins=os.getenv("MIKIUI_CORS_ORIGINS", "").split(",") or None,
)
```

### Secrets

Never hard-code secrets. Use environment variables or a secrets manager:

```python
import os
from mikiui import MikiApp

app = MikiApp(title="Secure App")
app.state.secret_key = os.getenv("SECRET_KEY")
```

---

## Docker Setup

### Dockerfile

```dockerfile
FROM python:3.14-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[build]"

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app:create_app", "--host", "0.0.0.0", "--port", "8000"]
```

If your app module is `app.py` and exports `app`:

```dockerfile
CMD ["uvicorn", "app:create_app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: "3.9"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MIKIUI_HOST=0.0.0.0
      - MIKIUI_PORT=8000
      - MIKIUI_LOG_LEVEL=info
    volumes:
      - ./static:/app/static:ro
    restart: unless-stopped

  # Optional: PostgreSQL for state persistence (MikiORM integration)
  # db:
  #   image: postgres:16-alpine
  #   environment:
  #     POSTGRES_USER: mikiui
  #     POSTGRES_PASSWORD: changeme
  #     POSTGRES_DB: mikiui
  #   volumes:
  #     - pgdata:/var/lib/postgresql/data
  #   restart: unless-stopped

# volumes:
#   pgdata:
```

### Building and Running

```bash
docker build -t my-mikiui-app .
docker run -p 8000:8000 my-mikiui-app

# Or with compose:
docker compose up -d
```

---

## Reverse Proxy

### Nginx

```nginx
server {
    listen 80;
    server_name myapp.example.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if used)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Caddy

```caddy
myapp.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

Caddy automatically provisions HTTPS certificates via Let's Encrypt.

---

## Process Management

### systemd

Create `/etc/systemd/system/mikiui.service`:

```ini
[Unit]
Description=MikiUI Application
After=network.target

[Service]
Type=notify
User=mikiui
Group=mikiui
WorkingDirectory=/opt/myapp
Environment="MIKIUI_HOST=0.0.0.0"
Environment="MIKIUI_PORT=8000"
ExecStart=/usr/local/bin/uvicorn app:create_app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mikiui
```

### supervisord

```ini
[program:mikiui]
command=uvicorn app:create_app --host 0.0.0.0 --port 8000
directory=/opt/myapp
user=mikiui
autostart=true
autorestart=true
stdout_logfile=/var/log/mikiui/stdout.log
stderr_logfile=/var/log/mikiui/stderr.log
```

### Gunicorn + Uvicorn Workers

```bash
gunicorn app:create_app \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-logfile - \
  --error-logfile -
```

---

## HTTPS Setup

### Behind a Reverse Proxy (Recommended)

Let the reverse proxy terminate TLS. Nginx + Let's Encrypt example:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d myapp.example.com
```

### Direct HTTPS with Uvicorn

```bash
uvicorn app:create_app --host 0.0.0.0 --port 8000 --ssl-keyfile /path/to/key.pem --ssl-certfile /path/to/cert.pem
```

### Force HTTPS via Middleware

```python
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

fastapi_app.add_middleware(HTTPSRedirectMiddleware)
```

---

## Database Placeholder

MikiUI does not ship with an ORM yet (MikiORM is planned). For production
state persistence, integrate your preferred database directly:

```python
from mikiui import MikiApp

app = MikiApp()

@app.on_event("startup")
async def connect_db():
    # TODO: Replace with MikiORM when available
    app.state.db = await create_engine(DATABASE_URL)

@app.on_event("shutdown")
async def disconnect_db():
    await app.state.db.dispose()
```

Recommended options:

- **PostgreSQL** — primary relational store
- **Redis** — session cache, pub/sub, rate limiting
- **SQLite** — lightweight embedded option for small apps

---

## Static Assets

### Runtime Assets

MikiUI serves framework runtime files (HTMX, Alpine.js, `miki.css`, theme CSS)
under `/_miki/runtime/`. In development, these are served directly from the
package. In production builds, they are copied to `dist/_miki/runtime/` and
can be served by any static file server or CDN.

### Component and Widget Static Files

Components and widgets can ship their own static assets (CSS, JS, images) in a
`static/` directory inside their package. MikiUI discovers these automatically
and mounts them under `/_miki/`:

```
/_miki/components/<package_name>/static/...
/_miki/widgets/<package_name>/static/...
```

The web build (`mikiui build --target web`) copies these assets into
`dist/_miki/components/` and `dist/_miki/widgets/` so the exported site is
fully self-contained.

### Project Static Directory

Any `static/` directory in your project root is automatically mounted at
`/static`. Files placed there are served as-is:

```
static/
  styles.css      -> /static/styles.css
  images/logo.png -> /static/images/logo.png
```

This is created automatically by `mikiui new plain` and works without any
additional configuration.

### Custom Static Mounts

For additional static directories, use `app.mount_static()`:

```python
app.mount_static("/media", "./media")
app.mount_static("/uploads", "/var/www/uploads")
```

### Cache Headers

Static files are served with conditional cache headers:

- **Content-hashed files** (filename contains a hex hash segment, e.g.
  `app.abc123.css`): `Cache-Control: public, max-age=31536000, immutable`
- **All other files**: `Cache-Control: public, max-age=3600`

This ensures that versioned assets are cached aggressively while unversioned
files can be updated within an hour.

### Reverse Proxy Static Optimization

When deploying behind Nginx or Caddy, you can offload static asset serving from
the Python process:

```nginx
location /_miki/ {
    alias /opt/myapp/dist/_miki/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header X-Content-Type-Options nosniff;
}
```

For mobile (Capacitor) deployments, the entire `dist/_miki/` tree is copied
into the Cordova/Capacitor `www/` directory during the mobile build.

## Performance Tuning

### Workers

Match worker count to CPU cores:

```bash
uvicorn app:create_app --workers $(nproc) --host 0.0.0.0 --port 8000
```

### Static Assets

Serve runtime assets via the reverse proxy or a CDN. In production builds:

```bash
mikiui build --target web --mode fullstack
```

This produces static HTML files with hashed assets for long-term caching.

### Tailwind Optimization

Build production CSS with purge:

```bash
mikiui build --target web --theme tailwind --optimize
```

### Gzip / Brotli

Enable compression in Nginx:

```nginx
gzip on;
gzip_types text/css application/javascript application/json image/svg+xml;
gzip_min_length 1024;
```

### Caching Headers

```nginx
location /_miki/runtime/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Connection Limits

```bash
# In uvicorn
uvicorn app:create_app --limit-concurrency 1000 --timeout-keep-alive 5
```

---

## Monitoring and Logging

### Application Logs

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
```

### Health Checks

```python
from fastapi import FastAPI

fastapi_app = create_app(app)

@fastapi_app.get("/health")
async def health():
    return {"status": "ok"}
```

### Request Logging Middleware

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        print(f"{request.method} {request.url.path} {response.status_code} {duration:.3f}s")
        return response

fastapi_app.add_middleware(RequestLoggingMiddleware)
```

### Metrics

Instrument with Prometheus:

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(fastapi_app).expose(fastapi_app)
```

### Error Tracking

Integrate Sentry for production error tracking:

```python
import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[StarletteIntegration()],
)
```

---

## Checklist

Before going to production, verify:

- [ ] `MIKIUI_RUNTIME=local` for offline builds
- [ ] Security headers enabled (CSP, HSTS, X-Frame-Options)
- [ ] HTTPS enforced
- [ ] Workers scaled to CPU cores
- [ ] Static assets served with caching headers
- [ ] Health check endpoint at `/health`
- [ ] Logs structured and centralized
- [ ] Error tracking configured
- [ ] Database credentials in secrets manager, not code
