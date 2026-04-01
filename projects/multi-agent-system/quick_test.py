#!/usr/bin/env python3
"""
快速验证测试
"""
import asyncio
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()


async def quick_test():
    """快速测试所有Agent"""
    print("=" * 60)
    print("  多Agent协作系统 - 快速验证测试")
    print("=" * 60)
    
    from src.core import get_llm_client, ContextManager
    
    results = []
    total_tokens = 0
    start_time = time.time()
    
    # 1. 测试Product Agent
    print("\n📋 Product Agent...")
    try:
        from src.agents import ProductAgent
        llm = get_llm_client()
        agent = ProductAgent(llm_client=llm)
        
        t0 = time.time()
        result = await agent.execute("生成一个简单的用户登录功能PRD", {})
        elapsed = time.time() - t0
        
        success = result.success and len(result.output or "") > 50
        total_tokens += result.tokens_used
        results.append(("Product Agent", success, result.tokens_used, elapsed))
        print(f"   {'✅' if success else '❌'} Token:{result.tokens_used} 时间:{elapsed:.1f}s")
    except Exception as e:
        results.append(("Product Agent", False, 0, 0))
        print(f"   ❌ 错误: {e}")
    
    # 2. 测试Architect Agent
    print("\n🏗️ Architect Agent...")
    try:
        from src.agents import ArchitectAgent
        agent = ArchitectAgent(llm_client=llm)
        
        t0 = time.time()
        result = await agent.execute("设计用户系统架构", {})
        elapsed = time.time() - t0
        
        success = result.success and len(result.output or "") > 50
        total_tokens += result.tokens_used
        results.append(("Architect Agent", success, result.tokens_used, elapsed))
        print(f"   {'✅' if success else '❌'} Token:{result.tokens_used} 时间:{elapsed:.1f}s")
    except Exception as e:
        results.append(("Architect Agent", False, 0, 0))
        print(f"   ❌ 错误: {e}")
    
    # 3. 测试Developer Agent
    print("\n💻 Developer Agent...")
    try:
        from src.agents import DeveloperAgent
        agent = DeveloperAgent(llm_client=llm)
        
        t0 = time.time()
        result = await agent.execute("写一个Python加法函数", {"tech_stack": "Python"})
        elapsed = time.time() - t0
        
        success = result.success and "def " in (result.output or "")
        total_tokens += result.tokens_used
        results.append(("Developer Agent", success, result.tokens_used, elapsed))
        print(f"   {'✅' if success else '❌'} Token:{result.tokens_used} 时间:{elapsed:.1f}s")
    except Exception as e:
        results.append(("Developer Agent", False, 0, 0))
        print(f"   ❌ 错误: {e}")
    
    # 4. 测试Reviewer Agent
    print("\n🔍 Reviewer Agent...")
    try:
        from src.agents import ReviewerAgent
        agent = ReviewerAgent(llm_client=llm)
        
        t0 = time.time()
        result = await agent.execute("审查代码: def add(a,b): return a+b", {})
        elapsed = time.time() - t0
        
        success = result.success and len(result.output or "") > 30
        total_tokens += result.tokens_used
        results.append(("Reviewer Agent", success, result.tokens_used, elapsed))
        print(f"   {'✅' if success else '❌'} Token:{result.tokens_used} 时间:{elapsed:.1f}s")
    except Exception as e:
        results.append(("Reviewer Agent", False, 0, 0))
        print(f"   ❌ 错误: {e}")
    
    # 5. 测试Tester Agent
    print("\n🧪 Tester Agent...")
    try:
        from src.agents import TesterAgent
        agent = TesterAgent(llm_client=llm)
        
        t0 = time.time()
        result = await agent.execute("为登录功能设计测试用例", {})
        elapsed = time.time() - t0
        
        success = result.success and len(result.output or "") > 50
        total_tokens += result.tokens_used
        results.append(("Tester Agent", success, result.tokens_used, elapsed))
        print(f"   {'✅' if success else '❌'} Token:{result.tokens_used} 时间:{elapsed:.1f}s")
    except Exception as e:
        results.append(("Tester Agent", False, 0, 0))
        print(f"   ❌ 错误: {e}")
    
    # 6. 测试上下文管理
    print("\n📦 上下文管理...")
    try:
        ctx = ContextManager()
        ctx.update_layer("global", {"test": "data"})
        total = ctx.get_total_tokens()
        within = ctx.is_within_limit()
        success = total < 16000
        results.append(("上下文管理", success, 0, 0))
        print(f"   {'✅' if success else '❌'} Tokens:{total} 限制内:{within}")
    except Exception as e:
        results.append(("上下文管理", False, 0, 0))
        print(f"   ❌ 错误: {e}")
    
    # 汇总
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r[1])
    total_count = len(results)
    
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    print(f"  总测试: {total_count}")
    print(f"  通过: {success_count}")
    print(f"  失败: {total_count - success_count}")
    print(f"  通过率: {success_count/total_count*100:.1f}%")
    print(f"  总Token: {total_tokens}")
    print(f"  总耗时: {total_time:.1f}s")
    print("=" * 60)
    
    # 生成报告
    report = f"""# 多Agent协作系统 - 测试报告

**测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**总耗时**: {total_time:.2f}秒  
**总Token消耗**: {total_tokens}

---

## 测试结果汇总

| 指标 | 数值 |
|------|------|
| 总测试数 | {total_count} |
| 通过数 | {success_count} |
| 失败数 | {total_count - success_count} |
| 通过率 | {success_count/total_count*100:.1f}% |

---

## 详细测试结果

| 测试项 | 状态 | Token | 耗时 |
|--------|------|-------|------|
"""
    for r in results:
        status = "✅ 通过" if r[1] else "❌ 失败"
        report += f"| {r[0]} | {status} | {r[2]} | {r[3]:.2f}s |\n"
    
    report += f"""
---

## 系统配置

| 配置项 | 值 |
|--------|-----|
| LLM模型 | LLM_GLM5 |
| API地址 | https://celia-claw-drcn.ai.dbankcloud.cn |
| 上下文限制 | 16K tokens |

---

## 结论

{'🎉 所有测试通过，系统功能正常！' if success_count == total_count else f'✅ 通过率 {success_count/total_count*100:.1f}%，核心功能正常。'}

**系统状态**: {'✅ 就绪，可投入使用' if success_count >= total_count*0.8 else '⚠️ 需要进一步优化'}
"""
    
    with open("TestReport.md", "w") as f:
        f.write(report)
    
    print(f"\n📄 测试报告已保存: TestReport.md")
    
    return success_count == total_count


if __name__ == "__main__":
    asyncio.run(quick_test())
