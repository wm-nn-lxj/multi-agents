"""
网页控制台 - 多Agent消息窗口
提供实时消息展示和Agent交互
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
import asyncio
import json
from datetime import datetime
import logging

logger = logging.getLogger("web_console")


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.message_history: List[dict] = []
        self.max_history = 100
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # 发送历史消息
        for msg in self.message_history[-20:]:
            await websocket.send_json(msg)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


# 全局连接管理器
manager = ConnectionManager()

# Agent消息队列
agent_messages: Dict[str, List[dict]] = {
    "product": [],
    "architect": [],
    "developer": [],
    "reviewer": [],
    "tester": []
}


def get_html_page() -> str:
    """获取HTML页面"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Console</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }
        
        .status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4ade80;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-template-rows: repeat(2, 1fr);
            gap: 15px;
            padding: 20px;
            height: calc(100vh - 70px);
        }
        
        .agent-window {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .agent-header {
            padding: 12px 15px;
            background: rgba(0, 0, 0, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .agent-name {
            font-weight: 600;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .agent-icon {
            font-size: 18px;
        }
        
        .agent-status {
            font-size: 12px;
            padding: 3px 8px;
            border-radius: 10px;
            background: rgba(74, 222, 128, 0.2);
            color: #4ade80;
        }
        
        .agent-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .message {
            padding: 10px 12px;
            border-radius: 8px;
            max-width: 90%;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.sent {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            align-self: flex-end;
        }
        
        .message.received {
            background: rgba(255, 255, 255, 0.1);
            align-self: flex-start;
        }
        
        .message.system {
            background: rgba(251, 191, 36, 0.2);
            color: #fbbf24;
            align-self: center;
            text-align: center;
            font-size: 12px;
        }
        
        .message-time {
            font-size: 10px;
            opacity: 0.6;
            margin-top: 4px;
        }
        
        .input-area {
            padding: 12px;
            background: rgba(0, 0, 0, 0.2);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            gap: 10px;
        }
        
        .input-area input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 14px;
            outline: none;
        }
        
        .input-area input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        
        .input-area button {
            padding: 10px 20px;
            border: none;
            border-radius: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            font-size: 14px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .input-area button:hover {
            transform: scale(1.05);
        }
        
        /* Agent颜色主题 */
        .product .agent-header { border-left: 3px solid #f59e0b; }
        .architect .agent-header { border-left: 3px solid #3b82f6; }
        .developer .agent-header { border-left: 3px solid #10b981; }
        .reviewer .agent-header { border-left: 3px solid #ef4444; }
        .tester .agent-header { border-left: 3px solid #8b5cf6; }
        .system .agent-header { border-left: 3px solid #6b7280; }
        
        /* 滚动条样式 */
        .agent-messages::-webkit-scrollbar {
            width: 6px;
        }
        
        .agent-messages::-webkit-scrollbar-track {
            background: transparent;
        }
        
        .agent-messages::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
        }
        
        /* 响应式 */
        @media (max-width: 1200px) {
            .container {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                grid-template-rows: auto;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Multi-Agent Console</h1>
        <div class="status">
            <div class="status-dot"></div>
            <span id="connection-status">Connected</span>
        </div>
    </div>
    
    <div class="container">
        <div class="agent-window product" id="product-window">
            <div class="agent-header">
                <div class="agent-name">
                    <span class="agent-icon">📋</span>
                    Product Agent
                </div>
                <span class="agent-status" id="product-status">idle</span>
            </div>
            <div class="agent-messages" id="product-messages"></div>
            <div class="input-area">
                <input type="text" id="product-input" placeholder="Send message to Product Agent..." onkeypress="handleKeyPress(event, 'product')">
                <button onclick="sendMessage('product')">Send</button>
            </div>
        </div>
        
        <div class="agent-window architect" id="architect-window">
            <div class="agent-header">
                <div class="agent-name">
                    <span class="agent-icon">🏗️</span>
                    Architect Agent
                </div>
                <span class="agent-status" id="architect-status">idle</span>
            </div>
            <div class="agent-messages" id="architect-messages"></div>
            <div class="input-area">
                <input type="text" id="architect-input" placeholder="Send message to Architect Agent..." onkeypress="handleKeyPress(event, 'architect')">
                <button onclick="sendMessage('architect')">Send</button>
            </div>
        </div>
        
        <div class="agent-window developer" id="developer-window">
            <div class="agent-header">
                <div class="agent-name">
                    <span class="agent-icon">💻</span>
                    Developer Agent
                </div>
                <span class="agent-status" id="developer-status">idle</span>
            </div>
            <div class="agent-messages" id="developer-messages"></div>
            <div class="input-area">
                <input type="text" id="developer-input" placeholder="Send message to Developer Agent..." onkeypress="handleKeyPress(event, 'developer')">
                <button onclick="sendMessage('developer')">Send</button>
            </div>
        </div>
        
        <div class="agent-window reviewer" id="reviewer-window">
            <div class="agent-header">
                <div class="agent-name">
                    <span class="agent-icon">🔍</span>
                    Reviewer Agent
                </div>
                <span class="agent-status" id="reviewer-status">idle</span>
            </div>
            <div class="agent-messages" id="reviewer-messages"></div>
            <div class="input-area">
                <input type="text" id="reviewer-input" placeholder="Send message to Reviewer Agent..." onkeypress="handleKeyPress(event, 'reviewer')">
                <button onclick="sendMessage('reviewer')">Send</button>
            </div>
        </div>
        
        <div class="agent-window tester" id="tester-window">
            <div class="agent-header">
                <div class="agent-name">
                    <span class="agent-icon">🧪</span>
                    Tester Agent
                </div>
                <span class="agent-status" id="tester-status">idle</span>
            </div>
            <div class="agent-messages" id="tester-messages"></div>
            <div class="input-area">
                <input type="text" id="tester-input" placeholder="Send message to Tester Agent..." onkeypress="handleKeyPress(event, 'tester')">
                <button onclick="sendMessage('tester')">Send</button>
            </div>
        </div>
        
        <div class="agent-window system" id="system-window">
            <div class="agent-header">
                <div class="agent-name">
                    <span class="agent-icon">📊</span>
                    System Log
                </div>
                <span class="agent-status">monitoring</span>
            </div>
            <div class="agent-messages" id="system-messages"></div>
        </div>
    </div>
    
    <script>
        let ws;
        let reconnectAttempts = 0;
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function() {
                document.getElementById('connection-status').textContent = 'Connected';
                reconnectAttempts = 0;
                addSystemMessage('WebSocket connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function() {
                document.getElementById('connection-status').textContent = 'Disconnected';
                addSystemMessage('WebSocket disconnected, reconnecting...');
                reconnectAttempts++;
                if (reconnectAttempts < 5) {
                    setTimeout(connect, 2000);
                }
            };
            
            ws.onerror = function(error) {
                addSystemMessage('WebSocket error');
            };
        }
        
        function handleMessage(data) {
            const { type, agent, content, timestamp, status } = data;
            
            if (type === 'message') {
                addMessage(agent, content, 'received', timestamp);
            } else if (type === 'status') {
                updateAgentStatus(agent, status);
            } else if (type === 'system') {
                addSystemMessage(content);
            }
        }
        
        function addMessage(agent, content, msgType, timestamp) {
            const container = document.getElementById(`${agent}-messages`);
            if (!container) return;
            
            const msg = document.createElement('div');
            msg.className = `message ${msgType}`;
            msg.innerHTML = `
                <div>${escapeHtml(content)}</div>
                <div class="message-time">${timestamp || new Date().toLocaleTimeString()}</div>
            `;
            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;
        }
        
        function addSystemMessage(content) {
            const container = document.getElementById('system-messages');
            const msg = document.createElement('div');
            msg.className = 'message system';
            msg.innerHTML = `
                <div>${escapeHtml(content)}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;
        }
        
        function updateAgentStatus(agent, status) {
            const statusEl = document.getElementById(`${agent}-status`);
            if (statusEl) {
                statusEl.textContent = status;
                statusEl.style.background = status === 'working' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(74, 222, 128, 0.2)';
                statusEl.style.color = status === 'working' ? '#3b82f6' : '#4ade80';
            }
        }
        
        function sendMessage(agent) {
            const input = document.getElementById(`${agent}-input`);
            const content = input.value.trim();
            
            if (!content) return;
            
            const data = {
                type: 'message',
                agent: agent,
                content: content,
                timestamp: new Date().toLocaleTimeString()
            };
            
            ws.send(JSON.stringify(data));
            addMessage(agent, content, 'sent', data.timestamp);
            input.value = '';
        }
        
        function handleKeyPress(event, agent) {
            if (event.key === 'Enter') {
                sendMessage(agent);
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // 初始化连接
        connect();
    </script>
</body>
</html>
"""


def create_console_app() -> FastAPI:
    """创建控制台应用"""
    app = FastAPI(title="Multi-Agent Console")
    
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
                
                # 处理消息
                await handle_agent_message(message)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    return app


async def handle_agent_message(message: dict):
    """处理Agent消息"""
    msg_type = message.get("type")
    agent = message.get("agent")
    content = message.get("content")
    
    if msg_type == "message" and agent and content:
        # 广播用户消息
        await manager.broadcast({
            "type": "message",
            "agent": agent,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "sender": "user"
        })
        
        # 更新Agent状态
        await manager.broadcast({
            "type": "status",
            "agent": agent,
            "status": "working"
        })
        
        # 调用Agent处理
        try:
            response = await process_with_agent(agent, content)
            
            # 广播Agent响应
            await manager.broadcast({
                "type": "message",
                "agent": agent,
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "sender": "agent"
            })
        except Exception as e:
            await manager.broadcast({
                "type": "system",
                "content": f"Error: {str(e)}"
            })
        
        finally:
            # 恢复Agent状态
            await manager.broadcast({
                "type": "status",
                "agent": agent,
                "status": "idle"
            })


async def process_with_agent(agent: str, content: str) -> str:
    """调用Agent处理消息"""
    from src.core import get_llm_client
    from src.agents import ProductAgent, ArchitectAgent, DeveloperAgent, ReviewerAgent, TesterAgent
    
    llm = get_llm_client()
    
    agents = {
        "product": ProductAgent,
        "architect": ArchitectAgent,
        "developer": DeveloperAgent,
        "reviewer": ReviewerAgent,
        "tester": TesterAgent
    }
    
    if agent in agents:
        agent_instance = agents[agent](llm_client=llm)
        result = await agent_instance.execute(content, {})
        
        if result.success and result.output:
            # 截断过长输出
            output = result.output
            if len(output) > 500:
                output = output[:500] + "..."
            return output
        else:
            return f"Error: {result.error or 'No response'}"
    
    return "Unknown agent"


# 全局应用实例
console_app = create_console_app()
