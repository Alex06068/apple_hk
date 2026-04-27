FROM python:3.12-slim

WORKDIR /app

# 安裝編譯 mysqlclient 必要的系統庫
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app
COPY run.py /app/

ENV PYTHONPATH=/app
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]