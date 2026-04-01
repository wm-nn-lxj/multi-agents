#!/usr/bin/env python3
"""
完整系统测试 - 功能、性能、稳定性测试
"""
import asyncio
import sys
import os
import time
from datetime import datetime

# 添加src到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = []
        self.total_tokens = 0
        self.start_time = None
    
    def record(self, name: str, success: bool, tokens: int, time_sec: float, details: str = ""):
        """记录测试结果"""
        self.results.append({
            "name": name,
            "success": success,
            "tokens": tokens,
            "time": time_sec,
            "details": details
        })
        self.total_tokens += tokens
    
    async def test_product_agent_prd(self):
        """测试Product Agent PRD生成"""
        from src.agents import ProductAgent
        from src.core import get_llm_client
        
        print("\n📋 测试: Product Agent - PRD生成")
        
        try:
            llm = get_llm_client()
            agent = ProductAgent(llm_client=llm)
            
            start = time.time()
            result = await agent.execute(
                "生成一个用户登录功能的PRD文档",
                {"project": "测试项目"}
            )
            elapsed = time.time() - start
            
            success = result.success and len(result.output or "") > 100
            self.record("Product Agent - PRD生成", success, result.tokens_used, elapsed,
                       result.output[:100] if result.output else "无输出")
            
            print(f"   {'✅ 通过' if success else '❌ 失败'}")
            print(f"   Token: {result.tokens_used}, 时间: {elapsed:.2f}s")
            return success
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.record("Product Agent - PRD生成", False, 0, 0, str(e))
            return False
    
    async def test_architect_agent(self):
        """测试Architect Agent"""
        from src.agents import ArchitectAgent
        from src.core import get_llm_client
        
        print("\n🏗️ 测试: Architect Agent - 架构设计")
        
        try:
            llm = get_llm_client()
            agent = ArchitectAgent(llm_client=llm)
            
            start = time.time()
            result = await agent.execute(
                "设计一个微服务架构的用户系统",
                {}
            )
            elapsed = time.time() - start
            
            success = result.success and len(result.output or "") > 100
            self.record("Architect Agent - 架构设计", success, result.tokens_used, elapsed,
                       result.output[:100] if result.output else "无输出")
            
            print(f"   {'✅ 通过' if success else '❌ 失败'}")
            print(f"   Token: {result.tokens_used}, 时间: {elapsed:.2f}s")
            return success
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.record("Architect Agent - 架构设计", False, 0, 0, str(e))
            return False
    
    async def test_developer_agent(self):
        """测试Developer Agent"""
        from src.agents import DeveloperAgent
        from src.core import get_llm_client
        
        print("\n💻 测试: Developer Agent - 代码生成")
        
        try:
            llm = get_llm_client()
            agent = DeveloperAgent(llm_client=llm)
            
            start = time.time()
            result = await agent.execute(
                "实现一个Python快速排序函数",
                {"tech_stack": "Python"}
            )
            elapsed = time.time() - start
            
            success = result.success and "def " in (result.output or "")
            self.record("Developer Agent - 代码生成", success, result.tokens_used, elapsed,
                       result.output[:100] if result.output else "无输出")
            
            print(f"   {'✅ 通过' if success else '❌ 失败'}")
            print(f"   Token: {result.tokens_used}, 时间: {elapsed:.2f}s")
            return success
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.record("Developer Agent - 代码生成", False, 0, 0, str(e))
            return False
    
    async def test_reviewer_agent(self):
        """测试Reviewer Agent"""
        from src.agents import ReviewerAgent
        from src.core import get_llm_client
        
        print("\n🔍 测试: Reviewer Agent - 代码审查")
        
        test_code = """
def add(a, b):
    return a + b
"""
        
        try:
            llm = get_llm_client()
            agent = ReviewerAgent(llm_client=llm)
            
            start = time.time()
            result = await agent.execute(
                f"审查以下代码:\n{test_code}",
                {}
            )
            elapsed = time.time() - start
            
            success = result.success and len(result.output or "") > 50
            self.record("Reviewer Agent - 代码审查", success, result.tokens_used, elapsed,
                       result.output[:100] if result.output else "无输出")
            
            print(f"   {'✅ 通过' if success else '❌ 失败'}")
            print(f"   Token: {result.tokens_used}, 时间: {elapsed:.2f}s")
            return success
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.record("Reviewer Agent - 代码审查", False, 0, 0, str(e))
            return False
    
    async def test_tester_agent(self):
        """测试Tester Agent"""
        from src.agents import TesterAgent
        from src.core import get_llm_client
        
        print("\n🧪 测试: Tester Agent - 测试用例生成")
        
        try:
            llm = get_llm_client()
            agent = TesterAgent(llm_client=llm)
            
            start = time.time()
            result = await agent.execute(
                "为用户登录功能设计测试用例",
                {}
            )
            elapsed = time.time() - start
            
            success = result.success and len(result.output or "") > 100
            self.record("Tester Agent - 测试用例生成", success, result.tokens_used, elapsed,
                       result.output[:100] if result.output else "无输出")
            
            print(f"   {'✅ 通过' if success else '❌ 失败'}")
            print(f"   Token: {result.tokens_used}, 时间: {elapsed:.2f}s")
            return success
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.record("Tester Agent - 测试用例生成", False, 0, 0, str(e))
            return False
    
    async def test_context_management(self):
        """测试上下文管理"""
        from src.core import ContextManager
        
        print("\n📦 测试: 上下文管理")
        
        try:
            ctx = ContextManager()
            
            # 测试分层
            ctx.update_layer("global", {"system_prompt": "test"})
            ctx.update_layer("session", {"history": ["msg1", "msg2"]})
            
            # 检查限制
            total = ctx.get_total_tokens()
            within = ctx.is_within_limit()
            
            success = total < 16000 and within
            self.record("上下文管理", success, 0, 0, f"Total tokens: {total}")
            
            print(f"   {'✅ 通过' if success else '❌ 失败'}")
            print(f"   上下文大小: {total} tokens")
            return success
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.record("上下文管理", False, 0, 0, str(e))
            return False
    
    async def test_performance(self):
        """测试性能"""
        from src.agents import DeveloperAgent
        from src.core import get_llm_client
        
        print("\n⚡ 测试: 性能测试")
        
        try:
            llm = get_llm_client()
            agent = DeveloperAgent(llm_client=llm)
            
            times = []
            for i in range(3):
                start = time.time()
                result = await agent.execute(f"写一个函数，返回数字{i}", {})
                times.append(time.time() - start)
            
            avg_time = sum(times) / len(times)
            success = avg_time < 30  # 平均响应时间小于30秒
            
            self.record("性能测试", success, 0, avg_time, f"平均响应: {avg_time:.2f}s")
            
            print(f"   {'✅ 通过' if success else '❌ 失败'}")
            print(f"   平均响应时间: {avg_time:.2f}s")
            return success
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            self.record("性能测试", False, 0, 0, str(e))
            return False
    
    def generate_report(self) -> str:
        """生成测试报告"""
        total_time = time.time() - self.start_time
        success_count = sum(1 for r in self.results if r["success"])
        total_count = len(self.results)
        success_rate = success_count / total_count * 100 if total_count > 0 else 0
        
        report = f"""
# 多Agent协作系统 - 测试报告

**测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**总耗时**: {total_time:.2f}秒  
**总Token消耗**: {self.total_tokens}

---

## 测试结果汇总

| 指标 | 数值 |
|------|------|
| 总测试数 | {total_count} |
| 通过数 | {success_count} |
| 失败数 | {total_count - success_count} |
| 通过率 | {success_rate:.1f}% |

---

## 详细测试结果

| 测试项 | 状态 | Token | 耗时 |
|--------|------|-------|------|
"""
        for r in self.results:
            status = "✅ 通过" if r["success"] else "❌ 失败"
            report += f"| {r['name']} | {status} | {r['tokens']} | {r['time']:.2f}s |\n"
        
        report += f"""
---

## 结论

{'🎉 所有测试通过，系统功能正常！' if success_rate == 100 else f'⚠️ 通过率 {success_rate:.1f}%，部分测试未通过。'}

**系统状态**: {'✅ 就绪' if success_rate >= 80 else '❌ 需要修复'}
"""
        
        return report
    
    async def run_all(self):
        """运行所有测试"""
        self.start_time = time.time()
        
        print("=" * 60)
        print("  多Agent协作系统 - 完整测试")
        print("=" * 60)
        
        # 功能测试
        await self.test_product_agent_prd()
        await self.test_architect_agent()
        await self.test_developer_agent()
        await self.test_reviewer_agent()
        await self.test_tester_agent()
        
        # 系统测试
        await self.test_context_management()
        
        # 性能测试
        await self.test_performance()
        
        # 生成报告
        print("\n" + "=" * 60)
        print("  测试完成")
        print("=" * 60)
        
        report = self.generate_report()
        print(report)
        
        # 保存报告
        with open("TestReport.md", "w") as f:
            f.write(report)
        
        print(f"\n📄 测试报告已保存: TestReport.md")
        
        return all(r["success"] for r in self.results)


async def main():
    runner = TestRunner()
    success = await runner.run_all()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
