# Docker Network Gateway Setup Guide

## Overview

This guide shows how to set up a gateway container that bridges your LAN network to Docker containers running on isolated Docker networks.

## Problem

You have:
- Docker containers on a custom network (e.g., `myapp_network` on subnet `172.20.0.0/16`)
- LAN devices on a different subnet (e.g., `192.168.1.0/24`)
- LAN devices cannot reach containers on the Docker network

## Solution

Use a reverse proxy container that:
1. Connects to **both** the host network (LAN) and the Docker network
2. Listens on a LAN-accessible port
3. Forwards traffic to containers on the isolated network

---

## Option 1: Nginx Proxy Gateway (Simple)

### Step 1: Install the Service

1. Open Docker Helper GUI
2. Select `nginx-proxy-gateway` service
3. Configure:
   - **Nginx Config Directory**: `/etc/nginx-proxy` (create this folder)
   - **Docker Network**: Name of your isolated network (e.g., `myapp_network`)
   - **HTTP Port**: `8080` (or your preferred port)

### Step 2: Create Nginx Configuration

Create `/etc/nginx-proxy/upstream.conf`:

```nginx
# Upstream configuration for containers
upstream myapp_backend {
    server myapp_container:8000;
}

upstream mydb_admin {
    server postgres:5432;
}

# HTTP server
server {
    listen 80;
    server_name _;

    # Proxy to backend app
    location /app/ {
        proxy_pass http://myapp_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy to database admin
    location /db/ {
        proxy_pass http://mydb_admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
```

### Step 3: Connect to Docker Network

After installation, connect the proxy to your Docker network:

```bash
docker network connect myapp_network nginx-proxy-gateway
```

### Step 4: Access from LAN

From any device on your LAN:
- `http://192.168.1.100:8080/app/` → Routes to `myapp_container:8000`
- `http://192.168.1.100:8080/db/` → Routes to `postgres:5432`

---

## Option 2: Traefik Gateway (Automatic Discovery)

Traefik automatically discovers containers and routes traffic based on labels.

### Step 1: Create Traefik Configuration

Create `/etc/traefik-config/traefik.yml`:

```yaml
# Traefik static configuration
api:
  dashboard: true
  insecure: true  # For dashboard access (use reverse proxy in production)

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false  # Only expose containers with traefik labels
    network: "myapp_network"  # Network to monitor

log:
  level: INFO

# Optional: ACME/Let's Encrypt for automatic SSL
# certificatesResolvers:
#   myresolver:
#     acme:
#       email: your@email.com
#       storage: /etc/traefik/acme.json
#       httpChallenge:
#         entryPoint: web
```

### Step 2: Install Traefik Service

1. Open Docker Helper GUI
2. Select `traefik-gateway` service
3. Configure:
   - **Traefik Config Directory**: `/etc/traefik-config`
   - **Docker Socket**: `/var/run/docker.sock` (with volume mapping enabled)
   - **HTTP Port**: `80`
   - **HTTPS Port**: `443`
   - **Dashboard Port**: `8080`

### Step 3: Label Your Containers

Add labels to containers you want to expose:

```bash
docker run -d \
  --name myapp \
  --network myapp_network \
  --label "traefik.enable=true" \
  --label "traefik.http.routers.myapp.rule=Host(\`myapp.local\`)" \
  --label "traefik.http.routers.myapp.entrypoints=web" \
  --label "traefik.http.services.myapp.loadbalancer.server.port=8000" \
  myapp:latest
```

Or add to docker-compose.yml:

```yaml
services:
  myapp:
    image: myapp:latest
    networks:
      - myapp_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myapp.rule=Host(`myapp.local`)"
      - "traefik.http.routers.myapp.entrypoints=web"
      - "traefik.http.services.myapp.loadbalancer.server.port=8000"
```

### Step 4: Configure DNS/Hosts

On LAN devices, add to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
192.168.1.100  myapp.local
192.168.1.100  api.local
192.168.1.100  db.local
```

### Step 5: Access from LAN

- `http://myapp.local` → Routes to `myapp:8000`
- `http://192.168.1.100:8080` → Traefik dashboard

---

## Network Architecture

```
┌─────────────────────────────────────────────────┐
│  LAN (192.168.1.0/24)                          │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ PC       │  │ Phone    │  │ Tablet   │     │
│  │ .10      │  │ .20      │  │ .30      │     │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘     │
│        │            │             │            │
│        └────────────┴─────────────┘            │
│                     │                          │
│              ┌──────▼──────┐                   │
│              │ Docker Host │                   │
│              │ 192.168.1.100                   │
│              └──────┬──────┘                   │
└─────────────────────┼──────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        │   ┌─────────▼─────────┐   │
        │   │  Proxy Gateway    │   │
        │   │  (Nginx/Traefik)  │   │
        │   │  Port: 80/443     │   │
        │   └─────────┬─────────┘   │
        │             │             │
        │   Docker Network          │
        │   (myapp_network)         │
        │   172.20.0.0/16          │
        │             │             │
        │   ┌─────────┼─────────┐   │
        │   │         │         │   │
        │ ┌─▼──┐   ┌─▼──┐   ┌──▼─┐ │
        │ │App │   │ DB │   │API │ │
        │ │:800│   │:543│   │:300│ │
        │ └────┘   └────┘   └────┘ │
        └───────────────────────────┘
```

---

## Advanced: Multiple Networks

To bridge multiple Docker networks:

### Nginx Approach

1. Connect proxy to all networks:
```bash
docker network connect network1 nginx-proxy-gateway
docker network connect network2 nginx-proxy-gateway
docker network connect network3 nginx-proxy-gateway
```

2. Configure upstreams for each network:
```nginx
upstream app1 {
    server container_on_network1:8000;
}

upstream app2 {
    server container_on_network2:9000;
}
```

### Traefik Approach

Traefik automatically discovers containers on all networks it's connected to:

```bash
docker network connect network1 traefik-gateway
docker network connect network2 traefik-gateway
docker network connect network3 traefik-gateway
```

---

## Security Considerations

1. **Firewall Rules**: Configure host firewall to allow traffic on proxy ports
2. **Authentication**: Add HTTP basic auth or OAuth proxy
3. **TLS/SSL**: Use HTTPS with proper certificates (Traefik supports automatic Let's Encrypt)
4. **Network Isolation**: Keep Docker networks isolated except via proxy
5. **Rate Limiting**: Configure rate limits on proxy to prevent abuse

---

## Troubleshooting

### Can't reach containers

1. Verify proxy is on correct network:
```bash
docker inspect nginx-proxy-gateway | grep NetworkMode
docker network inspect myapp_network
```

2. Check container can resolve names:
```bash
docker exec nginx-proxy-gateway ping myapp_container
```

3. Verify ports are listening:
```bash
netstat -tlnp | grep 8080
```

### DNS not working

For Traefik with hostnames, ensure:
1. DNS/hosts file configured on client
2. Router forwards DNS or use dnsmasq
3. Container labels are correct

### Connection refused

1. Check container ports are exposed
2. Verify nginx/traefik config syntax
3. Check logs: `docker logs nginx-proxy-gateway`

---

## Performance Tips

1. **Connection Pooling**: Increase nginx worker connections
2. **Caching**: Enable proxy caching for static content
3. **Compression**: Enable gzip in nginx/traefik
4. **Keep-Alive**: Enable HTTP keep-alive connections
5. **Load Balancing**: Use multiple upstream servers

---

## Example: Complete Setup

### 1. Create Docker Network
```bash
docker network create --subnet=172.20.0.0/16 myapp_network
```

### 2. Run Application Containers
```bash
docker run -d --name myapp --network myapp_network \
  -e PORT=8000 myapp:latest

docker run -d --name postgres --network myapp_network \
  -e POSTGRES_PASSWORD=secret postgres:alpine
```

### 3. Install Nginx Proxy Gateway (via GUI)
- Config dir: `/etc/nginx-proxy`
- HTTP port: `8080`

### 4. Connect Networks
```bash
docker network connect myapp_network nginx-proxy-gateway
```

### 5. Create Config
```bash
cat > /etc/nginx-proxy/upstream.conf << 'EOF'
upstream app {
    server myapp:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
    }
}
EOF
```

### 6. Reload Nginx
```bash
docker exec nginx-proxy-gateway nginx -s reload
```

### 7. Test from LAN
```bash
curl http://192.168.1.100:8080/
```

Done! 🎉

---

## References

- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Traefik Docker Provider](https://doc.traefik.io/traefik/providers/docker/)
- [Docker Networks](https://docs.docker.com/network/)
