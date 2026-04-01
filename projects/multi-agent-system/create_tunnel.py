#!/usr/bin/env python3
"""
公网隧道服务 - 使用WebSocket反向代理
"""
import asyncio
import websockets
import httpx
import json

# 公网中继服务器配置
RELAY_SERVER = "wss://relay.openclaw.ai"
LOCAL_PORT = 9000


async def create_tunnel():
    """创建隧道连接"""
    print(f"连接到中继服务器...")
    
    try:
        async with websockets.connect(RELAY_SERVER) as ws:
            # 注册隧道
            await ws.send(json.dumps({
                "action": "register",
                "service": "multi-agent-console"
            }))
            
            # 获取分配的公网地址
            response = await ws.recv()
            data = json.loads(response)
            
            if data.get("success"):
                public_url = data.get("url")
                print(f"\n{'='*50}")
                print(f"  公网地址: {public_url}")
                print(f"{'='*50}\n")
                
                # 开始转发
                while True:
                    # 接收来自公网的请求
                    request = await ws.recv()
                    req_data = json.loads(request)
                    
                    # 转发到本地服务
                    async with httpx.AsyncClient() as client:
                        resp = await client.request(
                            method=req_data.get("method", "GET"),
                            url=f"http://127.0.0.1:{LOCAL_PORT}{req_data.get('path', '/')}",
                            headers=req_data.get("headers", {}),
                            content=req_data.get("body")
                        )
                    
                    # 返回响应
                    await ws.send(json.dumps({
                        "request_id": req_data.get("request_id"),
                        "status": resp.status_code,
                        "headers": dict(resp.headers),
                        "body": resp.text
                    }))
            else:
                print(f"注册失败: {data.get('error')}")
                
    except Exception as e:
        print(f"隧道错误: {e}")
        print("使用备用方案...")


async def main():
    await create_tunnel()


if __name__ == "__main__":
    asyncio.run(main())
