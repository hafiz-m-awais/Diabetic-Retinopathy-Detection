# RetinaScan: Diabetic Retinopathy Detection System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20ECR%20%7C%20S3-FF9900?style=flat&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

An end-to-end, serverless machine learning system to automate Diabetic Retinopathy (DR) grading using an **EfficientNetV2-S** model. This project was developed as part of an MS Thesis and published in IEEE Access (2025).

The system features a highly scalable inference backend deployed on **AWS Lambda** using **Docker** containers, coupled with a responsive, interactive frontend web application hosted on **AWS S3**.

---

## 📖 Publication
**Improving Inference Time in Diabetic Retinopathy - Recent Trends and Future Directions**  
*IEEE Access, 2025*  
[DOI: 10.1109/ACCESS.2025.3607992](https://ieeexplore.ieee.org/document/11153952/)

---

## ✨ Features
* **State-of-the-Art Model:** Uses EfficientNetV2-S trained on the APTOS 2019 dataset for 5-class severity grading.
* **Serverless Architecture:** Cost-effective inference utilizing AWS Lambda and Amazon ECR.
* **Interactive UI:** Drag-and-drop web interface providing real-time multi-class probability metrics and visual confidence scores.
* **Automated Deployment:** One-click deployment script (`deploy.sh`) to provision AWS infrastructure and container registries.

---

## 📂 Project Structure
```text
dr-deployment/
├── app.py                  ← FastAPI inference server
├── requirements.txt        ← Python dependencies
├── Dockerfile              ← Lambda container image
├── deploy.sh               ← One-shot AWS deployment script
├── frontend/
│   └── index.html          ← Web UI (hosted on S3)
└── efficientnetv2_best.pth ← Model weights (to be provided prior to build)
```

---

## 🚀 Deployment Guide (AWS)

### 1. Copy Your Model
Before building, place your `.pth` model file into the root of this folder. The Dockerfile bakes the model weights directly into the container image.
```bash
cp "path/to/your/efficientnetv2_best.pth" ./efficientnetv2_best.pth
```
*(Note: Docker must be running on your machine.)*

### 2. One-Command Deployment
If you have AWS CLI configured and Docker running, simply use the deployment script:
```bash
# 1. Make the script executable
chmod +x deploy.sh

# 2. Edit AWS_REGION in deploy.sh if needed (default: us-east-1)

# 3. Run it
bash deploy.sh
```
The script will output your API URL and frontend S3 URL when finished.

### 3. Manual Deployment (Alternative)
If you prefer to deploy manually step-by-step:

**Step 1:** Build the Docker image
```bash
docker build --platform linux/amd64 -t dr-detection-api:latest .
```

**Step 2:** Push to AWS ECR
```bash
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1

aws ecr create-repository --repository-name dr-detection-api --region $REGION

aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com

docker tag dr-detection-api:latest $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/dr-detection-api:latest
docker push $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/dr-detection-api:latest
```

**Step 3:** Deploy Lambda Function
```bash
aws lambda create-function \
  --function-name dr-detection-api \
  --package-type Image \
  --code ImageUri=$AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/dr-detection-api:latest \
  --role arn:aws:iam::$AWS_ACCOUNT:role/dr-detection-lambda-role \
  --memory-size 3008 \
  --timeout 30 \
  --region $REGION
```

**Step 4:** Generate Public URL
```bash
aws lambda create-function-url-config \
  --function-name dr-detection-api \
  --auth-type NONE \
  --region $REGION
```

---

## 🧪 Testing the API

**Health Check endpoint:**
```bash
curl https://YOUR_LAMBDA_URL/health
```

**Prediction Endpoint:**
```bash
curl -X POST https://YOUR_LAMBDA_URL/predict \
     -F "file=@retinal_image.jpg"
```

**Expected JSON Response:**
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

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'app'` | Make sure CMD in Dockerfile is `["app.handler"]` |
| **Model not found** at startup | Check `MODEL_PATH` env var matches Dockerfile `COPY` path |
| **State dict key mismatch** | Your checkpoint uses a wrapper key — check `state["model_state_dict"]` handling in `app.py` |
| **Lambda timeout** | Increase `--timeout` to 60; cold starts loading the PyTorch model take ~5–8 sec |
| **CORS error in browser** | Ensure `CORSMiddleware` with `allow_origins=["*"]` is correctly set in `app.py` |
| **Wildly wrong predictions** | Ensure preprocessing matches training exactly: `Resize(224,224)` + ImageNet normalization |

---

## 💰 AWS Cost Estimate (Free Tier)

| Service | Monthly Cost |
|---|---|
| **Lambda** (1M req/month) | Free tier |
| **ECR storage** (~500MB image) | ~$0.05/month |
| **S3 frontend hosting** | ~$0.00/month |
| **Total for thesis/demo use** | **< $1/month** |
