#!/usr/bin/env python3
"""
快速测试脚本 - 角色模型配置
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from rich.console import Console

console = Console()


async def test_simple_conversation():
    """测试简单对话"""
    console.print("[bold green]💬 测试简单对话...[/bold green]")
    
    try:
        # 这里可以添加实际的对话测试逻辑
        console.print("[yellow]提示: 使用以下命令测试对话[/yellow]")
        console.print("python -m daip_live.cli pa \"你好，我想测试一下角色配置\" --role tech_analyst")
        
    except Exception as e:
        console.print(f"[red]❌ 对话测试失败: {e}[/red]")


def show_available_roles():
    """显示可用角色"""
    console.print("\n[bold blue]🎭 可用角色列表[/bold blue]")
    
    try:
        manager = RoleModelManager("roles")
        roles = manager.list_roles()
        
        for role in roles:
            if hasattr(role, 'model_configs') and len(role.model_configs) > 0:
                primary_config = role.get_primary_model_config()
                console.print(f"  • [cyan]{role.name}[/cyan] - 主模型: {primary_config.model_name}")
                if role.debate_model_config:
                    console.print(f"    辩论模型: {role.debate_model_config.model_name}")
        
    except Exception as e:
        console.print(f"[red]❌ 无法加载角色: {e}[/red]")


def main():
    """主函数"""
    console.print("[bold magenta]🚀 角色模型配置快速测试[/bold magenta]")
    console.print("=" * 50)
    
    # 显示可用角色
    show_available_roles()
    
    # 显示测试命令
    console.print("\n[bold green]🧪 测试命令:[/bold green]")
    
    commands = [
        ("技术分析师对话", "python -m daip_live.cli pa \"帮我分析一下Python代码的优化建议\" --role tech_analyst"),
        ("创意写作师对话", "python -m daip_live.cli pa \"帮我写一首关于AI的诗\" --role creative_writer"),
        ("数据科学家对话", "python -m daip_live.cli pa \"如何分析这个数据集的特征\" --role data_scientist"),
        ("产品经理对话", "python -m daip_live.cli pa \"如何改进这个产品的用户体验\" --role product_manager"),
        ("哲学思辨家对话", "python -m daip_live.cli pa \"什么是意识的本质\" --role philosophy_thinker"),
        ("两角色辩论", "python -m daip_live.cli debate \"技术发展是否让人类更快乐\" --roles tech_analyst,philosophy_thinker --rounds 3"),
        ("多角色辩论", "python -m daip_live.cli debate \"AI时代的就业前景\" --roles tech_analyst,product_manager,data_scientist --rounds 3"),
    ]
    
    for desc, cmd in commands:
        console.print(f"\n[dim]{desc}:[/dim]")
        console.print(f"[dim]  {cmd}[/dim]")
    
    console.print("\n[yellow]💡 提示:[/yellow]")
    console.print("1. 确保Ollama正在运行: ollama serve")
    console.print("2. 确保已安装所需模型，或根据你的模型修改配置文件")
    console.print("3. 从简单对话开始测试，确保模型正常工作")
    console.print("4. 可以在配置文件中调整模型参数以获得最佳效果")


if __name__ == "__main__":
    main()