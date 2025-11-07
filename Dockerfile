FROM python:3.11-slim

# Cài Tesseract + tiếng Việt
RUN apt update && apt install -y tesseract-ocr tesseract-ocr-vie && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
