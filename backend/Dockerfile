FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设置代理环境变量
ENV HTTPS_PROXY=http://host.docker.internal:7897
ENV HTTP_PROXY=http://host.docker.internal:7897
ENV ALL_PROXY=socks5://host.docker.internal:7897

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 下载 spaCy 模型
RUN python -m spacy download zh_core_web_sm

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]