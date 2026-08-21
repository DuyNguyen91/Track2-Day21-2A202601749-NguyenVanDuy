from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os

app = FastAPI()

S3_BUCKET = os.environ.get("S3_BUCKET", os.environ.get("CLOUD_BUCKET"))
S3_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")

def download_model():
    """Tải file model.pkl từ AWS S3 về máy."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    s3 = boto3.client("s3")
    s3.download_file(S3_BUCKET, S3_MODEL_KEY, MODEL_PATH)
    print(f"Downloaded model from s3://{S3_BUCKET}/{S3_MODEL_KEY} to {MODEL_PATH}")

# Server khởi động sẽ load model (nếu đã có trên S3)
try:
    download_model()
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Warning: Model not loaded yet: {e}")
    model = None

class PredictRequest(BaseModel):
    features: list[float]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    global model
    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")
    if model is None:
        download_model()
        model = joblib.load(MODEL_PATH)
    
    pred = int(model.predict([req.features])[0])
    label_map = {0: "thap", 1: "trung_binh", 2: "cao"}
    return {"prediction": pred, "label": label_map.get(pred, "unknown")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
