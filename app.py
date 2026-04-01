import io
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import efficientnet_v2_s
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DR Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DR class definitions ──────────────────────────────────────────────────────
DR_CLASSES = {
    0: {"label": "No DR",            "severity": "None",     "color": "#22c55e"},
    1: {"label": "Mild DR",          "severity": "Mild",     "color": "#84cc16"},
    2: {"label": "Moderate DR",      "severity": "Moderate", "color": "#f59e0b"},
    3: {"label": "Severe DR",        "severity": "Severe",   "color": "#ef4444"},
    4: {"label": "Proliferative DR", "severity": "Critical", "color": "#7c3aed"},
}

# ── Image transform — must exactly match training ─────────────────────────────
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

model = None   # lazy singleton

def load_model():
    global model
    if model is not None:
        return model

    device = torch.device("cpu")
    logger.info("Loading EfficientNetV2-S …")

    net = efficientnet_v2_s(weights=None)
    in_features = net.classifier[1].in_features   # 1280
    net.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 5),
    )

    model_path = os.environ.get("MODEL_PATH", "/opt/ml/model/efficientnetv2_best.pth")
    state = torch.load(model_path, map_location=device)

    # Support both raw state_dict and wrapped checkpoint dicts
    if isinstance(state, dict) and "model_state_dict" in state:
        state = state["model_state_dict"]
    elif isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]

    net.load_state_dict(state)
    net.eval().to(device)
    model = net
    logger.info("Model ready.")
    return model


@app.on_event("startup")
async def startup_event():
    load_model()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Upload must be a JPEG or PNG image.")

    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image too large — 10 MB maximum.")

    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Cannot decode image.")

    net    = load_model()
    tensor = TRANSFORM(image).unsqueeze(0)

    with torch.no_grad():
        logits = net(tensor)
        probs  = torch.softmax(logits, dim=1)[0]
        grade  = int(torch.argmax(probs).item())

    confidence = round(float(probs[grade].item()) * 100, 2)
    all_probs  = {
        DR_CLASSES[i]["label"]: round(float(probs[i].item()) * 100, 2)
        for i in range(5)
    }

    return {
        "grade":      grade,
        "label":      DR_CLASSES[grade]["label"],
        "severity":   DR_CLASSES[grade]["severity"],
        "color":      DR_CLASSES[grade]["color"],
        "confidence": confidence,
        "all_probs":  all_probs,
    }


# AWS Lambda entry-point
handler = Mangum(app)
