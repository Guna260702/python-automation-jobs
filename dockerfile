FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc \
    && rm -rf /var/lib/apt/lists/*

COPY *.py .

CMD ["python", "leetcode_bot.py"]   