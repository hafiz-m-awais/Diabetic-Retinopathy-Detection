# DR Detection — AWS Deployment Guide

## Project Structure
```
dr-deployment/
├── app.py                  ← FastAPI inference server
├── requirements.txt        ← Python dependencies
├── Dockerfile              ← Lambda container image
├── deploy.sh               ← One-shot deployment script
├── frontend/
│   └── index.html          ← Web UI (hosted on S3)
└── efficientnetv2_best.pth ← YOUR MODEL (copy here first!)
```

---

## Before You Start — Copy Your Model

```bash
# Copy your .pth file into this folder
cp "d:/Semester_4/MS Thesis/.../efficientnetv2_best.pth" ./efficientnetv2_best.pth
```

> The Dockerfile bakes the model into the container image.
> Docker must be running on your machine.

---

## One-Command Deployment

```bash
# 1. Make the script executable
chmod +x deploy.sh

# 2. Edit AWS_REGION in deploy.sh if needed (default: us-east-1)

# 3. Run it
bash deploy.sh
```

The script will print your API URL and frontend URL when done.

---

## Manual Steps (if you prefer)

### Step 1 — Build the Docker image
```bash
docker build --platform linux/amd64 -t dr-detection-api:latest .
```

### Step 2 — Push to AWS ECR
```bash
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1

aws ecr create-repository --repository-name dr-detection-api --region $REGION

aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com

docker tag dr-detection-api:latest \
  $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/dr-detection-api:latest

docker push $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/dr-detection-api:latest
```

### Step 3 — Deploy Lambda
```bash
# Create IAM role first (see deploy.sh for full trust policy)
# Then:
aws lambda create-function \
  --function-name dr-detection-api \
  --package-type Image \
  --code ImageUri=$AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/dr-detection-api:latest \
  --role arn:aws:iam::$AWS_ACCOUNT:role/dr-detection-lambda-role \
  --memory-size 3008 \
  --timeout 30 \
  --region $REGION
```

### Step 4 — Get public URL
```bash
aws lambda create-function-url-config \
  --function-name dr-detection-api \
  --auth-type NONE \
  --region $REGION
```

---

## Test the API

```bash
# Health check
curl https://YOUR_LAMBDA_URL/health

# Prediction
curl -X POST https://YOUR_LAMBDA_URL/predict \
     -F "file=@retinal_image.jpg"
```

**Response format:**
```json
{
  "grade": 2,
  "label": "Moderate DR",
  "severity": "Moderate",
  "color": "#f59e0b",
  "confidence": 87.34,
  "all_probs": {
    "No DR": 2.1,
    "Mild DR": 5.3,
    "Moderate DR": 87.34,
    "Severe DR": 3.8,
    "Proliferative DR": 1.46
  }
}
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'app'` | Make sure CMD in Dockerfile is `["app.handler"]` |
| Model not found at startup | Check MODEL_PATH env var matches Dockerfile COPY path |
| State dict key mismatch | Your checkpoint uses a wrapper key — check `state["model_state_dict"]` handling in app.py |
| Lambda timeout | Increase `--timeout` to 60; cold start loads the model (~5–8 sec) |
| CORS error in browser | CORSMiddleware with `allow_origins=["*"]` is already set |
| Image too dark / wrong predictions | Ensure preprocessing matches training: Resize(224,224) + ImageNet normalization |

---

## Cost Estimate (AWS Free Tier)

| Service | Cost |
|---|---|
| Lambda (1M req/month) | Free tier |
| ECR storage (~500MB image) | ~$0.05/month |
| S3 frontend | ~$0.00/month |
| **Total for thesis/demo use** | **< $1/month** |
