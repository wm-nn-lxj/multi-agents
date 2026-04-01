#!/usr/bin/env python3
"""
简单启动脚本 - 网页控制台
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ============ HTML页面 ============

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Multi-Agent Console</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif;
            background: #1a1a2e; 
            color: #fff;
            min-height: 100vh;
        }
        .header {
            background: #16213e;
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid #333;
        }
        .container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            padding: 15px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .window {
            background: #16213e;
            border-radius: 8px;
            border: 1px solid #333;
            height: 400px;
            display: flex;
            flex-direction: column;
        }
        .window-header {
            padding: 10px;
            background: #0f3460;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
        }
        .window-body {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }
        .window-input {
            padding: 10px;
            border-top: 1px solid #333;
            display: flex;
            gap: 5px;
        }
        .window-input input {
            flex: 1;
            padding: 8px;
            border: 1px solid #333;
            border-radius: 4px;
            background: #1a1a2e;
            color: #fff;
        }
        .window-input button {
            padding: 8px 15px;
            background: #e94560;
            border: none;
            border-radius: 4px;
            color: #fff;
            cursor: pointer;
        }
        .msg {
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            font-size: 13px;
        }
        .msg-user { background: #0f3460; text-align: right; }
        .msg-agent { background: #1a1a2e; }
        .msg-system { background: #533483; text-align: center; font-size: 11px; }
        .status { font-size: 11px; color: #4ade80; }
        .status.working { color: #f59e0b; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Multi-Agent Console</h1>
        <div id="status">Status: <span class="status">Connected</span></div>
    </div>
    
    <div class="container">
        <div class="window" id="product-window">
            <div class="window-header">
                <span>📋 Product Agent</span>
                <span class="status" id="product-status">idle</span>
            </div>
            <div class="window-body" id="product-msgs"></div>
            <div class="window-input">
                <input id="product-input" placeholder="Type message..." onkeypress="if(event.key==='Enter')send('product')">
                <button onclick="send('product')">Send</button>
            </div>
        </div>
        
        <div class="window" id="architect-window">
            <div class="window-header">
                <span>🏗️ Architect Agent</span>
                <span class="status" id="architect-status">idle</span>
            </div>
            <div class="window-body" id="architect-msgs"></div>
            <div class="window-input">
                <input id="architect-input" placeholder="Type message..." onkeypress="if(event.key==='Enter')send('architect')">
                <button onclick="send('architect')">Send</button>
            </div>
        </div>
        
        <div class="window" id="developer-window">
            <div class="window-header">
                <span>💻 Developer Agent</span>
                <span class="status" id="developer-status">idle</span>
            </div>
            <div class="window-body" id="developer-msgs"></div>
            <div class="window-input">
                <input id="developer-input" placeholder="Type message..." onkeypress="if(event.key==='Enter')send('developer')">
                <button onclick="send('developer')">Send</button>
            </div>
        </div>
        
        <div class="window" id="reviewer-window">
            <div class="window-header">
                <span>🔍 Reviewer Agent</span>
                <span class="status" id="reviewer-status">idle</span>
            </div>
            <div class="window-body" id="reviewer-msgs"></div>
            <div class="window-input">
                <input id="reviewer-input" placeholder="Type message..." onkeypress="if(event.key==='Enter')send('reviewer')">
                <button onclick="send('reviewer')">Send</button>
            </div>
        </div>
        
        <div class="window" id="tester-window">
            <div class="window-header">
                <span>🧪 Tester Agent</span>
                <span class="status" id="tester-status">idle</span>
            </div>
            <div class="window-body" id="tester-msgs"></div>
            <div class="window-input">
                <input id="tester-input" placeholder="Type message..." onkeypress="if(event.key==='Enter')send('tester')">
                <button onclick="send('tester')">Send</button>
            </div>
        </div>
        
        <div class="window" id="system-window">
            <div class="window-header">
                <span>📊 System Log</span>
                <span class="status">monitoring</span>
            </div>
            <div class="window-body" id="system-msgs"></div>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket(`ws://${location.host}/ws`);
        
        ws.onopen = () => addMsg('system', 'Connected to server', 'system');
        ws.onclose = () => addMsg('system', 'Disconnected', 'system');
        
        ws.onmessage = (e) => {
            const d = JSON.parse(e.data);
            if (d.type === 'msg') addMsg(d.agent, d.content, 'agent');
            else if (d.type === 'status') {
                const el = document.getElementById(d.agent + '-status');
                if (el) { el.textContent = d.status; el.className = 'status ' + d.status; }
            }
            else if (d.type === 'sys') addMsg('system', d.content, 'system');
        };
        
        function addMsg(agent, content, type) {
            const container = document.getElementById(agent + '-msgs');
            if (!container) return;
            const div = document.createElement('div');
            div.className = 'msg msg-' + type;
            div.textContent = content.substring(0, 300) + (content.length > 300 ? '...' : '');
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
        
        function send(agent) {
            const input = document.getElementById(agent + '-input');
            const content = input.value.trim();
            if (!content) return;
            
            ws.send(JSON.stringify({type: 'msg', agent, content}));
            addMsg(agent, content, 'user');
            input.value = '';
        }
    </script>
</body>
</html>
"""

# ============ WebSocket管理 ============

class ConnectionManager:
    def __init__(self):
        self.connections = []
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)
    
    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)
    
    async def broadcast(self, data: dict):
        for conn in self.connections:
            try:
                await conn.send_json(data)
            except:
                pass

manager = ConnectionManager()

# ============ Agent处理 ============

async def process_agent_message(agent: str, content: str):
    """处理Agent消息"""
    from src.core import get_llm_client
    from src.agents import ProductAgent, ArchitectAgent, DeveloperAgent, ReviewerAgent, TesterAgent
    
    # 更新状态
    await manager.broadcast({"type": "status", "agent": agent, "status": "working"})
    
    try:
        llm = get_llm_client()
        
        agents = {
            "product": ProductAgent,
            "architect": ArchitectAgent,
            "developer": DeveloperAgent,
            "reviewer": ReviewerAgent,
            "tester": TesterAgent
        }
        
        if agent in agents:
            agent_inst = agents[agent](llm_client=llm)
            result = await agent_inst.execute(content, {})
            
            if result.success and result.output:
                response = result.output[:500] + ("..." if len(result.output) > 500 else "")
                await manager.broadcast({"type": "msg", "agent": agent, "content": response})
            else:
                await manager.broadcast({"type": "sys", "content": f"Error: {result.error or 'No response'}"})
    except Exception as e:
        await manager.broadcast({"type": "sys", "content": f"Error: {str(e)}"})
    finally:
        await manager.broadcast({"type": "status", "agent": agent, "status": "idle"})

# ============ FastAPI应用 ============

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return HTMLResponse(content=HTML_PAGE)

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = json.loads(await ws.receive_text())
            if data.get("type") == "msg":
                await process_agent_message(data["agent"], data["content"])
    except WebSocketDisconnect:
        manager.disconnect(ws)

# ============ 启动 ============

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Multi-Agent Web Console")
    print("="*50)
    print("\n  Local: http://localhost:8080")
    print("  Network: http://0.0.0.0:8080")
    print("\n" + "="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
