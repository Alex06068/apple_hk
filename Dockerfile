FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY app /app/app
COPY run.py /app/

# --- 关键修复：添加下面这一行 ---
ENV PYTHONPATH=/app

EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]