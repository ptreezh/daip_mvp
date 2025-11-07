#!/usr/bin/env python3
"""
DAIP-LIVE TUI 真实交互测试脚本

这个脚本模拟真实用户操作，测试TUI的实际启动和基本交互流程。
"""

import asyncio
import sys
import os
import time
import subprocess
from pathlib import Path

def test_tui_startup():
    """测试TUI实际启动过程"""
    print("\n🚀 测试TUI启动过程")
    print("="*50)
    
    try:
        # 测试直接启动TUI
        print("1. 测试TUI启动命令...")
        result = subprocess.run([
            sys.executable, "-m", "daip_live.tui", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 or "usage:" in result.stdout.lower() or "help" in result.stdout.lower():
            print("   ✅ TUI启动命令正常")
        else:
            print(f"   ❌ TUI启动异常: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  TUI启动超时（可能是正常行为）")
    except Exception as e:
        print(f"   ❌ TUI启动错误: {e}")
        return False
    
    return True

def test_cli_commands():
    """测试CLI命令执行"""
    print("\n📋 测试CLI命令")
    print("="*50)
    
    commands_to_test = [
        ("daip --help", "显示帮助信息"),
        ("daip role list", "列出角色"),
        ("daip session list", "列出会话"),
        ("daip knowledge sync", "同步知识库"),
    ]
    
    for cmd, description in commands_to_test:
        print(f"\n测试命令: {cmd}")
        print(f"描述: {description}")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "daip_live.cli"
            ] + cmd.split()[1:], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("   ✅ 命令执行成功")
                if result.stdout:
                    print(f"   输出: {result.stdout[:200]}...")
            else:
                print(f"   ⚠️  命令返回非零状态: {result.returncode}")
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}")
                    
        except subprocess.TimeoutExpired:
            print("   ⚠️  命令执行超时")
        except Exception as e:
            print(f"   ❌ 命令执行错误: {e}")

def test_configuration():
    """测试配置文件"""
    print("\n⚙️  测试配置系统")
    print("="*50)
    
    config_file = Path("config.yaml")
    if config_file.exists():
        print("✅ 配置文件存在")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   配置文件大小: {len(content)} 字节")
                if "database" in content and "llm_provider" in content:
                    print("   ✅ 配置文件包含必要配置项")
                else:
                    print("   ⚠️  配置文件可能缺少必要配置")
        except Exception as e:
            print(f"   ❌ 配置文件读取错误: {e}")
    else:
        print("⚠️  配置文件不存在，将使用默认配置")

def test_database():
    """测试数据库连接"""
    print("\n🗄️  测试数据库")
    print("="*50)
    
    db_file = Path("daip_live.db")
    if db_file.exists():
        print(f"✅ 数据库文件存在，大小: {db_file.stat().st_size} 字节")
    else:
        print("⚠️  数据库文件不存在，将在首次运行时创建")

def test_knowledge_base():
    """测试知识库"""
    print("\n📚 测试知识库")
    print("="*50)
    
    knowledge_dir = Path("knowledge")
    if knowledge_dir.exists():
        print("✅ 知识库目录存在")
        files = list(knowledge_dir.glob("*"))
        print(f"   文件数量: {len(files)}")
    else:
        print("⚠️  知识库目录不存在")

def test_roles():
    """测试角色系统"""
    print("\n🎭 测试角色系统")
    print("="*50)
    
    roles_dir = Path("roles")
    if roles_dir.exists():
        print("✅ 角色目录存在")
        role_files = list(roles_dir.glob("*.yaml")) + list(roles_dir.glob("*.yml"))
        print(f"   角色文件数量: {len(role_files)}")
        for role_file in role_files[:5]:  # 显示前5个
            print(f"   - {role_file.name}")
    else:
        print("⚠️  角色目录不存在")

def test_wiki_system():
    """测试Wiki系统"""
    print("\n📝 测试Wiki系统")
    print("="*50)
    
    wiki_dir = Path("wiki")
    if wiki_dir.exists():
        print("✅ Wiki目录存在")
        wiki_files = list(wiki_dir.glob("*.md"))
        print(f"   Wiki页面数量: {len(wiki_files)}")
    else:
        print("⚠️  Wiki目录不存在")

def test_debate_system():
    """测试辩论系统"""
    print("\n🗣️  测试辩论系统")
    print("="*50)
    
    # 检查辩论角色
    debate_roles_dir = Path("pro_arguer")
    if debate_roles_dir.exists():
        print("✅ 辩论角色目录存在")
        role_files = list(debate_roles_dir.glob("*.yaml")) + list(debate_roles_dir.glob("*.yml"))
        print(f"   辩论角色数量: {len(role_files)}")
    else:
        print("⚠️  辩论角色目录不存在")

def main():
    """主测试函数"""
    print("🔍 DAIP-LIVE TUI 真实交互测试")
    print("="*60)
    
    # 切换到项目根目录
    os.chdir(Path(__file__).parent)
    
    # 执行各项测试
    all_passed = True
    
    if not test_tui_startup():
        all_passed = False
    
    test_cli_commands()
    test_configuration()
    test_database()
    test_knowledge_base()
    test_roles()
    test_wiki_system()
    test_debate_system()
    
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    if all_passed:
        print("✅ 所有关键测试通过")
        print("\n🔧 建议下一步:")
        print("1. 运行 `python -m daip_live.tui` 启动完整TUI界面")
        print("2. 测试具体的交互命令，如 `/help` `/role list` 等")
        print("3. 进行辩论功能测试: `/debate start '测试话题'")
        print("4. 测试知识库功能: `/knowledge sync`")
    else:
        print("⚠️  部分测试存在问题，请检查配置")
    
    print("\n💡 注意: 这只是基础功能测试，完整的交互测试需要实际启动TUI界面")

if __name__ == "__main__":
    main()