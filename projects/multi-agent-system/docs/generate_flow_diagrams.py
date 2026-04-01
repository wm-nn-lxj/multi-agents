#!/usr/bin/env python3
"""
生成业务流程图 - 可视化PNG图片
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


def draw_main_flow():
    """绘制主流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # 标题
    ax.text(8, 11.5, 'Task 001 - Multi-Agent System Business Flow', 
            fontsize=20, fontweight='bold', ha='center', va='center')
    
    # 定义颜色
    colors = {
        'user': '#E3F2FD',
        'api': '#FFF3E0', 
        'coord': '#E8F5E9',
        'agent': '#F3E5F5',
        'support': '#FFEBEE',
        'arrow': '#455A64'
    }
    
    # 用户层
    user_box = FancyBboxPatch((0.5, 9), 3, 1.5, boxstyle="round,pad=0.1", 
                               facecolor=colors['user'], edgecolor='#1976D2', linewidth=2)
    ax.add_patch(user_box)
    ax.text(2, 9.75, 'User', fontsize=12, fontweight='bold', ha='center')
    
    # 网页控制台
    wc_box = FancyBboxPatch((4, 9), 3, 1.5, boxstyle="round,pad=0.1",
                            facecolor=colors['user'], edgecolor='#1976D2', linewidth=2)
    ax.add_patch(wc_box)
    ax.text(5.5, 9.75, 'Web Console', fontsize=12, fontweight='bold', ha='center')
    
    # API网关
    api_box = FancyBboxPatch((8, 9), 3, 1.5, boxstyle="round,pad=0.1",
                             facecolor=colors['api'], edgecolor='#F57C00', linewidth=2)
    ax.add_patch(api_box)
    ax.text(9.5, 9.75, 'API Gateway\nFastAPI:9000', fontsize=11, fontweight='bold', ha='center')
    
    # WebSocket
    ws_box = FancyBboxPatch((12, 9), 3, 1.5, boxstyle="round,pad=0.1",
                            facecolor=colors['api'], edgecolor='#F57C00', linewidth=2)
    ax.add_patch(ws_box)
    ax.text(13.5, 9.75, 'WebSocket\nReal-time', fontsize=11, fontweight='bold', ha='center')
    
    # Product Agent (协调者)
    pa_box = FancyBboxPatch((6, 6), 4, 2, boxstyle="round,pad=0.1",
                            facecolor=colors['coord'], edgecolor='#388E3C', linewidth=3)
    ax.add_patch(pa_box)
    ax.text(8, 7, 'Product Agent', fontsize=14, fontweight='bold', ha='center')
    ax.text(8, 6.5, 'Coordinator', fontsize=11, ha='center')
    ax.text(8, 6.1, 'Task Decomposition', fontsize=10, ha='center', style='italic')
    
    # 四个专业Agent
    agents = [
        ('Architect\nAgent', 1.5, 3, '#2196F3'),
        ('Developer\nAgent', 5, 3, '#4CAF50'),
        ('Reviewer\nAgent', 8.5, 3, '#F44336'),
        ('Tester\nAgent', 12, 3, '#9C27B0')
    ]
    
    for name, x, y, color in agents:
        box = FancyBboxPatch((x, y), 3, 2, boxstyle="round,pad=0.1",
                             facecolor=colors['agent'], edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x+1.5, y+1, name, fontsize=12, fontweight='bold', ha='center', va='center')
    
    # 支撑层
    support_boxes = [
        ('Context\n198K tokens', 2, 0.5),
        ('Memory\nRedis+Chroma', 6.5, 0.5),
        ('LLM\nGLM5/GPT-4', 11, 0.5)
    ]
    
    for name, x, y in support_boxes:
        box = FancyBboxPatch((x, y), 3, 1.2, boxstyle="round,pad=0.1",
                             facecolor=colors['support'], edgecolor='#D32F2F', linewidth=2)
        ax.add_patch(box)
        ax.text(x+1.5, y+0.6, name, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # 绘制箭头
    arrow_style = dict(arrowstyle='->', color=colors['arrow'], lw=2, 
                       connectionstyle='arc3,rad=0.1')
    
    # 用户 -> 控制台
    ax.annotate('', xy=(4, 9.75), xytext=(3.5, 9.75), arrowprops=arrow_style)
    # 控制台 <-> WebSocket
    ax.annotate('', xy=(12, 9.75), xytext=(7, 9.75), arrowprops=arrow_style)
    # WebSocket -> API
    ax.annotate('', xy=(11, 9.75), xytext=(12, 9.75), arrowprops=dict(arrowstyle='<->', color=colors['arrow'], lw=2))
    # API -> Product Agent
    ax.annotate('', xy=(8, 8), xytext=(9.5, 9), arrowprops=arrow_style)
    # Product Agent -> 四个Agent
    for x in [3, 6.5, 10, 13.5]:
        ax.annotate('', xy=(x, 5), xytext=(8, 6), arrowprops=arrow_style)
    # 四个Agent -> 支撑层
    ax.annotate('', xy=(3.5, 1.7), xytext=(3, 3), arrowprops=dict(arrowstyle='<->', color=colors['arrow'], lw=1.5))
    ax.annotate('', xy=(8, 1.7), xytext=(6.5, 3), arrowprops=dict(arrowstyle='<->', color=colors['arrow'], lw=1.5))
    ax.annotate('', xy=(12.5, 1.7), xytext=(13.5, 3), arrowprops=dict(arrowstyle='<->', color=colors['arrow'], lw=1.5))
    
    plt.tight_layout()
    plt.savefig('/home/sandbox/.openclaw/workspace/projects/multi-agent-system/docs/flow_main.png', 
                dpi=150, bbox_inches='tight', facecolor='white')
    print("✅ 主流程图已生成: docs/flow_main.png")


def draw_development_flow():
    """绘制开发流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 标题
    ax.text(7, 9.5, 'Multi-Agent Development Workflow', 
            fontsize=18, fontweight='bold', ha='center')
    
    # 阶段框
    stages = [
        ('1. Requirement', 0.5, 7, '#E3F2FD', '#1976D2'),
        ('2. Architecture', 0.5, 5, '#E8F5E9', '#388E3C'),
        ('3. Development', 0.5, 3, '#FFF3E0', '#F57C00'),
        ('4. Review', 0.5, 1, '#FCE4EC', '#C2185B'),
    ]
    
    for name, x, y, fc, ec in stages:
        box = FancyBboxPatch((x, y), 3, 1.5, boxstyle="round,pad=0.1",
                             facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(box)
        ax.text(x+1.5, y+0.75, name, fontsize=11, fontweight='bold', ha='center', va='center')
    
    # Agent框
    agents = [
        ('Product\nAgent', 5, 7, '#E8F5E9', '#388E3C'),
        ('Architect\nAgent', 5, 5, '#E3F2FD', '#1976D2'),
        ('Developer\nAgent', 5, 3, '#FFF3E0', '#F57C00'),
        ('Reviewer\nAgent', 5, 1, '#FCE4EC', '#C2185B'),
    ]
    
    for name, x, y, fc, ec in agents:
        box = FancyBboxPatch((x, y), 2.5, 1.5, boxstyle="round,pad=0.1",
                             facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(box)
        ax.text(x+1.25, y+0.75, name, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # 输出框
    outputs = [
        ('PRD\nDocument', 9, 7, '#E3F2FD', '#1976D2'),
        ('Architecture\nDesign', 9, 5, '#E8F5E9', '#388E3C'),
        ('Source\nCode', 9, 3, '#FFF3E0', '#F57C00'),
        ('Review\nReport', 9, 1, '#FCE4EC', '#C2185B'),
    ]
    
    for name, x, y, fc, ec in outputs:
        box = FancyBboxPatch((x, y), 2.5, 1.5, boxstyle="round,pad=0.1",
                             facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(box)
        ax.text(x+1.25, y+0.75, name, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # 测试阶段
    test_box = FancyBboxPatch((12, 3), 1.5, 3, boxstyle="round,pad=0.1",
                              facecolor='#F3E5F5', edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(test_box)
    ax.text(12.75, 4.5, 'Tester\nAgent', fontsize=10, fontweight='bold', ha='center', va='center')
    
    # 最终交付
    final_box = FancyBboxPatch((12, 7), 1.5, 1.5, boxstyle="round,pad=0.1",
                               facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=3)
    ax.add_patch(final_box)
    ax.text(12.75, 7.75, 'Delivery\nComplete', fontsize=10, fontweight='bold', ha='center', va='center')
    
    # 箭头
    arrow_style = dict(arrowstyle='->', color='#455A64', lw=2)
    
    # 阶段 -> Agent
    for y in [7.75, 5.75, 3.75, 1.75]:
        ax.annotate('', xy=(5, y), xytext=(3.5, y), arrowprops=arrow_style)
    
    # Agent -> 输出
    for y in [7.75, 5.75, 3.75, 1.75]:
        ax.annotate('', xy=(9, y), xytext=(7.5, y), arrowprops=arrow_style)
    
    # 输出 -> 下一阶段
    ax.annotate('', xy=(0.5, 5.75), xytext=(9, 7), 
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2, connectionstyle='arc3,rad=-0.3'))
    ax.annotate('', xy=(0.5, 3.75), xytext=(9, 5),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2, connectionstyle='arc3,rad=-0.3'))
    ax.annotate('', xy=(0.5, 1.75), xytext=(9, 3),
                arrowprops=dict(arrowstyle='->', color='#455A64', lw=2, connectionstyle='arc3,rad=-0.3'))
    
    # 到测试
    ax.annotate('', xy=(12, 4.5), xytext=(11.5, 3.75), arrowprops=arrow_style)
    
    # 到交付
    ax.annotate('', xy=(12, 7.75), xytext=(12.75, 6), arrowprops=arrow_style)
    
    plt.tight_layout()
    plt.savefig('/home/sandbox/.openclaw/workspace/projects/multi-agent-system/docs/flow_development.png',
                dpi=150, bbox_inches='tight', facecolor='white')
    print("✅ 开发流程图已生成: docs/flow_development.png")


def draw_context_flow():
    """绘制上下文管理流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # 标题
    ax.text(6, 7.5, 'Context Management Flow (198K tokens)', 
            fontsize=16, fontweight='bold', ha='center')
    
    # 分层框
    layers = [
        ('Global Layer\n10K tokens', 1, 5, '#E3F2FD', '#1976D2'),
        ('Session Layer\n100K tokens', 1, 3.5, '#E8F5E9', '#388E3C'),
        ('Task Layer\n50K tokens', 1, 2, '#FFF3E0', '#F57C00'),
        ('Memory Layer\n38K tokens', 1, 0.5, '#F3E5F5', '#7B1FA2'),
    ]
    
    for name, x, y, fc, ec in layers:
        box = FancyBboxPatch((x, y), 3, 1.2, boxstyle="round,pad=0.1",
                             facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(box)
        ax.text(x+1.5, y+0.6, name, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # 管理框
    mgmt = [
        ('Token\nEstimation', 5.5, 5, '#FFEBEE', '#D32F2F'),
        ('Limit\nCheck', 5.5, 3.5, '#FFEBEE', '#D32F2F'),
        ('Auto\nCompression', 5.5, 2, '#FFEBEE', '#D32F2F'),
        ('Summary\nGeneration', 5.5, 0.5, '#FFEBEE', '#D32F2F'),
    ]
    
    for name, x, y, fc, ec in mgmt:
        box = FancyBboxPatch((x, y), 2, 1.2, boxstyle="round,pad=0.1",
                             facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(box)
        ax.text(x+1, y+0.6, name, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # 输出框
    output_box = FancyBboxPatch((9, 2.5), 2.5, 2, boxstyle="round,pad=0.1",
                                facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=3)
    ax.add_patch(output_box)
    ax.text(10.25, 3.5, 'Combined\nContext\n<198K', fontsize=11, fontweight='bold', ha='center', va='center')
    
    # LLM框
    llm_box = FancyBboxPatch((9, 0.5), 2.5, 1.5, boxstyle="round,pad=0.1",
                             facecolor='#E1F5FE', edgecolor='#0288D1', linewidth=2)
    ax.add_patch(llm_box)
    ax.text(10.25, 1.25, 'Send to\nLLM', fontsize=11, fontweight='bold', ha='center', va='center')
    
    # 箭头
    arrow_style = dict(arrowstyle='->', color='#455A64', lw=2)
    
    # 层 -> 管理
    for y in [5.6, 4.1, 2.6, 1.1]:
        ax.annotate('', xy=(5.5, y), xytext=(4, y), arrowprops=arrow_style)
    
    # 管理 -> 输出
    ax.annotate('', xy=(9, 3.5), xytext=(7.5, 3.5), arrowprops=arrow_style)
    
    # 输出 -> LLM
    ax.annotate('', xy=(10.25, 2), xytext=(10.25, 2.5), arrowprops=arrow_style)
    
    # 循环箭头 (压缩)
    ax.annotate('', xy=(5.5, 2.6), xytext=(5.5, 3.5),
                arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=2, connectionstyle='arc3,rad=1'))
    ax.text(6.2, 3, 'Exceeds\nLimit', fontsize=8, color='#D32F2F', ha='center')
    
    plt.tight_layout()
    plt.savefig('/home/sandbox/.openclaw/workspace/projects/multi-agent-system/docs/flow_context.png',
                dpi=150, bbox_inches='tight', facecolor='white')
    print("✅ 上下文流程图已生成: docs/flow_context.png")


if __name__ == "__main__":
    print("Generating business flow diagrams...")
    draw_main_flow()
    draw_development_flow()
    draw_context_flow()
    print("\n✅ All diagrams generated successfully!")
