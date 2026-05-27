# Memory Distiller Deployment Guide

## Architecture Overview

```
                    ┌─────────────────────────────────────────┐
                    │           Internet                       │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │   Nginx (port 80/443)                    │
                    │   - TLS termination                     │
                    │   - Basic Auth                          │
                    │   - Proxy to backend                    │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────────────────▼────────────────────┐
                    │   Docker Container (127.0.0.1:8501)      │
                    │   - Streamlit application               │
                    │   - Binds to localhost only             │
                    └─────────────────────────────────────────┘
```

**Components:**
- **Nginx**: Reverse proxy, TLS termination, Basic Authentication
- **Docker Compose**: Container orchestration, binds Streamlit to `127.0.0.1:8501`
- **Streamlit**: Web application serving memory distillation

**Ports:**
- `80`: HTTP (redirects to HTTPS)
- `443`: HTTPS with TLS
- `8501`: Streamlit (localhost only, not exposed)

---

## Prerequisites

1. **DNS**: A records pointing to server IPv4 and IPv6 address
   - `memory.bitschi.org` A record: `<SERVER_IPv4>`
   - `memory.bitschi.org` AAAA record: `<SERVER_IPv6>`
   - Propagation may take up to 48 hours

2. **Server**: Debian/Ubuntu Linux with:
   - Root or sudo access
   - Docker and Docker Compose installed
   - Nginx available in package manager

3. **Domain**: Ownership verified and DNS configured

---

## Server Directory Structure

```
/opt/memory-distiller/
├── docker-compose.yml
├── .env                 # Environment variables (NEVER commit)
├── app/                 # Application code
│   └── ...
└── nginx.conf           # Copied from infra/nginx/
```

**Critical security note:** The `.env` file and `.htpasswd-memory-distiller` file must **never** be committed to version control. Both contain sensitive credentials.

---

## Deployment Steps

### 1. Clone or Update the Repository

```bash
# Clone fresh
git clone <REPO_URL> /opt/memory-distiller
cd /opt/memory-distiller

# Or update existing
cd /opt/memory-distiller
git pull
```

### 2. Configure Environment Variables

Create `/opt/memory-distiller/.env` with required variables:

```bash
# Application configuration
DEEPSEEK_API_KEY=replace-me
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

**Never commit this file.** Add `.env` to `.gitignore` if not already present.

### 3. Build and Start Containers

```bash
cd /opt/memory-distiller

# Build images
docker compose build

# Start services in background
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs
docker compose logs -f  # follow mode
```

### 4. Install Nginx Configuration

Copy the Nginx configuration file:

```bash
# Copy example config
sudo cp /opt/memory-distiller/infra/nginx/memory.bitschi.org.conf.example /etc/nginx/sites-available/memory.bitschi.org.conf

# Enable site (create symlink)
sudo ln -s /etc/nginx/sites-available/memory.bitschi.org.conf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 5. Set Up Basic Authentication

Generate the htpasswd file for Nginx Basic Auth:

```bash
# Install apache2-utils (provides htpasswd)
sudo apt update
sudo apt install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd-memory-distiller <USERNAME>
# You will be prompted for a password

# Verify file was created
sudo ls -la /etc/nginx/.htpasswd-memory-distiller
```

**Important:** The password file must be created at `/etc/nginx/.htpasswd-memory-distiller` and referenced exactly in the Nginx config.

### 6. Obtain TLS Certificate with Certbot

```bash
# Install Certbot and Nginx plugin
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate (automatically configures Nginx)
sudo certbot --nginx -d memory.bitschi.org

# Certbot will:
# - Verify domain ownership
# - Obtain SSL certificate
# - Update Nginx config with TLS settings
# - Set up auto-renewal via systemd timer
```

### 7. Verify Deployment

```bash
# Check Nginx is running
sudo systemctl status nginx

# Check Docker containers are running
docker compose ps

# Test Basic Auth prompt appears
curl -I https://memory.bitschi.org
# Should return 401 with WWW-Authenticate header

# Test login (when credentials configured)
curl -u <USERNAME>:<PASSWORD> -I https://memory.bitschi.org
# Should return 200
```

---

## Health Checks

### Application Health

```bash
# Inside container
docker compose exec app python -c "import streamlit; print('OK')"

# External via Nginx (bypasses auth)
curl https://memory.bitschi.org/health
```

### Nginx Health

```bash
# Configuration test
sudo nginx -t

# Service status
sudo systemctl status nginx

# Active connections
sudo netstat -tlnp | grep -E '80|443'
```

### Docker Health

```bash
# Container status
docker compose ps

# Resource usage
docker stats

# Logs review
docker compose logs --tail=100
```

---

## Rollback and Redeployment

### Quick Restart

```bash
cd /opt/memory-distiller
docker compose restart
```

### Full Redeploy

```bash
cd /opt/memory-distiller
git pull
docker compose down
docker compose build
docker compose up -d
```

### Rollback to Previous Version

```bash
cd /opt/memory-distiller
# Identify the previous commit/tag
git log --oneline -10

# Revert to previous version
git checkout <PREVIOUS_COMMIT>
docker compose build
docker compose up -d
```

### Container Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs app

# Follow mode
docker compose logs -f

# Last N lines
docker compose logs --tail=50
```

---

## IPv6 Considerations

The domain `memory.bitschi.org` has an AAAA record configured, meaning IPv6 is active.

**Server-side:**
- Nginx is configured to listen on both IPv4 and IPv6 (`listen 80; listen [::]:80;`)
- The application container binds to `127.0.0.1:8501` (IPv4 only), which is correct
- IPv6 requests from clients will be handled by Nginx and proxied via IPv4 to the backend

**Testing IPv6:**
```bash
# Test AAAA resolution
dig AAAA memory.bitschi.org

# Test IPv6 connectivity (from external)
# Use an online service or: curl -6 https://memory.bitschi.org
```

**Note:** Some hosting providers may have IPv6 routing issues. If IPv6 fails but IPv4 works, verify the server's IPv6 configuration and routing.

---

## Security Notes

### Critical: Never Commit Secrets

The following files must **never** be committed to version control:

| File | Contains |
|------|----------|
| `.env` | Environment variables, API keys, database credentials |
| `.htpasswd` | Basic Auth password hashes |

Add these to `.gitignore`:

```gitignore
.env
.htpasswd-*
/etc/nginx/.htpasswd-*
```

### General Security Practices

1. **Firewall**: Allow only ports 80 and 443, block all other incoming
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny incoming
   ```

2. **Docker**: Don't expose Docker socket, use non-root user in containers

3. **Nginx**: Keep TLS version current (TLS 1.2/1.3), disable weak ciphers

4. **Certbot**: Auto-renewal handles certificate updates; monitor renewal status
   ```bash
   sudo certbot renew --dry-run
   sudo systemctl status certbot.timer
   ```

5. **Basic Auth**: Use strong passwords, rotate periodically

6. **Updates**: Keep Docker images and system packages updated
   ```bash
   docker compose pull
   sudo apt update && sudo apt upgrade
   ```

---

## Troubleshooting

### Nginx Won't Start

```bash
# Check configuration syntax
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log

# Check ports are not in use
sudo netstat -tlnp | grep -E '80|443'
```

### Docker Container Won't Start

```bash
# Check logs
docker compose logs app

# Inspect container
docker compose ps
docker inspect <container_id>

# Check .env file exists and is valid
cat /opt/memory-distiller/.env
```

### Basic Auth Not Working

```bash
# Verify htpasswd file exists
ls -la /etc/nginx/.htpasswd-memory-distiller

# Check Nginx config references correct path
grep auth_basic_user_file /etc/nginx/sites-available/memory.bitschi.org.conf

# Test manually
htpasswd -c /etc/nginx/.htpasswd-memory-distiller testuser
# Then access https://memory.bitschi.org and login with testuser
```

### TLS Certificate Issues

```bash
# Check Certbot status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Check renewal timer
sudo systemctl status certbot.timer
```

### Streamlit WebSocket Issues

If the application appears to load but interactions fail:

1. Verify `proxy_http_version 1.1` is set
2. Verify `Upgrade` and `Connection` headers are configured
3. Check browser console for WebSocket errors
4. Increase `proxy_read_timeout` if needed (currently set to 86400)

---

## File Locations Reference

| Purpose | Path |
|---------|------|
| Application code | `/opt/memory-distiller/` |
| Docker Compose file | `/opt/memory-distiller/docker-compose.yml` |
| Environment variables | `/opt/memory-distiller/.env` |
| Nginx config (enabled) | `/etc/nginx/sites-enabled/memory.bitschi.org.conf` |
| Nginx config (available) | `/etc/nginx/sites-available/memory.bitschi.org.conf` |
| Basic Auth password file | `/etc/nginx/.htpasswd-memory-distiller` |
| TLS certificates | `/etc/letsencrypt/live/memory.bitschi.org/` |
| Application logs | `docker compose logs` |
| Nginx access log | `/var/log/nginx/access.log` |
| Nginx error log | `/var/log/nginx/error.log` |