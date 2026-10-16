# Focus Model: AI-Powered Focus Tracker

A full-stack "smart Pomodoro" app. A custom PyTorch CNN watches your webcam and pauses the focus timer when you look away.

## Quick start (Docker)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
docker compose up --build
```

Open http://localhost:8080 and allow camera access.

## Architecture

```
Browser ──▶ nginx :8080 ──┬── /          → React app (static files)
                          └── /api/...   → FastAPI :8000 (private network) → PyTorch CNN
```

- **nginx** serves the built frontend and reverse-proxies `/api` to the API, so the browser only talks to one origin (no CORS) and the API is never exposed publicly.
- **FastAPI** decodes the webcam frame in memory and returns `{"status": "Focused" | "Distracted"}`.
- **Docker Compose** runs both services on a private network; the web container waits until the API passes its health check.

| Layer    | Tech                                         |
| -------- | -------------------------------------------- |
| Frontend | React + TypeScript (Vite), Tailwind CSS      |
| Proxy    | nginx                                        |
| API      | FastAPI, Uvicorn                             |
| Model    | PyTorch CNN (64×64 RGB input, 2 classes)     |
| Infra    | Docker (multi-stage builds), Docker Compose  |

## Project structure

```
api/
  model.py              # CNN definition, preprocessing, load/predict
  main.py               # FastAPI app: /health, /predict-focus
  tests/                # pytest suite
  Dockerfile            # CPU-only PyTorch image, non-root user, healthcheck
  requirements.txt      # runtime dependencies (pinned)
  requirements-dev.txt  # test + lint tools
  pyproject.toml        # pytest + ruff config
app/
  src/                  # React frontend
  Dockerfile            # multi-stage: Node builds, nginx serves
  nginx.conf            # static files + /api reverse proxy
docker-compose.yml      # runs the full stack
```

## Local development (without Docker)

### API
```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-dev.txt
uvicorn main:app --reload
```
Interactive API docs: http://localhost:8000/docs

### Frontend
```bash
cd app
npm install
npm run dev
```
Open http://localhost:5173. Vite's dev server proxies `/api` to `localhost:8000`, mirroring the nginx setup.

## Configuration

| Variable          | Service  | Default                  | Purpose                                 |
| ----------------- | -------- | ------------------------ | --------------------------------------- |
| `MODEL_PATH`      | API      | `api/focus_model.pth`    | Path to model weights                   |
| `ALLOWED_ORIGINS` | API      | `http://localhost:5173`  | Comma-separated CORS origins            |
| `VITE_API_URL`    | Frontend | `/api`                   | API base URL (build time)               |

## Testing and linting

```bash
# API
cd api
ruff check .
python -m pytest -v

# Frontend
cd app
npm run lint
npm run build
```

## API

| Method | Path             | Body                        | Response                                   |
| ------ | ---------------- | --------------------------- | ------------------------------------------ |
| GET    | `/health`        | none                        | `{"status": "ok"}`                         |
| POST   | `/predict-focus` | `{"image_b64": "<base64>"}` | `{"status": "Focused"}` or `"Distracted"`  |

Returns `400` for invalid images and `413` for oversized payloads.

## Privacy

Webcam frames are processed in memory and never saved or logged. Camera access requires `localhost` or HTTPS.

## Roadmap

- [x] Refactor API, add tests and linting
- [x] Dockerize API and frontend, docker-compose
- [ ] GitHub Actions CI (lint, test, build, image scan)
- [ ] Model accuracy regression gate
- [ ] Deploy to AWS and Azure with Terraform
- [ ] Export model to ONNX to shrink the API image