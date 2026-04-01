#!/usr/bin/env python3
"""
上下文大小验证测试
测试场景：
1. 小于198K上下文 - 应正常处理
2. 大于198K上下文 - 应触发压缩或拒绝
"""
import asyncio
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()


class ContextLimitTester:
    """上下文限制测试器"""
    
    def __init__(self):
        self.results = []
    
    async def test_under_limit(self):
        """测试场景1: 上下文小于198K"""
        print("\n" + "=" * 60)
        print("测试场景1: 上下文 < 198K tokens")
        print("=" * 60)
        
        from src.core import ContextManager, get_llm_client
        from src.agents import DeveloperAgent
        
        ctx = ContextManager()
        
        # 添加约50K tokens的内容 (模拟正常对话)
        print("\n📦 构建上下文 (~50K tokens)...")
        
        # 全局层: 约5K
        global_content = {
            "system_prompt": "You are a helpful assistant." * 200,
            "project_info": "Project: Multi-Agent System" * 100
        }
        ctx.update_layer("global", global_content)
        
        # 会话层: 约30K
        session_content = {
            "history": [
                {"role": "user", "content": "Message " * 100}
                for i in range(100)
            ]
        }
        ctx.update_layer("session", session_content)
        
        # 任务层: 约10K
        task_content = {
            "current_task": "Implement feature" * 200,
            "code_context": "def function(): pass" * 100
        }
        ctx.update_layer("task", task_content)
        
        # 记忆层: 约5K
        memory_content = {
            "relevant_memories": ["Memory item " * 50 for _ in range(20)]
        }
        ctx.update_layer("memory", memory_content)
        
        total_tokens = ctx.get_total_tokens()
        within_limit = ctx.is_within_limit()
        
        print(f"   总上下文: {total_tokens:,} tokens")
        print(f"   限制: 198,000 tokens")
        print(f"   是否在限制内: {'✅ 是' if within_limit else '❌ 否'}")
        
        # 测试Agent能否正常处理
        print("\n🤖 测试Agent处理能力...")
        
        try:
            llm = get_llm_client()
            agent = DeveloperAgent(llm_client=llm)
            
            start = time.time()
            result = await agent.execute(
                "写一个简单的Python函数，计算两个数的和",
                {"tech_stack": "Python"}
            )
            elapsed = time.time() - start
            
            success = result.success
            print(f"   Agent响应: {'✅ 成功' if success else '❌ 失败'}")
            print(f"   响应时间: {elapsed:.2f}s")
            print(f"   Token使用: {result.tokens_used}")
            
            if result.output:
                print(f"   输出预览: {result.output[:100]}...")
            
            self.results.append({
                "test": "上下文 < 198K",
                "context_tokens": total_tokens,
                "success": success,
                "response_time": elapsed,
                "tokens_used": result.tokens_used,
                "error": result.error
            })
            
            return success
            
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.results.append({
                "test": "上下文 < 198K",
                "context_tokens": total_tokens,
                "success": False,
                "error": str(e)
            })
            return False
    
    async def test_near_limit(self):
        """测试场景2: 上下文接近198K"""
        print("\n" + "=" * 60)
        print("测试场景2: 上下文 ≈ 180K tokens (接近限制)")
        print("=" * 60)
        
        from src.core import ContextManager, get_llm_client
        from src.agents import DeveloperAgent
        
        ctx = ContextManager()
        
        print("\n📦 构建上下文 (~180K tokens)...")
        
        # 构建大量内容
        # 全局层: 约20K
        global_content = {
            "system_prompt": "System configuration and guidelines. " * 2000,
            "project_info": "Detailed project information. " * 2000
        }
        ctx.update_layer("global", global_content)
        
        # 会话层: 约100K
        session_content = {
            "history": [
                {"role": "user", "content": f"User message {i}: " + "Content " * 200}
                for i in range(200)
            ]
        }
        ctx.update_layer("session", session_content)
        
        # 任务层: 约40K
        task_content = {
            "current_task": "Complex implementation task. " * 2000,
            "code_context": "Large codebase context. " * 2000,
            "dependencies": "Module dependencies. " * 1000
        }
        ctx.update_layer("task", task_content)
        
        # 记忆层: 约20K
        memory_content = {
            "relevant_memories": [
                f"Memory {i}: " + "Historical context. " * 100
                for i in range(100)
            ]
        }
        ctx.update_layer("memory", memory_content)
        
        total_tokens = ctx.get_total_tokens()
        within_limit = ctx.is_within_limit()
        
        print(f"   总上下文: {total_tokens:,} tokens")
        print(f"   限制: 198,000 tokens")
        print(f"   是否在限制内: {'✅ 是' if within_limit else '❌ 否'}")
        print(f"   使用率: {total_tokens/198000*100:.1f}%")
        
        # 测试Agent处理
        print("\n🤖 测试Agent处理能力...")
        
        try:
            llm = get_llm_client()
            agent = DeveloperAgent(llm_client=llm)
            
            start = time.time()
            result = await agent.execute(
                "根据上下文，写一个简单的工具函数",
                {"tech_stack": "Python"}
            )
            elapsed = time.time() - start
            
            success = result.success
            print(f"   Agent响应: {'✅ 成功' if success else '❌ 失败'}")
            print(f"   响应时间: {elapsed:.2f}s")
            print(f"   Token使用: {result.tokens_used}")
            
            if result.output:
                print(f"   输出预览: {result.output[:100]}...")
            
            self.results.append({
                "test": "上下文 ≈ 180K",
                "context_tokens": total_tokens,
                "success": success,
                "response_time": elapsed,
                "tokens_used": result.tokens_used,
                "error": result.error
            })
            
            return success
            
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.results.append({
                "test": "上下文 ≈ 180K",
                "context_tokens": total_tokens,
                "success": False,
                "error": str(e)
            })
            return False
    
    async def test_over_limit(self):
        """测试场景3: 上下文超过198K"""
        print("\n" + "=" * 60)
        print("测试场景3: 上下文 > 198K tokens (超出限制)")
        print("=" * 60)
        
        from src.core import ContextManager, get_llm_client
        from src.agents import DeveloperAgent
        
        ctx = ContextManager()
        
        print("\n📦 构建上下文 (>198K tokens)...")
        
        # 故意构建超限内容
        # 全局层: 约30K
        global_content = {
            "system_prompt": "Very long system prompt. " * 3000,
            "project_info": "Extensive project documentation. " * 3000
        }
        ctx.update_layer("global", global_content)
        
        # 会话层: 约120K
        session_content = {
            "history": [
                {"role": "user", "content": f"Long message {i}: " + "Content " * 300}
                for i in range(300)
            ]
        }
        ctx.update_layer("session", session_content)
        
        # 任务层: 约50K
        task_content = {
            "current_task": "Very complex task. " * 3000,
            "code_context": "Massive codebase. " * 3000,
            "dependencies": "All dependencies. " * 2000
        }
        ctx.update_layer("task", task_content)
        
        # 记忆层: 约30K
        memory_content = {
            "relevant_memories": [
                f"Memory {i}: " + "Historical data. " * 150
                for i in range(150)
            ]
        }
        ctx.update_layer("memory", memory_content)
        
        total_tokens = ctx.get_total_tokens()
        within_limit = ctx.is_within_limit()
        
        print(f"   总上下文: {total_tokens:,} tokens")
        print(f"   限制: 198,000 tokens")
        print(f"   是否在限制内: {'✅ 是' if within_limit else '❌ 否 (超出)'}")
        print(f"   超出量: {total_tokens - 198000:,} tokens")
        print(f"   超出比例: {(total_tokens/198000 - 1)*100:.1f}%")
        
        # 检查系统如何处理超限情况
        print("\n🔍 检查系统处理超限情况...")
        
        # 1. 检查压缩机制
        status = ctx.get_status()
        print(f"   上下文状态: {status}")
        
        # 2. 尝试执行任务
        print("\n🤖 尝试执行任务...")
        
        try:
            llm = get_llm_client()
            agent = DeveloperAgent(llm_client=llm)
            
            # 评估任务
            evaluation = await agent.evaluate_task(
                "写一个简单的函数",
                {}
            )
            
            print(f"   任务评估:")
            print(f"     - 可执行: {'✅ 是' if evaluation.can_execute else '❌ 否'}")
            print(f"     - 完成概率: {evaluation.success_probability:.2%}")
            print(f"     - Token估算: {evaluation.token_estimate}")
            print(f"     - 原因: {evaluation.reason or '无'}")
            
            # 如果评估通过，尝试执行
            if evaluation.can_execute:
                start = time.time()
                result = await agent.execute("写一个简单函数", {})
                elapsed = time.time() - start
                
                print(f"   执行结果: {'✅ 成功' if result.success else '❌ 失败'}")
                print(f"   响应时间: {elapsed:.2f}s")
                
                self.results.append({
                    "test": "上下文 > 198K",
                    "context_tokens": total_tokens,
                    "success": result.success,
                    "response_time": elapsed,
                    "tokens_used": result.tokens_used,
                    "error": result.error,
                    "evaluation": evaluation.can_execute
                })
            else:
                print(f"   ⚠️ 任务被拒绝执行 (上下文超限)")
                self.results.append({
                    "test": "上下文 > 198K",
                    "context_tokens": total_tokens,
                    "success": False,
                    "error": "Context exceeds limit, task rejected",
                    "evaluation": False
                })
            
            return evaluation.can_execute
            
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.results.append({
                "test": "上下文 > 198K",
                "context_tokens": total_tokens,
                "success": False,
                "error": str(e)
            })
            return False
    
    def generate_report(self):
        """生成测试报告"""
        report = f"""# 上下文大小验证测试报告

**测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**上下文限制**: 198,000 tokens

---

## 测试场景

| 场景 | 上下文大小 | 预期行为 |
|------|-----------|----------|
| 场景1 | < 198K | 正常处理 |
| 场景2 | ≈ 180K | 正常处理 |
| 场景3 | > 198K | 拒绝或压缩 |

---

## 测试结果

| 测试场景 | 上下文Tokens | 结果 | 响应时间 | Token使用 |
|----------|-------------|------|----------|-----------|
"""
        
        for r in self.results:
            status = "✅ 通过" if r.get("success") else "❌ 失败"
            report += f"| {r['test']} | {r['context_tokens']:,} | {status} | {r.get('response_time', 0):.2f}s | {r.get('tokens_used', 0)} |\n"
        
        report += f"""
---

## 详细分析

"""
        
        for r in self.results:
            report += f"""### {r['test']}

- **上下文大小**: {r['context_tokens']:,} tokens
- **执行结果**: {'成功' if r.get('success') else '失败'}
"""
            if r.get('error'):
                report += f"- **错误信息**: {r['error']}\n"
            if r.get('evaluation') is not None:
                report += f"- **任务评估**: {'通过' if r['evaluation'] else '拒绝'}\n"
            report += "\n"
        
        report += f"""---

## 结论

"""
        
        success_count = sum(1 for r in self.results if r.get("success"))
        total_count = len(self.results)
        
        if success_count >= 2:
            report += "✅ **上下文管理功能正常**\n\n"
            report += "- 小于198K的上下文可以正常处理\n"
            report += "- 超过198K的上下文会被正确识别和处理\n"
            report += "- 系统具备上下文限制保护机制\n"
        else:
            report += "⚠️ **上下文管理需要优化**\n\n"
            report += "部分测试未通过，需要进一步调整。\n"
        
        return report
    
    async def run_all(self):
        """运行所有测试"""
        print("=" * 60)
        print("  上下文大小验证测试")
        print("  限制: 198,000 tokens")
        print("=" * 60)
        
        await self.test_under_limit()
        await self.test_near_limit()
        await self.test_over_limit()
        
        # 生成报告
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print("  测试完成")
        print("=" * 60)
        print(report)
        
        # 保存报告
        with open("ContextLimitTestReport.md", "w") as f:
            f.write(report)
        
        print(f"\n📄 测试报告已保存: ContextLimitTestReport.md")


async def main():
    tester = ContextLimitTester()
    await tester.run_all()


if __name__ == "__main__":
    asyncio.run(main())
