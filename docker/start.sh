#!/bin/bash
# 位于 docker/ 目录下的 start.sh

# 当任何命令失败时，立即退出脚本
set -e

# 关键步骤：切换到容器内的项目根目录 /app
# 这能确保后续所有命令的相对路径都是正确的
cd /app || exit

echo "[INFO] Current working directory: $(pwd)"

# 在前台启动 FastAPI 应用 (作为容器的主进程)
python3 run.py