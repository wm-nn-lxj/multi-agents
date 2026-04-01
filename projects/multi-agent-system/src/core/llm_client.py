"""
LLM客户端 - 统一的大模型调用接口
支持OpenAI API兼容接口，支持SSE流式响应
"""
import asyncio
from typing import Optional, AsyncGenerator
import logging
import httpx
import json
from pydantic import BaseModel

from config import LLMConfig


logger = logging.getLogger("llm_client")


class LLMResponse(BaseModel):
    """LLM响应"""
    content: str
    tokens_used: int
    model: str
    finish_reason: str


class LLMClient:
    """LLM客户端"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=120.0)
        # 特殊headers支持
        self.extra_headers = {
            "Accept": "text/event-stream",
            "x-request-from": "openclaw",
            "x-uid": "260086000020573795",
            "x-api-key": config.api_key or ""
        }
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        if not self.config.api_key:
            logger.warning("LLM API Key未配置，请设置OPENAI_API_KEY环境变量")
    
    def _get_headers(self) -> dict:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        headers.update(self.extra_headers)
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers
    
    def _get_url(self, endpoint: str) -> str:
        """获取完整URL"""
        base_url = self.config.base_url or "https://api.openai.com/v1"
        return f"{base_url.rstrip('/')}/{endpoint}"
    
    async def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> LLMResponse:
        """聊天补全"""
        if not self.config.api_key:
            raise ValueError("LLM API Key未配置，请先配置API密钥")
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": True  # 强制使用流式
        }
        
        try:
            # 使用流式请求
            full_content = ""
            tokens_used = 0
            
            async with self.client.stream(
                "POST",
                self._get_url("chat/completions"),
                headers=self._get_headers(),
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    full_content += delta["content"]
                            if "usage" in chunk:
                                tokens_used = chunk["usage"].get("total_tokens", 0)
                        except json.JSONDecodeError:
                            continue
            
            # 估算token（如果API没返回）
            if tokens_used == 0:
                tokens_used = len(full_content) // 2
            
            return LLMResponse(
                content=full_content,
                tokens_used=tokens_used,
                model=self.config.model,
                finish_reason="stop"
            )
        
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    async def chat_stream(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """流式聊天补全"""
        if not self.config.api_key:
            raise ValueError("LLM API Key未配置，请先配置API密钥")
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": True
        }
        
        try:
            async with self.client.stream(
                "POST",
                self._get_url("chat/completions"),
                headers=self._get_headers(),
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        
        except Exception as e:
            logger.error(f"LLM流式调用失败: {e}")
            raise
    
    async def embed(self, text: str) -> list[float]:
        """生成文本嵌入向量"""
        if not self.config.api_key:
            raise ValueError("LLM API Key未配置")
        
        payload = {
            "model": self.config.embedding_model or "text-embedding-ada-002",
            "input": text
        }
        
        try:
            response = await self.client.post(
                self._get_url("embeddings"),
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data["data"][0]["embedding"]
        
        except Exception as e:
            logger.error(f"嵌入生成失败: {e}")
            raise
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局LLM客户端实例（延迟初始化）
_llm_client: Optional[LLMClient] = None


def get_llm_client(config: Optional[LLMConfig] = None) -> LLMClient:
    """获取LLM客户端实例"""
    global _llm_client
    if _llm_client is None:
        from config import config as global_config
        _llm_client = LLMClient(config or global_config.shared_llm)
    return _llm_client


async def test_llm_connection() -> tuple[bool, str]:
    """测试LLM连接"""
    try:
        client = get_llm_client()
        if not client.config.api_key:
            return False, "API Key未配置"
        
        response = await client.chat(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        return True, f"连接成功，模型: {response.model}"
    except Exception as e:
        return False, f"连接失败: {str(e)}"
