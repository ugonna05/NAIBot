# Cell 11: Create Deployment Files for Render
# This cell creates the necessary files for Render deployment

# Create requirements.txt
requirements_content = 
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0
transformers>=4.35.0
accelerate>=0.24.0
bitsandbytes>=0.41.0
peft>=0.6.0
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
aiofiles>=23.2.0
python-dotenv>=1.0.0
sentencepiece>=0.1.99
protobuf>=3.20.0
huggingface-hub>=0.19.0
nest-asyncio>=1.5.0


with open("requirements.txt", "w") as f:
    f.write(requirements_content.strip())
print("✅ Created requirements.txt")

# Create main.py for Render deployment
main_py_content =
import torch
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import time
import uuid
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model Manager
class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_path = "/opt/render/project/src/models"
        self.loading_status = "not_started"
    
    def setup_device(self):
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device("cpu")
            logger.info("Using CPU")
    
    def load_model(self):
        try:
            self.loading_status = "loading"
            self.setup_device()
            
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("Loading model...")
            if torch.cuda.is_available():
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float32,
                    trust_remote_code=True
                ).to(self.device)
            
            self.loading_status = "loaded"
            logger.info("✅ Model loaded successfully!")
            return True
        except Exception as e:
            self.loading_status = "failed"
            logger.error(f"Failed to load model: {e}")
            return False
    
    def generate(self, prompt: str, **kwargs):
        if self.model is None:
            raise Exception("Model not loaded")
        
        start_time = time.time()
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        else:
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=kwargs.get('max_tokens', 512),
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 0.9),
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        return {"text": generated_text}

# Initialize model manager
model_manager = ModelManager()

# Create FastAPI app
app = FastAPI(title="Model API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    import threading
    thread = threading.Thread(target=model_manager.load_model, daemon=True)
    thread.start()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if model_manager.model is not None else "loading",
        "model_loaded": model_manager.model is not None,
        "device": str(model_manager.device) if model_manager.device else "unknown"
    }

@app.post("/generate")
async def generate(request: dict):
    if model_manager.model is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    
    try:
        result = model_manager.generate(
            prompt=request.get("prompt", ""),
            max_tokens=request.get("max_tokens", 512),
            temperature=request.get("temperature", 0.7)
        )
        return {
            "id": str(uuid.uuid4()),
            "text": result["text"],
            "created": int(time.time())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Model API is running", "docs": "/docs"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


with open("main.py", "w") as f:
    f.write(main_py_content.strip())
print("✅ Created main.py")

# Create render.yaml for deployment configuration
render_yaml_content = 
services:
  - type: web
    name: model-api
    runtime: python
    plan: free  # or standard, professional
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.12
      - key: HF_TOKEN
        sync: false  # Set this in Render dashboard
    disk:
      name: model-storage
      mountPath: /opt/render/project/src/models
      sizeGB: 50  # Adjust based on model size


with open("render.yaml", "w") as f:
    f.write(render_yaml_content.strip())
print("✅ Created render.yaml")

print("\n" + "="*60)
print("📦 DEPLOYMENT FILES CREATED SUCCESSFULLY!")
print("="*60)
