#!/usr/bin/env python3
"""
角色模型配置测试工具

用于测试和验证本地模型角色配置的正确性。
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.model_provider.provider import LiteLLMProvider
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def test_role_configurations():
    """测试角色配置加载和验证"""
    console.print("[bold blue]🔍 测试角色模型配置...[/bold blue]")
    
    try:
        # 初始化角色模型管理器
        roles_dir = Path("roles")
        if not roles_dir.exists():
            console.print("[bold red]❌ roles 目录不存在[/bold red]")
            return False
        
        manager = RoleModelManager(str(roles_dir))
        roles = manager.list_roles()
        
        if not roles:
            console.print("[bold red]❌ 没有找到角色配置文件[/bold red]")
            return False
        
        console.print(f"[green]✅ 成功加载 {len(roles)} 个角色配置[/green]")
        
        # 显示角色配置详情
        for role in roles:
            console.print(f"\n[bold cyan]📋 角色: {role.name}[/bold cyan]")
            console.print(f"   📝 角色描述: {role.persona[:80]}...")
            console.print(f"   🔧 工具: {', '.join(role.tools)}")
            
            # 显示模型配置
            console.print("   🤖 模型配置:")
            for i, config in enumerate(role.model_configs, 1):
                primary_mark = "🌟" if config.is_primary else ""
                console.print(f"     {i}. {config.model_name} ({config.provider}) {primary_mark}")
                console.print(f"        Temperature: {config.temperature}, Max tokens: {config.max_tokens}")
            
            # 显示辩论配置
            if role.debate_model_config:
                console.print("   ⚔️  辩论专用配置:")
                debate_config = role.debate_model_config
                console.print(f"     {debate_config.model_name} ({debate_config.provider})")
                console.print(f"        Temperature: {debate_config.temperature}, Max tokens: {debate_config.max_tokens}")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ 测试失败: {str(e)}[/bold red]")
        return False


def test_debate_model_summary():
    """测试辩论模型映射"""
    console.print("\n[bold blue]⚔️  测试辩论模型映射...[/bold blue]")
    
    try:
        manager = RoleModelManager("roles")
        roles = manager.list_roles()
        role_names = [role.name for role in roles]
        
        # 获取辩论模型映射
        mappings = manager.get_debate_model_mappings(role_names)
        
        if not mappings:
            console.print("[bold red]❌ 无法生成辩论模型映射[/bold red]")
            return False
        
        # 创建表格显示映射关系
        table = Table(title="辩论角色-模型映射", box=box.ROUNDED)
        table.add_column("角色", style="cyan", no_wrap=True)
        table.add_column("模型", style="green")
        table.add_column("提供者", style="yellow")
        table.add_column("温度", style="magenta")
        table.add_column("最大令牌", style="blue")
        
        for mapping in mappings:
            config = mapping.role_model_config
            table.add_row(
                mapping.role_name,
                config.model_name,
                config.provider,
                f"{config.temperature:.1f}",
                str(config.max_tokens)
            )
        
        console.print(table)
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ 测试失败: {str(e)}[/bold red]")
        return False


def test_model_availability():
    """测试模型可用性（需要Ollama运行）"""
    console.print("\n[bold blue]🔧 测试模型可用性...[/bold blue]")
    
    try:
        manager = RoleModelManager("roles")
        roles = manager.list_roles()
        
        # 获取所有模型名称
        all_models = set()
        for role in roles:
            for config in role.model_configs:
                all_models.add(config.model_name)
            if role.debate_model_config:
                all_models.add(role.debate_model_config.model_name)
        
        console.print(f"📦 发现 {len(all_models)} 个不同的模型配置:")
        for model in sorted(all_models):
            console.print(f"   • {model}")
        
        console.print("\n[yellow]💡 提示: 请确保Ollama正在运行，并且已经拉取了所需的模型[/yellow]")
        console.print("[yellow]   可以使用 'ollama pull <model_name>' 来拉取模型[/yellow]")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ 测试失败: {str(e)}[/bold red]")
        return False


def generate_test_commands():
    """生成测试命令示例"""
    console.print("\n[bold blue]📝 测试命令示例[/bold blue]")
    
    commands = [
        {
            "description": "测试默认对话模式",
            "command": "python -m daip_live.cli pa \"你好，我想了解一下AI技术的发展趋势\""
        },
        {
            "description": "测试指定角色的对话",
            "command": "python -m daip_live.cli pa \"帮我分析一下这个Python代码的性能问题\" --role tech_analyst"
        },
        {
            "description": "测试两个角色的辩论",
            "command": "python -m daip_live.cli debate \"人工智能是否会取代人类工作\" --roles tech_analyst,creative_writer --rounds 3"
        },
        {
            "description": "测试多角色辩论",
            "command": "python -m daip_live.cli debate \"技术发展对社会的影响\" --roles tech_analyst,product_manager,philosophy_thinker --rounds 3"
        },
        {
            "description": "启动TUI界面进行交互测试",
            "command": "python -m daip_live.cli run \"测试多模型角色配置\""
        }
    ]
    
    for cmd in commands:
        console.print(f"\n[bold green]{cmd['description']}:[/bold green]")
        console.print(f"[dim]{cmd['command']}[/dim]")


def main():
    """主测试函数"""
    console.print("[bold magenta]🚀 角色模型配置测试工具[/bold magenta]")
    console.print("=" * 60)
    
    # 运行测试
    tests = [
        ("角色配置加载", test_role_configurations),
        ("辩论模型映射", test_debate_model_summary),
        ("模型可用性", test_model_availability),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[bold red]❌ {test_name} 异常: {str(e)}[/bold red]")
            results.append((test_name, False))
    
    # 显示测试结果
    console.print("\n[bold blue]📊 测试结果总结[/bold blue]")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        color = "green" if result else "red"
        console.print(f"  [{color}]{status}[/] {test_name}")
    
    # 生成测试命令
    generate_test_commands()
    
    # 使用建议
    console.print("\n[bold yellow]💡 使用建议:[/bold yellow]")
    console.print("1. 确保Ollama服务正在运行: ollama serve")
    console.print("2. 拉取所需模型: ollama pull qwen-72b-chat")
    console.print("3. 根据你的实际模型修改配置文件中的模型名称")
    console.print("4. 先从简单的对话测试开始，再尝试复杂辩论")
    
    console.print("\n[bold green]🎉 测试完成！[/bold green]")


if __name__ == "__main__":
    main()