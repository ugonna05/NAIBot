#  NAiBot 

> **NaiLand's AI-powered onboarding and navigation assistant — production-ready REST API deployed on Render.**

[![CI](https://github.com/YOUR_ORG/naibot-api/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_ORG/naibot-api/actions)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Render](https://img.shields.io/badge/Deploy-Render-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Overview

NAiBot is NaiLand's intelligent onboarding assistant. It welcomes new users, guides them through the platform, answers questions about features, and navigates users to the right sections — all through a clean REST API that any frontend or mobile client can integrate with.

**Built by the NaiLand AI/ML team (Kwanele & Ugonna).**

---

## ✨ Features

- 🧠 LLM-powered conversational responses via a fine-tuned / prompted model
- 🚀 FastAPI backend with async support
- 🔒 CORS-configurable for secure frontend integration
- 📡 `/health` endpoint for uptime monitoring (UptimeRobot / Render health checks)
- 🗂️ Session ID support for multi-turn conversation tracking
- 🐳 Render-native deployment with persistent disk for model weights
- 📖 Auto-generated API docs at `/docs` (Swagger) and `/redoc`

---

## 📁 Project Structure

```
naibot-api/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI app, model manager, routes
├── scripts/
│   └── download_model.py    # One-time model download to Render disk
├── tests/
│   └── test_api.py          # Pytest smoke tests
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline
├── .env.example             # Environment variable template
├── .gitignore
├── render.yaml              # Render deployment configuration
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start (Local)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_ORG/naibot-api.git
cd naibot-api
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — set HF_TOKEN and MODEL_PATH
```

### 4. Download model (first time only)

```bash
python scripts/download_model.py
```

### 5. Run the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API is now live at **http://localhost:8000**
Interactive docs at **http://localhost:8000/docs**

---

## ☁️ Deploy to Render (Step-by-Step)

### Step 1 — Push to GitHub

```bash
git init
git remote add origin https://github.com/YOUR_ORG/naibot-api.git
git add .
git commit -m "feat: initial NAiBot API"
git push -u origin main
```

### Step 2 — Create Web Service on Render

1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repo
3. Render auto-detects `render.yaml` — click **Apply**

### Step 3 — Set Environment Variables (Render Dashboard)

| Key | Value |
|---|---|
| `HF_TOKEN` | Your Hugging Face access token |
| `MODEL_PATH` | `/opt/render/project/src/models` |
| `ALLOWED_ORIGINS` | Your frontend domain (e.g. `https://nailand.app`) |

### Step 4 — Add Persistent Disk

In your Render service: **Settings → Disks → Add Disk**

| Field | Value |
|---|---|
| Name | `model-storage` |
| Mount Path | `/opt/render/project/src/models` |
| Size | `20 GB` (adjust for your model) |

### Step 5 — Download Model to Disk (One Time)

In Render's **Shell** tab (after first deploy):

```bash
HF_TOKEN=your_token MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0 python scripts/download_model.py
```

> ⚠️ For gated models like Llama-2 or Mistral, you must [request access on Hugging Face](https://huggingface.co) first.

### Step 6 — Redeploy

Trigger a redeploy from the Render dashboard. The model loads from disk on startup.

---

## 📡 API Reference

### `GET /health`

Check if NAiBot and the model are ready.

```bash
curl https://your-service.onrender.com/health
```

```json
{
  "status": "ready",
  "model_loaded": true,
  "device": "cpu",
  "version": "1.0.0"
}
```

---

### `POST /chat`

Send a message to NAiBot.

```bash
curl -X POST https://your-service.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I get started on NaiLand?",
    "session_id": "user-abc-123",
    "max_tokens": 300,
    "temperature": 0.7
  }'
```

**Request body:**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `message` | string | ✅ | — | User's message (1–2048 chars) |
| `session_id` | string | ❌ | auto-generated | For tracking sessions |
| `max_tokens` | int | ❌ | 512 | Max response length |
| `temperature` | float | ❌ | 0.7 | Response creativity (0.1–1.5) |

**Response:**

```json
{
  "id": "a3f2c1d0-...",
  "session_id": "user-abc-123",
  "reply": "Welcome to NaiLand! Let me walk you through getting started...",
  "model_loaded": true,
  "created": 1749301200
}
```

---

## ⚙️ Render Plan Guide

| Plan | RAM | CPU | Suitable For |
|---|---|---|---|
| Free | 512 MB | Shared | ❌ Not enough for LLMs |
| Starter | 512 MB | 0.5 | Small models only (TinyLlama ~1B) |
| Standard | 2 GB | 1 | Quantized 7B models (4-bit) |
| Professional | 4 GB | 2 | Full 7B/8B models |

> 💡 **Recommendation:** Use **Standard ($7/mo)** for 4-bit quantized 7B models. Add [UptimeRobot](https://uptimerobot.com) (free) to ping `/health` every 10 minutes and prevent cold starts.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🛠️ Tech Stack

- **Runtime:** Python 3.10
- **Framework:** FastAPI + Uvicorn
- **ML:** PyTorch + Hugging Face Transformers
- **Deployment:** Render (Web Service + Persistent Disk)
- **CI:** GitHub Actions

---

## 👥 Team

| Name | Role |
|---|---|
| Kwanele | AI/ML Team|
| Ugonna | AI/ML Team |

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

*NAiBot is part of the NaiLand platform. For support, contact the NaiLand AI team.*
