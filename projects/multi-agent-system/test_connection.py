#!/usr/bin/env python3
"""
LLM连通性测试脚本
"""
import asyncio
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.core.llm_client import LLMClient, LLMConfig


async def test_connection():
    """测试LLM连接"""
    print("=" * 50)
    print("LLM 连通性测试")
    print("=" * 50)
    
    # 从环境变量读取配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("LLM_MODEL", "LLM_GLM5")
    
    print(f"\n配置信息:")
    print(f"  API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'N/A'}")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    
    if not api_key:
        print("\n❌ 错误: 未配置OPENAI_API_KEY")
        return False
    
    # 创建客户端
    config = LLMConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        max_tokens=100
    )
    
    client = LLMClient(config)
    
    print(f"\n正在测试连接...")
    
    try:
        # 发送测试请求
        response = await client.chat(
            messages=[{"role": "user", "content": "你好，请回复'连接成功'"}],
            max_tokens=50
        )
        
        print(f"\n✅ 连接成功!")
        print(f"  模型: {response.model}")
        print(f"  响应: {response.content[:100]}")
        print(f"  Token使用: {response.tokens_used}")
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        return False
    
    finally:
        await client.close()


async def test_agent():
    """测试Agent功能"""
    print("\n" + "=" * 50)
    print("Agent 功能测试")
    print("=" * 50)
    
    from src.core.llm_client import get_llm_client
    from src.agents import DeveloperAgent
    
    try:
        llm = get_llm_client()
        agent = DeveloperAgent(llm_client=llm)
        
        print("\n正在测试Developer Agent...")
        result = await agent.execute(
            "写一个Python函数，计算两个数的和",
            {"tech_stack": "Python"}
        )
        
        if result.success:
            print(f"\n✅ Agent执行成功!")
            print(f"  Token使用: {result.tokens_used}")
            print(f"  执行时间: {result.execution_time:.2f}秒")
            print(f"  输出预览: {result.output[:200]}...")
            return True
        else:
            print(f"\n❌ Agent执行失败: {result.error}")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


async def main():
    """主函数"""
    # 测试连接
    connected = await test_connection()
    
    if connected:
        # 测试Agent
        agent_ok = await test_agent()
        
        print("\n" + "=" * 50)
        print("测试结果汇总")
        print("=" * 50)
        print(f"  LLM连接: {'✅ 通过' if connected else '❌ 失败'}")
        print(f"  Agent功能: {'✅ 通过' if agent_ok else '❌ 失败'}")
        
        if connected and agent_ok:
            print("\n🎉 所有测试通过！系统已就绪。")
            return 0
        else:
            print("\n⚠️ 部分测试未通过，请检查配置。")
            return 1
    else:
        print("\n❌ LLM连接失败，无法继续测试。")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
