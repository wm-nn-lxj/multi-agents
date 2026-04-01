#!/bin/bash
# 多Agent协作系统 - 启动脚本

set -e

echo "=========================================="
echo "  多Agent协作系统 - 启动脚本"
echo "=========================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt -q

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，请复制.env.example并配置"
    echo "cp .env.example .env"
    echo ""
    echo "请至少配置OPENAI_API_KEY"
    exit 1
fi

# 创建必要目录
mkdir -p data/chroma logs

# 启动服务
echo ""
echo "启动API服务..."
echo "访问地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
