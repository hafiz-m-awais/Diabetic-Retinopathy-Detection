# ── Base: AWS Lambda Python 3.11 runtime ─────────────────────────────────────
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Copy source code
COPY app.py .

# Copy model weights into the image
# ⚠️  Place your efficientnetv2_best.pth in the same folder before building
COPY efficientnetv2_best.pth /opt/ml/model/efficientnetv2_best.pth

# Set the model path env var (app.py reads this)
ENV MODEL_PATH=/opt/ml/model/efficientnetv2_best.pth

# Lambda handler — points to handler object inside app.py
CMD ["app.handler"]
