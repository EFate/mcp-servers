# 位于 docker/ 目录下的 Dockerfile

FROM python:3.10-slim

# 1. 配置 pip 和 uv 的国内镜像源 (可选，但推荐)
# uv 会自动识别和使用 pip 的配置
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    # 使用配置好的镜像源升级 pip 并安装 uv
    pip install --no-cache-dir --upgrade pip uv

# 2. 创建并设置工作目录
WORKDIR /app

# 3. 复制依赖定义文件
# 优先复制这两个文件，以便利用 Docker 的层缓存。
# 只要这两个文件不变，后续的依赖安装步骤就不会重复执行，从而加快构建速度。
COPY pyproject.toml uv.lock* ./

# 4.安装依赖
RUN uv pip install --system --no-cache -r pyproject.toml

# 5. 将项目所有文件复制到工作目录
# 这一步在安装完依赖之后执行。由于有 .dockerignore 文件，不必要的内容不会被复制。
COPY . .

# 6. 赋予启动脚本执行权限
RUN chmod +x /app/docker/start.sh

# 7. 暴露 FastAPI 应用端口
EXPOSE 13000

# 8. 定义容器启动命令
# 使用绝对路径，确保命令的准确性
CMD ["./docker/start.sh"]