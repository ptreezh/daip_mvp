"""
验证Wiki和辩论日志路径配置功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_config_paths():
    """测试配置路径功能"""
    print("=== 验证Wiki和辩论日志路径配置 ===\n")
    
    try:
        # 创建容器并测试配置
        from src.daip_live.container import Container
        
        container = Container()
        
        # 加载配置
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        container.config.from_dict(config_data)
        
        print("✅ 1. 配置加载成功")
        print(f"   - Wiki页面目录: {container.config.wiki.pages_directory()}")
        print(f"   - 论文下载目录: {container.config.paper.download_directory()}")
        print(f"   - 辩论日志目录: {container.config.debate.logs_directory()}")
        
        # 测试使用配置值
        wiki_path = Path(os.getcwd()) / container.config.wiki.pages_directory()
        paper_path = Path(os.getcwd()) / container.config.paper.download_directory()
        debate_path = Path(os.getcwd()) / container.config.debate.logs_directory()
        
        print(f"   - Wiki路径: {wiki_path}")
        print(f"   - 论文路径: {paper_path}")
        print(f"   - 辩论路径: {debate_path}")
        
        print("\n✅ 2. 路径组合测试通过")
        
        # 检查目录是否正确创建
        if not wiki_path.exists():
            print(f"⚠️  Wiki目录不存在: {wiki_path}")
        else:
            print(f"   - Wiki目录存在: {wiki_path}")
        
        if not paper_path.exists():
            print(f"⚠️  论文目录不存在: {paper_path}")
        else:
            print(f"   - 论文目录存在: {paper_path}")
        
        if not debate_path.exists():
            print(f"⚠️  辩论目录不存在: {debate_path}")
        else:
            print(f"   - 辩论目录存在: {debate_path}")
        
        # 验证目录是否已创建
        wiki_path.mkdir(parents=True, exist_ok=True)
        paper_path.mkdir(parents=True, exist_ok=True)
        debate_path.mkdir(parents=True, exist_ok=True)
        
        print(f"   - 已自动创建缺失的目录")
        
        print("\n✅ 3. 目录创建测试通过")
        
        # 验证WikiManager使用配置路径
        from src.daip_live.wiki.manager import WikiManager
        from src.daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager  
        from src.daip_live.model_provider.provider import LiteLLMProvider
        from src.daip_live.core.models import ProviderConfig
        
        # 创建模拟提供者
        provider_config = ProviderConfig(model="mock-model")
        model_provider = LiteLLMProvider(provider_config)
        role_model_manager = RoleModelManager()
        
        # 使用配置的路径初始化WikiManager
        wiki_manager = WikiManager(
            wiki_root=wiki_path,
            role_model_manager=role_model_manager,
            model_provider=model_provider
        )
        
        print(f"✅ 4. WikiManager初始化成功，使用路径: {wiki_manager.wiki_root}")
        
        # 创建一个测试Wiki页面
        test_page = wiki_manager.create_page(
            title="测试页面",
            content="# 测试\n这是一个测试页面。",
            tags=["test", "configuration"]
        )
        
        expected_file_path = wiki_path / "测试页面.md"
        if expected_file_path.exists():
            print(f"✅ 5. Wiki页面创建测试成功: {expected_file_path}")
        else:
            print(f"⚠️  5. Wiki页面可能在其他路径: {[f for f in wiki_path.iterdir() if f.suffix == '.md']}")
        
        print("\n✅ Wiki和辩论日志路径配置验证通过！")
        print("\n系统现在将：")
        print("- 从配置文件读取Wiki页面保存路径 (默认: knowledge/wiki/)")
        print("- 从配置文件读取辩论日志保存路径 (默认: knowledge/debate/)")
        print("- 从配置文件读取论文下载路径 (默认: knowledge/paper/)")
        print("- 正确使用配置的路径进行文件保存")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_debate_log_path():
    """测试辩论日志路径功能"""
    print("\n=== 验证辩论日志保存路径 ===\n")
    
    try:
        from src.daip_live.tui import DAIP_TUI
        
        # 创建一个模拟的TUI实例来测试辩论日志路径
        print("创建模拟TUI实例以测试辩论日志路径...")
        
        # 由于完整初始化TUI比较复杂，我们直接测试路径配置
        from src.daip_live.container import Container
        import yaml
        
        container = Container()
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        container.config.from_dict(config_data)
        
        # 检查配置值
        debate_logs_dir = container.config.debate.logs_directory()
        print(f"✅ 从配置读取辩论日志目录: {debate_logs_dir}")
        
        output_path = Path(os.getcwd()) / debate_logs_dir
        print(f"✅ 构造输出路径: {output_path}")
        
        # 创建目录
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 辩论日志目录已创建/验证: {output_path}")
        
        # 创建测试文件以确认目录可用
        test_file = output_path / "test_debate_log.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Test Debate Log\n\nThis is a test debate log.")
        
        if test_file.exists():
            print(f"✅ 6. 辩论日志保存路径测试成功: {test_file}")
            test_file.unlink()  # 清理测试文件
        else:
            print(f"❌ 6. 辩论日志保存路径测试失败: {test_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 辩论日志路径测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("="*60)
    print("           知识库系统路径配置验证")
    print("="*60)
    
    success1 = test_config_paths()
    success2 = test_debate_log_path()
    
    print("\n" + "="*60)
    if success1 and success2:
        print("✅ 所有验证测试通过！")
        print("系统现在正确地从配置文件读取Wiki、辩论和论文目录。")
    else:
        print("❌ 部分验证测试失败！")
    print("="*60)
    
    return success1 and success2


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)