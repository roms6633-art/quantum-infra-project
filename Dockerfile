FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    python3-tk \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# מעתיקים רק את קובץ הפייתון, בלי תמונות!
COPY app.py .

CMD ["python", "app.py"]