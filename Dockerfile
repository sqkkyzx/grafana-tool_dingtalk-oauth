# 使用 Python 官方镜像作为基础镜像
FROM python:3.12-alpine

# 设置工作目录
WORKDIR /usr/src/myapp

# 安装基础依赖
RUN apk update && \
    pip install --upgrade pip && \
    pip install fastapi[all] colorama && \
    pip cache purge && rm -rf /var/cache/apk/*

# 安装其他依赖
RUN apk update && \
    pip install --upgrade pip && \
    pip install pyjwt -U --no-cache-dir && \
    pip cache purge && rm -rf /var/cache/apk/*

# 复制项目文件到工作目录
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]