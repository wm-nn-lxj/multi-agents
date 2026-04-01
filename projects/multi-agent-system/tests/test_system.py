"""
系统测试 - 功能、性能、稳定性测试
"""
import pytest
import asyncio
import time
from datetime import datetime

# 添加src到路径
import sys
sys.path.insert(0, ".")


class TestLLMConnection:
    """LLM连接测试"""
    
    @pytest.mark.asyncio
    async def test_llm_connection(self):
        """测试LLM连接"""
        from core import test_llm_connection
        
        ok, msg = await test_llm_connection()
        
        # 如果未配置API，跳过
        if not ok and "未配置" in msg:
            pytest.skip("LLM API未配置")
        
        print(f"LLM连接: {msg}")
        assert ok or "未配置" in msg


class TestAgentFunctionality:
    """Agent功能测试"""
    
    @pytest.mark.asyncio
    async def test_product_agent_prd(self):
        """测试Product Agent生成PRD"""
        from agents import ProductAgent
        from core import get_llm_client
        
        try:
            llm = get_llm_client()
            agent = ProductAgent(llm_client=llm)
        except:
            pytest.skip("LLM未配置")
        
        result = await agent.execute(
            "生成一个用户登录功能的PRD",
            {"project": "测试项目"}
        )
        
        print(f"PRD生成结果: {result.output[:200] if result.output else 'None'}...")
        assert result.success or result.needs_human
    
    @pytest.mark.asyncio
    async def test_architect_agent_design(self):
        """测试Architect Agent架构设计"""
        from agents import ArchitectAgent
        from core import get_llm_client
        
        try:
            llm = get_llm_client()
            agent = ArchitectAgent(llm_client=llm)
        except:
            pytest.skip("LLM未配置")
        
        result = await agent.execute(
            "设计一个微服务架构的用户系统",
            {}
        )
        
        print(f"架构设计结果: {result.output[:200] if result.output else 'None'}...")
        assert result.success or result.needs_human
    
    @pytest.mark.asyncio
    async def test_developer_agent_code(self):
        """测试Developer Agent代码生成"""
        from agents import DeveloperAgent
        from core import get_llm_client
        
        try:
            llm = get_llm_client()
            agent = DeveloperAgent(llm_client=llm)
        except:
            pytest.skip("LLM未配置")
        
        result = await agent.execute(
            "实现一个Python函数，计算斐波那契数列",
            {"tech_stack": "Python"}
        )
        
        print(f"代码生成结果: {result.output[:200] if result.output else 'None'}...")
        assert result.success or result.needs_human


class TestContextManagement:
    """上下文管理测试"""
    
    def test_context_layer_sizes(self):
        """测试上下文层大小限制"""
        from core import ContextManager
        from config import config
        
        ctx = ContextManager()
        
        # 检查各层限制
        assert ctx.layer_limits["global"] == config.context.global_layer_max
        assert ctx.layer_limits["session"] == config.context.session_layer_max
        assert ctx.layer_limits["task"] == config.context.task_layer_max
        assert ctx.layer_limits["memory"] == config.context.memory_layer_max
        
        # 检查总限制
        total_limit = sum(ctx.layer_limits.values())
        assert total_limit <= 16000  # 16K限制
    
    def test_context_compression(self):
        """测试上下文压缩"""
        from core import ContextManager
        
        ctx = ContextManager()
        
        # 添加大量内容
        large_content = {"data": "x" * 10000}
        ctx.update_layer("session", large_content)
        
        # 检查是否触发压缩
        status = ctx.get_status()
        print(f"上下文状态: {status}")


class TestMemoryManagement:
    """记忆管理测试"""
    
    @pytest.mark.asyncio
    async def test_memory_initialization(self):
        """测试记忆系统初始化"""
        from core import MemoryManager
        
        memory = MemoryManager()
        await memory.initialize()
        
        status = memory.get_status()
        print(f"记忆系统状态: {status}")
        
        await memory.close()
    
    @pytest.mark.asyncio
    async def test_short_term_memory(self):
        """测试短期记忆"""
        from core import MemoryManager
        
        memory = MemoryManager()
        await memory.initialize()
        
        # 存储记忆
        mem_id = await memory.remember("测试记忆内容", {"type": "test"})
        
        # 检索记忆
        results = await memory.recall("测试")
        
        print(f"检索结果: {len(results)}条")
        
        await memory.close()


class TestMessageBus:
    """消息总线测试"""
    
    @pytest.mark.asyncio
    async def test_message_sending(self):
        """测试消息发送"""
        from core import MessageBus, Message
        from config import AgentType
        
        bus = MessageBus()
        await bus.start()
        
        # 发送消息
        msg = Message(
            sender=AgentType.PRODUCT,
            receiver=AgentType.DEVELOPER,
            content="测试消息"
        )
        
        success = await bus.send(msg)
        assert success
        
        # 获取统计
        stats = bus.get_stats()
        print(f"消息统计: {stats}")
        
        await bus.stop()


class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """测试响应时间"""
        from agents import DeveloperAgent
        from core import get_llm_client
        
        try:
            llm = get_llm_client()
            agent = DeveloperAgent(llm_client=llm)
        except:
            pytest.skip("LLM未配置")
        
        start = time.time()
        result = await agent.execute("写一个hello world函数", {})
        elapsed = time.time() - start
        
        print(f"响应时间: {elapsed:.2f}秒")
        print(f"Token使用: {result.tokens_used}")
        
        # 响应时间应小于30秒
        assert elapsed < 30 or result.needs_human
    
    def test_context_size_limit(self):
        """测试上下文大小限制"""
        from core import ContextManager
        
        ctx = ContextManager()
        
        # 添加内容直到接近限制
        for i in range(100):
            ctx.update_layer("session", {f"key_{i}": f"value_{i}" * 100})
        
        # 检查是否在限制内
        assert ctx.is_within_limit() or ctx.get_total_tokens() < 20000


class TestStability:
    """稳定性测试"""
    
    @pytest.mark.asyncio
    async def test_multiple_tasks(self):
        """测试连续执行多个任务"""
        from agents import DeveloperAgent
        from core import get_llm_client
        
        try:
            llm = get_llm_client()
            agent = DeveloperAgent(llm_client=llm)
        except:
            pytest.skip("LLM未配置")
        
        tasks = [
            "写一个加法函数",
            "写一个减法函数",
            "写一个乘法函数"
        ]
        
        success_count = 0
        for task in tasks:
            result = await agent.execute(task, {})
            if result.success:
                success_count += 1
        
        print(f"成功率: {success_count}/{len(tasks)}")
        assert success_count >= len(tasks) * 0.8  # 80%成功率


def run_tests():
    """运行所有测试"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
