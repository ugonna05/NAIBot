from fastapi import FastAPI

app = FastAPI(title="NAI1")

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Your model API is running"}

@app.get("/health")
def health_check():
    return {"status":"ok"}
