#!/usr/bin/env python3
"""
启动网页控制台服务
支持本地和公网访问
"""
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("console_server")


def create_app() -> FastAPI:
    """创建完整应用"""
    from src.console.web_console import get_html_page, manager, handle_agent_message
    from fastapi import WebSocket, WebSocketDisconnect
    import json
    
    app = FastAPI(
        title="Multi-Agent Console",
        description="Web console for multi-agent system",
        version="1.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def get_console():
        """获取控制台页面"""
        return HTMLResponse(content=get_html_page())
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket端点"""
        await manager.connect(websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                await handle_agent_message(message)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    return app


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent Console Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind")
    parser.add_argument("--public", action="store_true", help="Enable public access via ngrok")
    args = parser.parse_args()
    
    app = create_app()
    
    print("\n" + "=" * 60)
    print("  Multi-Agent Web Console")
    print("=" * 60)
    print(f"\n  Local URL: http://localhost:{args.port}")
    print(f"  Network URL: http://0.0.0.0:{args.port}")
    
    if args.public:
        print("\n  Starting ngrok tunnel for public access...")
        try:
            import subprocess
            # 启动ngrok
            ngrok_process = subprocess.Popen(
                ["ngrok", "http", str(args.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待ngrok启动
            import time
            time.sleep(3)
            
            # 获取公网地址
            import httpx
            try:
                response = httpx.get("http://localhost:4040/api/tunnels")
                tunnels = response.json().get("tunnels", [])
                if tunnels:
                    public_url = tunnels[0].get("public_url", "")
                    print(f"\n  🌐 Public URL: {public_url}")
                    print("\n  Share this URL to access the console from anywhere!")
            except:
                print("\n  ⚠️ Could not get ngrok public URL")
                print("  Make sure ngrok is installed and running")
                
        except FileNotFoundError:
            print("\n  ⚠️ ngrok not found. Install it from https://ngrok.com")
            print("  Continuing with local access only...")
    
    print("\n" + "=" * 60)
    print("  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
