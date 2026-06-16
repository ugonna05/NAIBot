#!/usr/bin/env python3
"""
download_model.py
─────────────────
Run this script ONCE on Render (via Shell) to download the model onto the
persistent disk before the first deployment.

Usage:
    HF_TOKEN=your_token python scripts/download_model.py
    HF_TOKEN=your_token MODEL_NAME=meta-llama/Llama-2-7b-chat-hf python scripts/download_model.py
"""

import os
import sys
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError:
    print("❌ Install dependencies first: pip install transformers huggingface-hub")
    sys.exit(1)

# ─── Config ──────────────────────────────────────────────────────────────────

HF_TOKEN   = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")  # swap for your model
MODEL_PATH = os.getenv("MODEL_PATH", "/opt/render/project/src/models")

# ─── Download ────────────────────────────────────────────────────────────────

def main():
    dest = Path(MODEL_PATH)
    dest.mkdir(parents=True, exist_ok=True)

    # Skip download if model already present
    config_file = dest / "config.json"
    if config_file.exists():
        print(f"✅ Model already present at {dest} — skipping download.")
        return

    print(f"📥 Downloading '{MODEL_NAME}' → {dest}")
    print("    This may take several minutes depending on model size…\n")

    kwargs = {"local_dir": str(dest), "local_dir_use_symlinks": False}
    if HF_TOKEN:
        kwargs["token"] = HF_TOKEN

    snapshot_download(repo_id=MODEL_NAME, **kwargs)
    print(f"\n✅ Model downloaded successfully to {dest}")


if __name__ == "__main__":
    main()
