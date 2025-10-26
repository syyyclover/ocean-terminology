# 海洋防灾减灾知识库术语识别系统 Docker镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY . .

# 创建数据目录
RUN mkdir -p data/raw data/processed output

# 设置入口点
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 暴露端口（如果需要Web服务）
# EXPOSE 5000

# 设置默认命令
CMD ["/entrypoint.sh"]