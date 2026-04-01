# 🩺 RetinaScan: Diabetic Retinopathy Detection System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20ECR%20%7C%20S3-FF9900?style=flat&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

**RetinaScan** is an end-to-end machine learning system designed to automate **Diabetic Retinopathy (DR) grading** using an **EfficientNetV2-S** model. The backend is built with **FastAPI**, containerized via **Docker**, and designed for serverless deployment on **AWS Lambda** with a responsive frontend hosted on **AWS S3**.  

🌐 **Live Demo:** [RetinaScan Web Application](http://dr-detection-frontend-858758523999.s3-website-us-east-1.amazonaws.com/)

Developed as part of an MS Thesis and published in IEEE Access (2025).  

---

## ✨ Features
* **State-of-the-Art Model:** EfficientNetV2-S trained on the **APTOS 2019 dataset** for 5-class severity grading.  
* **Serverless Ready:** Designed for AWS Lambda with Docker containers.  
* **Interactive UI:** Drag-and-drop web interface with real-time class probabilities and visual confidence scores.  
* **Cross-platform:** Fully compatible with Windows, Linux, and MacOS development environments.  
* **Clean Repo:** Model weights are excluded; scalable and lightweight repository.  

---

## 🏗️ Architecture

| Component | Technology |
|-----------|-----------|
| Model | PyTorch EfficientNetV2-S |
| Backend | FastAPI |
| Containerization | Docker |
| Deployment | AWS Lambda + ECR |
| Frontend | Static HTML hosted on AWS S3 |

---

## 📂 Project Structure

```text
dr-deployment/
├── app.py                 ← FastAPI inference server
├── requirements.txt       ← Python dependencies
├── Dockerfile             ← Container image for AWS Lambda
├── frontend/
│   └── index.html         ← Web UI hosted on S3
├── retina_image.jpg       ← Example input image
└── README.md              ← This file
```

> **Note:** Model weights (`efficientnetv2_best.pth`) are **not included** in this repository.

---

## 🔑 Model Weights

To run the system locally or deploy:

1. Place your trained model file in the root directory:
```bash
cp "path/to/efficientnetv2_best.pth" ./efficientnetv2_best.pth
```
2. Ensure `app.py` is updated with the correct path.
3. Alternatively, configure `app.py` to load the model from AWS S3 or other cloud storage.

---

## ▶️ Running Locally

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
uvicorn app:app --reload
```

Open the interactive API docs in your browser:  
👉 `http://127.0.0.1:8000/docs`

---

## 🧪 Testing the API

**Health Check endpoint:**
```bash
curl https://YOUR_API_URL/health
```

**Prediction Endpoint:**
```bash
curl -X POST https://YOUR_API_URL/predict \
     -F "file=@retina_image.jpg"
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
