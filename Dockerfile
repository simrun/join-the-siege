FROM python:3.12.0-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download EasyOCR models (otherwise it happens at startup)
RUN apt-get update && apt-get install -y curl unzip --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN mkdir -p models && \
  curl -fsSL https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.zip -o models/english_g2.zip && \
  unzip models/english_g2.zip -d models/ && \
  curl -fsSL https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip -o models/craft_mlt_25k.zip && \
  unzip models/craft_mlt_25k.zip -d models/

COPY src src
COPY classifier_rules.yaml .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "src.app:app"]
