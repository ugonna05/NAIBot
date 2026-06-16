# 🤖 NAiBot API

> **NaiLand's AI-powered onboarding and navigation assistant — now running on Google Colab GPU with Ugonna's fine-tuned Llama-3.1 8B model.**

[![Colab](https://img.shields.io/badge/Launch-Colab-orange)](https://colab.research.google.com/github/YOUR_USERNAME/naibot-api/blob/main/naibot_colab_deployment.ipynb)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Model](https://img.shields.io/badge/Model-Llama%203.1%208B-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Overview

NAiBot is NaiLand's intelligent onboarding assistant, now **running on free GPU (T4) via Google Colab**. It welcomes new users, guides them through the platform, answers questions, and navigates users — with fast inference powered by Ugonna's fine-tuned Llama-3.1 8B model.

**Built by the NaiLand AI/ML team (Kwanele & Ugonna).**

---

## ✨ Features

- 🚀 **GPU-Powered:** Runs on Google Colab's free T4 GPU (instant responses, ~2-3 sec per request)
- 🧠 **Fine-Tuned Model:** Ugonna's Llama-3.1 8B (`ugonna/llama3.18B-Fine-tunedByUgo3`)
- 🔗 **Public URL:** Auto-exposed via ngrok — share with your team instantly
- 📡 `/health` endpoint for monitoring
- 🗂️ Session ID support for multi-turn conversations
- 📖 Auto-generated API docs at `/docs` (Swagger)
- ✅ CORS-enabled for frontend integration

---

## 📁 Project Structure

```
naibot-api/
├── app/
│   ├── __init__.py
│   └── main.py                      # FastAPI app (production Render version)
├── scripts/
│   └── download_model.py            # Model downloader (Render)
├── tests/
│   └── test_api.py                  # Unit tests
├── naibot_colab_deployment.ipynb   # 👈 COLAB NOTEBOOK (run this!)
├── .github/workflows/
│   └── ci.yml                       # GitHub Actions CI
├── render.yaml                      # Render deployment config
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 🚀 Quick Start — Google Colab (Recommended for Now)

### 1️⃣ Click the Colab button above ↑

Or go here: **[Open NAiBot Colab Notebook](https://colab.research.google.com/github/YOUR_USERNAME/naibot-api/blob/main/naibot_colab_deployment.ipynb)**

### 2️⃣ Set GPU Runtime

- Runtime → Change runtime type → **T4 GPU** → Save

### 3️⃣ Get ngrok Auth Token (2 minutes)

1. Go to [ngrok.com](https://ngrok.com) → **Sign up** (free)
2. Dashboard → **Get your authtoken**
3. Paste it into **Cell 3** of the notebook

### 4️⃣ Run cells in order

| Cell | What it does |
|---|---|
| 1 | ✅ Verify GPU available |
| 2 | 📦 Install dependencies |
| 3 | 🔐 Configure ngrok |
| 4 | ⚙️ Define FastAPI + NAiBot |
| 5 | 📥 Download Ugonna's model (first run ~5 min) |
| 6 | 🚀 Start server + expose URL |
| 7 | 🧪 Test the API |

### 5️⃣ You're live!

After Cell 6 completes, you'll see:

```
🌐 Public URL: https://abc123-xyz.ngrok.io
📖 API Docs: https://abc123-xyz.ngrok.io/docs
🔗 Health: https://abc123-xyz.ngrok.io/health
```

**Share that URL with your team.** It's your live API endpoint.

---

## 📡 API Reference

### `GET /health`

```bash
curl https://your-ngrok-url.ngrok.io/health
```

```json
{
  "status": "ready",
  "model_loaded": true,
  "device": "cuda:0",
  "version": "1.0.0-colab"
}
```

---

### `POST /chat`

```bash
curl -X POST https://your-ngrok-url.ngrok.io/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I get started on NaiLand?",
    "session_id": "user-123",
    "max_tokens": 300,
    "temperature": 0.7
  }'
```

**Response:**

```json
{
  "id": "a3f2c1d0-...",
  "session_id": "user-123",
  "reply": "Welcome to NaiLand! Let me walk you through getting started...",
  "model_loaded": true,
  "created": 1749301200
}
```

---

## 💡 Why Google Colab?

| Aspect | Colab | Render Free | Render Paid |
|---|---|---|---|
| **GPU** | T4 (free) | ❌ None | ✅ (paid) |
| **Inference Speed** | ~2-3 sec | N/A | ~3-5 sec |
| **Cost** | Free | Free | $7+/month |
| **Uptime** | 12 hours | 24/7 | 24/7 |
| **Best for** | Dev & demos | Small models | Production |

**For right now:** Colab is perfect. You get a free GPU and instant API for your team to test.

**For production later:** Render Standard ($7/month) with persistent disk for 24/7 uptime.

---

## 🔄 Workflow Going Forward

```
1. You run Colab notebook
   ↓
2. ngrok exposes your server
   ↓
3. Frontend hits the ngrok URL
   ↓
4. NAiBot responds (powered by Ugonna's model on GPU)
   ↓
5. Share new ngrok URL with team each session
```

---

## ⚠️ Important Notes

**Colab Session:**
- Notebooks run for up to 12 hours before auto-disconnecting
- To keep it alive, click **Runtime → Run all** periodically or use a [Colab Extension](https://github.com/kaushikjadhav01/Google-Colab-AutoRefresh)
- Restart = new ngrok URL (share it with your team)

**Model Loading:**
- First run: Downloads Ugonna's 8B model (~5-7GB, takes ~5 minutes)
- Subsequent runs: Uses cached weights (instant startup)

**GPU Memory:**
- Model uses ~6-7GB VRAM
- T4 has 15GB total — plenty of headroom

**ngrok Free Plan:**
- URLs are public and expire when you close the tunnel
- Bandwidth is limited to ~1GB/month (enough for testing)
- For production, upgrade to paid ngrok ($5/month) or use Render

---

## 🛠️ Local Development (Optional)

If you want to test on your PC before Colab:

```bash
# Create venv
python -m venv venv
source venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Download TinyLlama (small CPU-friendly model)
python scripts/download_model.py

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open **http://localhost:8000/docs**

---

## 📊 Model Specs

**Ugonna's Fine-Tuned Model:**
- Base: Meta Llama-3.1 8B
- Fine-tuned for: NaiLand onboarding tasks
- Repo: `ugonna/llama3.18B-Fine-tunedByUgo3`
- Parameters: 8 billion
- Precision: float16 (GPU)
- License: Llama 3.1 Community License

---

## 🚢 Production Deployment (Later)

When you're ready to move to 24/7 production:

1. **Push to GitHub** (you're already here!)
2. **Deploy to Render:**
   - Connect repo → pick `render.yaml`
   - Add persistent disk for model cache
   - Render auto-pulls from Hugging Face
3. **Update frontend** to use Render URL instead of ngrok

See the **Render Deployment** section at the end of this README.

---

## 🧪 Testing

**From Colab (Cell 7):**
Notebook includes a test cell that auto-runs `/health` and `/chat` against your live API.

**From your PC (after downloading model):**
```bash
pytest tests/ -v
```

---

## 👥 Team

| Name | Role | Model |
|---|---|---|
| Kwanele | API & Deployment | FastAPI, Render, Colab |
| Ugonna | Fine-tuning & ML | Llama-3.1 8B (`ugonna/llama3.18B-Fine-tunedByUgo3`) |

---

## 📝 Colab Deployment Checklist

- [ ] Push this repo to GitHub
- [ ] Click the Colab badge above
- [ ] Enable T4 GPU (Runtime → Change runtime type)
- [ ] Get ngrok auth token from https://ngrok.com
- [ ] Fill in Cell 3 with your token
- [ ] Run all cells in order
- [ ] Copy the ngrok URL and share with team
- [ ] Test at `/docs` in your browser
- [ ] Make a commit with this README

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

## 🔗 Quick Links

- **GitHub Repo:** [naibot-api](https://github.com/YOUR_USERNAME/naibot-api)
- **Ugonna's Model:** [huggingface.co/ugonna](https://huggingface.co/ugonna)
- **Google Colab:** [colab.research.google.com](https://colab.research.google.com)
- **ngrok:** [ngrok.com](https://ngrok.com)

---

*NAiBot is part of the NaiLand platform. Built with ❤️ by the AI/ML team.*