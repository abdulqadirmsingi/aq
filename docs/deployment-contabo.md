# Contabo Deployment Guide

This project is best deployed with:

- `app.abdulqadirmsingi.com` on Vercel for the Next.js frontend
- `api.abdulqadirmsingi.com` on your Contabo VPS for the FastAPI backend
- Docker Compose on the VPS for PostgreSQL, Redis, the backend, `celery_worker`, and `celery_beat`

That split fits the current codebase well because the frontend is a Next.js 15 app, while the backend and Celery services need always-on processes.

## What is currently deployable

The backend currently exposes:

- Energy APIs
- Money APIs

The frontend also has Living Cost, Medicine, and HR sections in the codebase, but some of them are still marked disabled in the navigation and are not all wired into `backend/app/main.py` yet. A production deployment today should be treated as an Energy + Money release.

## Why Vercel for the frontend

Use Vercel instead of Netlify for this repo because:

- the frontend is a Next.js app
- Vercel handles Next.js App Router deployments more directly
- adding a custom subdomain like `app.abdulqadirmsingi.com` is straightforward

You can still use Netlify, but Vercel is the lower-friction option here.

## Recommended production layout

On the VPS:

- `db` container for PostgreSQL
- `redis` container for Celery
- `backend` container for FastAPI
- `celery_worker` container for background jobs
- `celery_beat` container for schedules

On Vercel:

- `frontend` project with `NEXT_PUBLIC_API_URL=https://api.abdulqadirmsingi.com/api/v1`

DNS:

- `app.abdulqadirmsingi.com` -> Vercel
- `api.abdulqadirmsingi.com` -> your Contabo VPS public IP

## Before you start

The production files added for this setup are:

- `docker-compose.prod.yml`
- `.env.prod.example`
- `backend/Dockerfile.prod`
- `scrapers/Dockerfile.prod`
- `infra/nginx/aq-api.conf.example`

Your current `docker-compose.yml` is still a development setup. Do not use it directly for production because it mounts source code and starts services in dev mode.

## Step 1: Prepare the VPS

SSH into the server and install Docker, Docker Compose plugin, Git, and Nginx if they are not installed yet.

Example Ubuntu packages:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg git nginx
```

Install Docker using the official Docker instructions for your VPS OS, then verify:

```bash
docker --version
docker compose version
nginx -v
```

## Step 2: Clone the project in a separate directory

Since you already have another project in `~/civora-oea`, keep this one separate:

```bash
cd ~
git clone <your-repo-url> aq
cd aq
```

This avoids mixing containers, env files, and scripts between projects.

## Step 3: Create the production env file

On the VPS:

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Set at least these values:

```env
COMPOSE_PROJECT_NAME=aq
POSTGRES_USER=aq_user
POSTGRES_PASSWORD=<strong-random-password>
POSTGRES_DB=aq_db
BACKEND_BIND_IP=127.0.0.1
BACKEND_PORT=8001
DATABASE_URL=postgresql+asyncpg://aq_user:<strong-random-password>@db:5432/aq_db
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
SECRET_KEY=<strong-random-secret>
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://app.abdulqadirmsingi.com
POSTGRES_PORT=5432
```

Notes:

- `BACKEND_PORT=8001` is intentional so you avoid conflicts with other apps on the server.
- `POSTGRES_PORT=5432` publishes PostgreSQL only to `127.0.0.1` on the VPS so tools like DBeaver can connect through SSH tunneling without exposing the database publicly.
- `ALLOWED_ORIGINS` must match the real frontend domain.
- `DATABASE_URL` uses `db` as the hostname because that is the Docker service name.

## Step 4: Build and start the data services

From the repo root on the VPS:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml build
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d db redis
docker compose --env-file .env.prod -f docker-compose.prod.yml --profile ops run --rm migrate
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d backend celery_worker celery_beat
```

Check status:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f backend
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f celery_worker
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f celery_beat
```

## Step 5: Put Nginx in front of the API

Copy the example config and adjust only if your local backend port is different:

```bash
sudo cp infra/nginx/aq-api.conf.example /etc/nginx/sites-available/aq-api
sudo ln -s /etc/nginx/sites-available/aq-api /etc/nginx/sites-enabled/aq-api
sudo nginx -t
sudo systemctl reload nginx
```

At this point Nginx will proxy:

- `api.abdulqadirmsingi.com` -> `127.0.0.1:8001`

If your other project already uses Nginx, this is the safe approach: keep one Nginx on the host and add one more server block for AQ.

## Step 6: Add HTTPS with Let's Encrypt

Install Certbot if needed, then issue the certificate:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.abdulqadirmsingi.com
```

After that, test:

```bash
curl https://api.abdulqadirmsingi.com/health
curl https://api.abdulqadirmsingi.com/docs
```

You should get a healthy response from `/health`.

## Step 7: Deploy the frontend to Vercel

Push the repo to GitHub or your Git provider, then in Vercel:

1. Import the repo
2. Set the project root to `frontend`
3. Add environment variable:

```env
NEXT_PUBLIC_API_URL=https://api.abdulqadirmsingi.com/api/v1
```

4. Deploy
5. Add the custom domain `app.abdulqadirmsingi.com`

Vercel will show you the DNS record to create. In many cases this is a CNAME for `app`.

For this repo, if your real frontend domain is `data.abdulqadirmsingi.com`, use that instead of `app.abdulqadirmsingi.com` in both Vercel and `ALLOWED_ORIGINS`.

Important: set the Vercel project root to `frontend`. Do not deploy the app under a `/frontend` URL path.

## Step 8: Create the DNS records

In your DNS provider for `abdulqadirmsingi.com`:

- point `api` to the Contabo VPS public IP
- point `app` to Vercel using the record Vercel provides

After DNS propagates, verify:

```bash
curl https://api.abdulqadirmsingi.com/health
```

Then open:

- `https://app.abdulqadirmsingi.com`
- `https://api.abdulqadirmsingi.com/docs`

## Step 9: How the whole system works after deployment

1. A user opens `app.abdulqadirmsingi.com`
2. Vercel serves the Next.js frontend
3. The frontend calls `https://api.abdulqadirmsingi.com/api/v1/...`
4. Nginx on the VPS proxies that traffic to the backend container
5. The backend reads from PostgreSQL
6. `celery_beat` schedules scraper jobs
7. `celery_worker` runs those scraper jobs
8. The scrapers write new normalized data into PostgreSQL
9. The backend exposes the updated data to the frontend

Redis is only for Celery queueing and job coordination. PostgreSQL is the source of truth for the application data.

## Why the browser may not show API requests

The frontend uses the Next.js App Router and most pages fetch data on the server during rendering. That means:

- the request often happens from the Vercel server, not the browser
- you may not see the request in the browser Network tab on first page load
- if `NEXT_PUBLIC_API_URL` is missing in production, the build should now fail instead of silently falling back to localhost

If you need to confirm requests are happening, check:

- Vercel function logs
- the page HTML output
- the backend access logs on the VPS

## Step 10: Automatic deployment

Vercel already supports automatic frontend deployment when the GitHub repo is connected. Every push to `main` triggers a new frontend deployment automatically.

For the VPS backend, this repo now includes a GitHub Actions workflow in `.github/workflows/deploy.yml` that deploys after the `CI` workflow passes for `main`.

Before it can work, do these one-time VPS steps:

1. Ensure the `deploy` user can run Docker without `sudo`:

```bash
sudo usermod -aG docker deploy
```

2. Log out and SSH back in so the new group membership takes effect.

3. Verify:

```bash
docker ps
```

Then add these GitHub repository secrets:

- `CONTABO_HOST` = your VPS public IP or hostname
- `CONTABO_PORT` = `22`
- `CONTABO_USER` = `deploy`
- `CONTABO_SSH_KEY` = the private SSH key contents for the deploy user

After that, every push to `main` will;

1. SSH into the VPS
2. `git pull` the latest code
3. rebuild Docker images
4. run migrations
5. restart `backend`, `celery_worker`, and `celery_beat`

Recommended first test:

- push once to `main`
- open GitHub Actions
- watch the `CI` workflow pass
- watch the `Deploy` workflow run
- verify `https://api.abdulqadirmsingi.com/health`

## Step 11: Connecting DBeaver to the AQ database

In production, PostgreSQL is intentionally private inside Docker and is not exposed publicly. The safest way to connect from DBeaver is with an SSH tunnel through the VPS.

Use these DBeaver settings:

- Database: PostgreSQL
- Host: `127.0.0.1`
- Port: `5432`
- Database: `aq_db`
- Username: `aq_user`
- Password: the value from `POSTGRES_PASSWORD` in `.env.prod`

SSH tab:

- Use SSH Tunnel: enabled
- Host/IP: your Contabo VPS IP
- Port: `22`
- User name: `deploy`
- Authentication: your SSH private key

If you prefer a direct local tunnel first, you can also run this on your computer:

```bash
ssh -L 5433:127.0.0.1:5432 deploy@your-vps-ip
```

Then in DBeaver use:

- Host: `127.0.0.1`
- Port: `5433`
- Database: `aq_db`
- Username: `aq_user`
- Password: your `POSTGRES_PASSWORD`

## Step 12: Safe operations and updates

When updating the code on the VPS:

```bash
cd ~/aq
git pull
docker compose --env-file .env.prod -f docker-compose.prod.yml build
docker compose --env-file .env.prod -f docker-compose.prod.yml --profile ops run --rm migrate
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d backend celery_worker celery_beat
```

This flow is safer than tearing everything down, and it reduces the chance of breaking your existing project on the same server.

## Step 13: Recommended checks before calling it done

- `docker compose ... ps` shows all AQ containers healthy/running
- `curl https://api.abdulqadirmsingi.com/health` returns success
- `celery_worker` logs show it connected to Redis
- `celery_beat` logs show schedules loading
- frontend loads and shows live API data
- browser network requests go to `api.abdulqadirmsingi.com`
- CORS allows your real frontend domain, for example `https://data.abdulqadirmsingi.com`

## Important caution

I cannot honestly guarantee that "nothing would break" without also testing on the real VPS and checking how your existing project currently uses Nginx, ports, Docker networks, and certificates. This setup is designed to avoid the most common breakages:

- separate project directory
- separate Compose project name
- backend bound to `127.0.0.1`
- one host-level Nginx reverse proxy
- no public PostgreSQL or Redis ports

That is the safest deployment pattern for your situation.
