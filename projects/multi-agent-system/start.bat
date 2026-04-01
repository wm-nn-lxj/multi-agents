@echo off
REM 多Agent协作系统 - Windows启动脚本

echo ==========================================
echo   多Agent协作系统 - 启动脚本
echo ==========================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    exit /b 1
)

REM 进入项目目录
cd /d "%~dp0"

REM 创建虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt -q

REM 检查环境变量
if not exist ".env" (
    echo 警告: 未找到.env文件，请复制.env.example并配置
    echo copy .env.example .env
    echo.
    echo 请至少配置OPENAI_API_KEY
    exit /b 1
)

REM 创建必要目录
if not exist "data" mkdir data
if not exist "data\chroma" mkdir data\chroma
if not exist "logs" mkdir logs

REM 启动服务
echo.
echo 启动API服务...
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
