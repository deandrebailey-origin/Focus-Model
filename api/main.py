import base64
import binascii
import io
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

from model import load_model, predict

MODEL_PATH = os.getenv("MODEL_PATH", str(Path(__file__).parent / "focus_model.pth"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
MAX_B64_CHARS = 2_000_000  # 1MB limit for base64-encoded images

app = FastAPI(title="Focus Model API")
app.add_middleware(
    CORSMiddleware, # allow cross-origin requests from specified origins
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=["GET", "POST"],
    allow_headers=["*"],
)
model = load_model(MODEL_PATH)

class ImafeData(BaseModel):
    image_b64: str

## checks if incoming json has no image_b64 key or if the value is empty, and raises an HTTPException with a 400 status code and a message indicating that the image data is missing.\

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post
def predict_focus(data: ImageData):
    if len(data.image_b64) > MAX_B64_CHARS:
        raise HTTPException(status_code=413, detail="Image too large")
    encoded = data.image_b64.split(",", 1)[-1]  # strip "data:image/jpeg;base64,"
    try:
        img = Image.open(io.BytesIO(base64.b64decode(encoded, validate=True)))
    except (binascii.Error, UnidentifiedImageError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid image") from None
    return {"status": predict(model, img)}

