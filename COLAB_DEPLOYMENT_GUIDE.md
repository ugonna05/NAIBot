# 🚀 NAiBot Colab Deployment — Step-by-Step Guide

## 📋 Prerequisites (5 minutes)

### 1. Get ngrok Token (FREE)

1. Go to **https://ngrok.com** → Click **Sign Up**
2. Create account (email/GitHub)
3. After login, go to **Dashboard** (left sidebar)
4. Copy your **Authtoken** (looks like: `2bWNbJWPO...`)
5. **Save it somewhere safe** — you'll paste it in Colab

---

## 🚀 Deploy on Colab (10 minutes)

### Step 1: Open the Colab Notebook

1. Go to GitHub repo → open `naibot_colab_deployment.ipynb`
2. Click **"Open in Colab"** button
   - Or manually: **https://colab.research.google.com** → Upload notebook from your repo

### Step 2: Enable GPU

In Colab:
1. Click **Runtime** (top menu)
2. Select **Change runtime type**
3. Under "Hardware accelerator" → Select **T4 GPU**
4. Click **Save**

You should see ⚡ next to Runtime now.

### Step 3: Run Cell 1 (Verify GPU)

```python
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

**You should see:**
```
GPU Available: True
Device: Tesla T4
VRAM: 15.00 GB
```

If you see `False`, go back to Step 2 and select GPU again.

---

### Step 4: Run Cell 2 (Install Dependencies)

Just click the ▶️ play button. It installs all libraries needed.

Takes ~2 minutes.

---

### Step 5: Run Cell 3 (Configure ngrok)

Replace this line with your actual ngrok token:

```python
NGROK_AUTH_TOKEN = "your_ngrok_authtoken_here"
```

Change it to:

```python
NGROK_AUTH_TOKEN = "2bWNbJWPO..."  # your actual token
```

Then run the cell. You should see:
```
✅ ngrok configured
```

---

### Step 6: Run Cell 4 (Define NAiBot)

This cell defines the FastAPI app with Ugonna's model. Just run it.

You should see:
```
✅ FastAPI app defined
```

---

### Step 7: Run Cell 5 (Download Model)

This downloads Ugonna's 8B model from Hugging Face.

**First time:** ~5 minutes (downloads ~7GB)
**Subsequent times:** ~30 seconds (uses cache)

You'll see progress bars. Wait for:
```
✅ Model loading in background...
```

---

### Step 8: Run Cell 6 (Start Server)

This is the magic cell. It:
1. Starts the FastAPI server
2. Exposes it via ngrok
3. Prints your **PUBLIC URL**

Wait for it to print:
```
🌐 Public URL: https://abc123-xyz.ngrok.io
📖 API Docs: https://abc123-xyz.ngrok.io/docs
🔗 Health Check: https://abc123-xyz.ngrok.io/health
```

**Copy that URL and share with your team!**

The server keeps running in the background.

---

### Step 9 (Optional): Run Cell 7 (Test API)

This cell tests your live API:

```python
# Tests /health and /chat endpoints
```

If the model is done loading, you'll see:
```json
{
  "status": "ready",
  "model_loaded": true,
  "device": "cuda:0"
}
```

---

## ✅ You're Live!

Your team can now hit:

```
https://your-ngrok-url.ngrok.io/docs
```

And test the API in Swagger UI, or integrate it directly:

```python
import requests

response = requests.post(
    "https://your-ngrok-url.ngrok.io/chat",
    json={"message": "What is NaiLand?"}
)
print(response.json())
```

---

## 🔄 Keep Session Alive

By default, Colab stops after 12 hours. To keep it running:

**Option 1 (Easiest):** Install [Colab AutoRefresh Extension](https://github.com/kaushikjadhav01/Google-Colab-AutoRefresh)

**Option 2 (Manual):** Periodically click **Runtime → Run all** to refresh

**Option 3 (Schedule):** Use a free uptime monitoring tool like [UptimeRobot](https://uptimerobot.com) to ping `/health` every 10 minutes

---

## ⚠️ If Something Goes Wrong

### **"Module not found" error:**
- Run Cell 2 again to install dependencies

### **"CUDA out of memory":**
- Reduce `max_tokens` in requests (default 512, try 256)
- Or upgrade to Colab Pro

### **Model still loading after 10 minutes:**
- Normal for first run — Ugonna's 8B model takes time to download and load
- Wait longer, don't restart

### **ngrok URL not working:**
- Make sure Cell 6 is still running (check for errors)
- Token expired? Get a new one from https://ngrok.com/dashboard

### **"Model not loaded yet" on /chat:**
- The model is still loading in background (Cell 5)
- Check `/health` endpoint — wait until `model_loaded = true`

---

## 📊 What's Happening Behind the Scenes

```
┌─────────────────────────────────────┐
│      Your Colab Notebook            │
│  ┌────────────────────────────────┐ │
│  │  FastAPI App (Port 8000)      │ │
│  │  + Ugonna's Model (GPU)        │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
           ↑
           │ (internal)
           ↓
    ┌────────────────┐
    │    ngrok       │  ← Creates public tunnel
    └────────────────┘
           ↑
           │ (HTTPS)
           ↓
    Your Team's Frontend
    (uses ngrok URL)
```

Every time you restart Colab, you get a **new ngrok URL**. Share it in Slack/Discord.

---

## 🎯 Next Steps

1. **Test locally** with `/docs` Swagger UI (in Colab)
2. **Share the ngrok URL** with Ugonna and your team
3. **Make changes together** — you edit the Colab, Ugonna tunes the model
4. **Commit to GitHub** when stable
5. **Deploy to Render** for 24/7 production (later)

---

## 📞 Quick Troubleshooting Checklist

- [ ] GPU enabled? (check Runtime shows ⚡)
- [ ] ngrok token set? (Cell 3)
- [ ] Model done loading? (check `/health`)
- [ ] URL printed from Cell 6? (copy it!)
- [ ] Can access `/docs`? (browser test)
- [ ] Can hit `/health`? (should return JSON)
- [ ] Can hit `/chat`? (should return response, unless model still loading)

---

##  You're ready to go!

