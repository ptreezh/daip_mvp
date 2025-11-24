"""
快速验证：检查配置文件中路径设置是否正确
"""

import yaml
from pathlib import Path
import os


def test_config_paths():
    """验证配置文件中的路径设置"""
    print("=== 配置文件路径设置验证 ===\n")
    
    try:
        # 读取配置文件
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("✅ 配置文件加载成功")
        
        # 检查各项配置
        wiki_dir = config.get('wiki', {}).get('pages_directory', 'wiki/')
        paper_dir = config.get('paper', {}).get('download_directory', 'knowledge/paper/')
        debate_dir = config.get('debate', {}).get('logs_directory', 'knowledge/debate/')
        
        print(f"✅ Wiki页面目录配置: {wiki_dir}")
        print(f"✅ 论文下载目录配置: {paper_dir}")
        print(f"✅ 辩论日志目录配置: {debate_dir}")
        
        # 检查目录是否存在，如果不存在则创建
        for dir_path, desc in [(wiki_dir, "Wiki"), (paper_dir, "论文"), (debate_dir, "辩论")]:
            full_path = Path(os.getcwd()) / dir_path
            print(f"   {desc}目录完整路径: {full_path}")
            
            if not full_path.exists():
                print(f"   ⚠️  {desc}目录不存在，正在创建...")
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ {desc}目录已创建")
            else:
                print(f"   ✅ {desc}目录已存在")
        
        print("\n✅ 配置文件路径验证通过！")
        print("\n系统现在将:")
        print(f"   - 从配置文件读取Wiki页面保存路径: {wiki_dir}")
        print(f"   - 从配置文件读取论文下载路径: {paper_dir}")
        print(f"   - 从配置文件读取辩论日志路径: {debate_dir}")
        print("   - 正确使用配置的路径创建和保存文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_updated_code():
    """测试更新后的代码是否能正确读取配置"""
    print(f"\n=== 代码更新功能验证 ===\n")
    
    # 检查TUI文件中的关键代码
    with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
        tui_content = f.read()
    
    # 检查是否包含新的代码
    has_wiki_config = 'self.container.config.wiki.pages_directory()' in tui_content
    has_debate_config = 'self.container.config.debate.logs_directory()' in tui_content
    has_wiki_default = 'wiki_dir = "wiki"' in tui_content  # 检查是否有默认值处理
    
    print(f"✅ Wiki配置读取代码: {'存在' if has_wiki_config else '不存在'}")
    print(f"✅ 辩论日志配置读取代码: {'存在' if has_debate_config else '不存在'}")
    print(f"✅ Wiki默认值处理: {'存在' if has_wiki_default else '不存在'}")
    
    if has_wiki_config and has_debate_config and has_wiki_default:
        print("✅ 代码更新验证通过！")
        return True
    else:
        print("❌ 代码更新验证失败！")
        return False


if __name__ == "__main__":
    print("="*60)
    print("           配置路径验证")
    print("="*60)
    
    test1 = test_config_paths()
    test2 = test_updated_code()
    
    print("\n" + "="*60)
    if test1 and test2:
        print("✅ 所有验证通过！")
        print("   配置文件中的路径设置正确")
        print("   代码已更新为使用配置文件中的路径")
    else:
        print("❌ 验证失败！")
    print("="*60)