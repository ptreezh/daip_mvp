"""
验证系统配置更新 - 检查各组件是否能正确定位到新目录结构
"""

import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

def validate_configurations():
    """验证配置文件中的所有目录路径设置"""
    print("=== 系统配置验证 ===\n")
    
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ 配置文件不存在")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("配置文件加载成功\n")
    
    # 检查各个目录配置
    expected_paths = [
        ("knowledge_base.directory", "knowledge/"),
        ("debate.logs_directory", "knowledge/debate/"),
        ("paper.download_directory", "knowledge/paper/"),
        ("wiki.pages_directory", "knowledge/wiki/")
    ]
    
    all_good = True
    for key_path, expected_value in expected_paths:
        keys = key_path.split('.')
        current = config
        for k in keys:
            current = current[k]
        
        if current == expected_value:
            print(f"✅ {key_path}: {current}")
        else:
            print(f"❌ {key_path}: 期望 {expected_value}, 实际 {current}")
            all_good = False
    
    print()
    return all_good


def validate_directories():
    """验证目录结构是否正确创建"""
    print("=== 目录结构验证 ===\n")
    
    expected_dirs = [
        Path("knowledge"),
        Path("knowledge/debate"),
        Path("knowledge/paper"),
        Path("knowledge/wiki")
    ]
    
    all_good = True
    for directory in expected_dirs:
        exists = directory.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {directory}/ : {'存在' if exists else '不存在'}")
        if not exists:
            all_good = False
    
    print()
    return all_good


def validate_moved_content():
    """验证迁移的内容是否正确"""
    print("=== 迁移内容验证 ===\n")
    
    # 检查wiki内容是否已迁移
    wiki_dir = Path("knowledge/wiki")
    if wiki_dir.exists():
        wiki_files = list(wiki_dir.glob("*.md"))
        print(f"✅ Wiki目录存在，找到 {len(wiki_files)} 个MD文件")
        if wiki_files:
            print("   Wiki文件列表 (前5个):")
            for wf in wiki_files[:5]:
                print(f"   - {wf.name}")
    else:
        print("❌ Wiki目录不存在")
        return False
    
    # 检查论文内容是否已迁移
    paper_dir = Path("knowledge/paper")
    if paper_dir.exists():
        paper_subdirs = [d for d in paper_dir.iterdir() if d.is_dir()]
        paper_files = list(paper_dir.rglob("*.pdf"))
        print(f"✅ 论文目录存在，找到 {len(paper_subdirs)} 个子目录和 {len(paper_files)} 个PDF文件")
    else:
        print("❌ 论文目录不存在")
        return False
    
    # 检查旧的目录结构是否已清理（可选验证）
    old_docs = Path("docs")
    if old_docs.exists():
        remaining_items = list(old_docs.iterdir())
        if remaining_items:
            print(f"ℹ️  旧的docs目录仍有 {len(remaining_items)} 个项目")
        else:
            print("✅ 旧的docs目录已清空")
    
    print()
    return True


def validate_system_ready():
    """验证系统是否准备好使用新结构"""
    print("=== 系统准备状态验证 ===\n")
    
    config_valid = validate_configurations()
    dirs_valid = validate_directories()
    content_valid = validate_moved_content()
    
    print("="*60)
    print("验证总结:")
    print(f"- 配置验证: {'✅ 通过' if config_valid else '❌ 失败'}")
    print(f"- 目录验证: {'✅ 通过' if dirs_valid else '❌ 失败'}")
    print(f"- 内容验证: {'✅ 通过' if content_valid else '❌ 失败'}")
    
    overall_success = config_valid and dirs_valid and content_valid
    print(f"\n整体状态: {'✅ 系统配置更新成功' if overall_success else '❌ 系统配置存在问题'}")
    
    if overall_success:
        print("\n🎉 新的知识库目录结构已成功配置！")
        print("\n新结构说明:")
        print("- 知识库主目录: knowledge/")
        print("- 辩论日志目录: knowledge/debate/")
        print("- 论文下载目录: knowledge/paper/")
        print("- Wiki页面目录: knowledge/wiki/")
        print("\n系统现在可以根据新的目录结构正确运行。")
    
    return overall_success


if __name__ == "__main__":
    validate_system_ready()