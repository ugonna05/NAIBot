import torch
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
import uuid
from typing import Optional
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── NAiBot System Prompt ────────────────────────────────────────────────────

NAIBOT_SYSTEM_PROMPT = """You are NAiBot, the official AI assistant for NaiLand — a modern platform designed to connect, engage, and empower its users.

Your primary responsibilities are:
1. **Welcome** new users warmly and introduce them to NaiLand's features.
2. **Onboard** users by walking them through the platform step by step.
3. **Navigate** users to the right sections of NaiLand based on their needs.
4. **Answer questions** about how NaiLand works with clarity and friendliness.
5. **Escalate** complex issues by directing users to human support when needed.

Tone: Friendly, professional, concise, and encouraging.
Always stay on-topic about NaiLand. If asked about unrelated topics, politely redirect.
"""

# ─── Request / Response Schemas ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to NAiBot", min_length=1, max_length=2048)
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")
    max_tokens: Optional[int] = Field(512, ge=64, le=2048)
    temperature: Optional[float] = Field(0.7, ge=0.1, le=1.5)

class ChatResponse(BaseModel):
    id: str
    session_id: str
    reply: str
    model_loaded: bool
    created: int

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str
    version: str

# ─── Model Manager ───────────────────────────────────────────────────────────

class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_path = os.getenv("MODEL_PATH", "/opt/render/project/src/models")
        self.loading_status = "not_started"
        self._lock = threading.Lock()

    def setup_device(self):
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device("cpu")
            logger.info("Using CPU (inference will be slower)")

    def load_model(self):
        with self._lock:
            if self.loading_status == "loaded":
                return True
            try:
                self.loading_status = "loading"
                self.setup_device()

                logger.info(f"Loading tokenizer from: {self.model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path, trust_remote_code=True
                )
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token

                logger.info("Loading model weights...")
                if torch.cuda.is_available():
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True,
                    )
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        torch_dtype=torch.float32,
                        trust_remote_code=True,
                        low_cpu_mem_usage=True,
                    ).to(self.device)

                self.loading_status = "loaded"
                logger.info("✅ NAiBot model loaded successfully!")
                return True
            except Exception as e:
                self.loading_status = "failed"
                logger.error(f"❌ Failed to load model: {e}")
                return False

    def build_prompt(self, user_message: str) -> str:
        """Format prompt with the NAiBot system context."""
        return (
            f"<|system|>\n{NAIBOT_SYSTEM_PROMPT}\n"
            f"<|user|>\n{user_message}\n"
            f"<|assistant|>\n"
        )

    def generate(self, user_message: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        if self.model is None:
            raise RuntimeError("Model not loaded yet. Please retry in a moment.")

        prompt = self.build_prompt(user_message)
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        )

        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        else:
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()


# ─── App Initialisation ──────────────────────────────────────────────────────

model_manager = ModelManager()

app = FastAPI(
    title="NAiBot API",
    description="NaiLand's onboarding and navigation AI assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=model_manager.load_model, daemon=True)
    thread.start()
    logger.info("🚀 NAiBot API starting — model loading in background...")


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "NAiBot API",
        "description": "NaiLand's AI-powered onboarding assistant",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    return HealthResponse(
        status="ready" if model_manager.model is not None else model_manager.loading_status,
        model_loaded=model_manager.model is not None,
        device=str(model_manager.device) if model_manager.device else "initializing",
        version="1.0.0",
    )


@app.post("/chat", response_model=ChatResponse, tags=["NAiBot"])
async def chat(request: ChatRequest):
    """
    Send a message to NAiBot and receive an onboarding/navigation response.
    """
    if model_manager.model is None:
        raise HTTPException(
            status_code=503,
            detail=f"NAiBot is still loading (status: {model_manager.loading_status}). Please retry shortly.",
        )

    try:
        reply = model_manager.generate(
            user_message=request.message,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        session = request.session_id or str(uuid.uuid4())
        return ChatResponse(
            id=str(uuid.uuid4()),
            session_id=session,
            reply=reply,
            model_loaded=True,
            created=int(time.time()),
        )
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
