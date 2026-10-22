
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(
    title="DikaSearch AI Pro Backend",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "service": "DikaSearch AI Pro Backend",
        "status": "running",
        "message": "Backend ทดลองพร้อมตอบคำขอ",
    }

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "dikasearch-ai-pro-backend",
        "status": "awake",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/wake")
def wake():
    return {
        "ok": True,
        "status": "awake",
        "message": "Backend ตอบสนองแล้ว",
    }
