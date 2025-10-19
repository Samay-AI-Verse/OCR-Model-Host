# -------------------- Base Image --------------------
FROM python:3.10-slim

# -------------------- Install System Dependencies --------------------
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && apt-get clean

# -------------------- Set Working Directory --------------------
WORKDIR /app

# -------------------- Copy Requirements and Install --------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------- Copy Project Files --------------------
COPY . .

# -------------------- Expose Port --------------------
EXPOSE 10000

# -------------------- Run FastAPI using $PORT from Render --------------------
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
