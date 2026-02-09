FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-dev \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-rus \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download ru_core_news_sm

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]