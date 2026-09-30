FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 HF_HOME=/cache/hf

WORKDIR /srv

RUN apt-get update \
 && apt-get install -y --no-install-recommends libgomp1 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.6.0 \
 && pip install --no-cache-dir -r requirements.txt

COPY train.py .
COPY data ./data

CMD ["python", "train.py", "--out", "/models/intent"]
