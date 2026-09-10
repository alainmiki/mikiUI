# Deployment

This guide covers deploying MikiUI applications to production. It includes Docker, reverse proxies, process management, HTTPS, and performance tuning.

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
app.secret_key = os.environ["MIKIUI_SECRET_KEY"]
```

## Docker Setup

Create a `Dockerfile`:

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t myapp .
docker run -p 8000:8000 -e MIKIUI_SECRET_KEY=your-secret myapp
```

## Reverse Proxy

### Nginx

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy

```caddy
example.com {
    reverse_proxy 127.0.0.1:8000
}
```

## Process Management

Use `systemd` or `supervisord` to manage the MikiUI process:

```ini
# /etc/systemd/system/mikiui.service
[Unit]
Description=MikiUI App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/myapp
Environment="MIKIUI_SECRET_KEY=your-secret"
ExecStart=/opt/myapp/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

## HTTPS

Use Let's Encrypt with Certbot:

```bash
certbot --nginx -d example.com -d www.example.com
```

Or use a reverse proxy that handles TLS for you (Caddy, Cloudflare, etc.).

## Static Site Deployment

For static exports:

```bash
mikiui build --target web --mode separate --out dist/
```

Deploy the `dist/` directory to any static host:
- **Netlify**: drag-and-drop or connect Git
- **Vercel**: `vercel deploy dist/`
- **GitHub Pages**: push to `gh-pages` branch
- **S3**: `aws s3 sync dist/ s3://your-bucket`

## Performance Tuning

### Uvicorn Workers

```bash
uvicorn app:app --workers 4 --loop uvloop
```

### Caching

Enable caching for static assets:

```python
from mikiui.app.static_assets import CachingStaticFiles

app.mount_static("/static", "./static", static_files_class=CachingStaticFiles)
```

### Database

For production, use a persistent database instead of in-memory storage:

```python
from mikiui_app_plugins.session import RedisSessionStorage

session = SessionPlugin(
    secret_key="your-secret",
    storage=RedisSessionStorage(redis_url="redis://localhost:6379/0"),
)
```

## Monitoring

- Use `MIKIUI_LOG_LEVEL=info` for production logging
- Monitor with Prometheus/Grafana or your APM of choice
- Set up health checks at `/health`

## Backup

- Backup your database regularly
- Version-control your code and configuration
- Use environment variables for secrets, not config files

## Build System

MikiUI includes a production-ready build system for web and desktop targets.
Builds are deterministic, self-contained, and include all runtime assets,
component static files, and themes.

### Web Build

```bash
mikiui build --target web --mode fullstack --out dist/
```

The web build produces:

- Pre-rendered HTML for every GET route
- Copied runtime assets (`_miki/runtime/`)
- A production HTML shell with CSP nonces
- `manifest.json` with content hashes for cache busting
- `sitemap.xml` for crawler discoverability
- `robots.txt`
- `404.html` fallback for SPA routes
- `server.py` (fullstack mode only) for standalone serving

#### Modes

| Mode | Output | Use case |
|------|--------|----------|
| `fullstack` | Static HTML + `server.py` | Deploy as a standalone ASGI app |
| `separate` | Static HTML only | Deploy behind any static file server or CDN |

#### Framework Options

```bash
# Plain CSS (default, no Node.js required)
mikiui build --target web --mode fullstack

# Tailwind CSS (requires Node.js)
mikiui build --target web --mode fullstack --theme tailwind --daisyui

# Local Tailwind CSS bundle
mikiui build --target web --mode fullstack --theme tailwind --style-mode local
```

### Desktop Build

```bash
mikiui build --target desktop --out dist_desktop/
```

The desktop build:

1. Produces a web build inside `dist_desktop/web/`
2. Generates a portable launcher script
3. Auto-installs PyInstaller if needed
4. Runs PyInstaller to produce a native executable
5. Wraps the executable in a platform-native bundle (`.app` on macOS)

PyInstaller is installed automatically if it is not already available. If
PyInstaller fails, the build still returns a usable directory with the web
build and launcher scripts.

#### Options

```bash
# Standard desktop build
mikiui build --target desktop

# Single-file executable (slower startup, easier distribution)
mikiui build --target desktop --onefile

# Custom icon
mikiui build --target desktop --icon path/to/icon.ico
```

#### Output

| File | Description |
|------|-------------|
| `dist_desktop/web/` | Web build (static front-end + ASGI server) |
| `dist_desktop/launch.exe` / `launch.app` / `launch` | Platform launcher |
| `dist_desktop/mikiui_linux.spec` | PyInstaller spec |
| `dist_desktop/dist/` | PyInstaller output directory |
| `dist_desktop/<AppName>.app` | macOS app bundle (if on macOS) |

### Static Assets

The build system automatically copies:

- Runtime JS/CSS files from `mikiui/runtime/`
- Component static files from `mikiui/components/*/static/`
- Widget static files from `mikiui/widgets/*/static/`
- Theme CSS files from `mikiui/runtime/themes/`

All assets are included in `manifest.json` with content hashes for cache
busting.

### Optimization

```bash
# Build with minification
mikiui build --target web --optimize

# Skip optimization
mikiui build --target web --no-optimize
```

The optimizer strips comments and collapses whitespace in CSS and JS files.
For larger apps, consider using a Vite/Webpack pipeline via `package.json`.

### Clean Builds

```bash
mikiui build --target web --clean
```

Removes the output directory before building.

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
