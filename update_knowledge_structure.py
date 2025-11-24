"""
知识库目录结构配置更新器
将系统的各种目录配置更新为新的知识库结构：
- 知识库目录: knowledge/
- 辩论日志目录: knowledge/debate/
- 论文下载目录: knowledge/paper/
- Wiki页面目录: knowledge/wiki/
"""

import os
import yaml
from pathlib import Path
import shutil


def update_system_directories():
    """更新系统目录结构"""
    print("=== 知识库目录结构配置更新器 ===\n")
    
    # 1. 创建知识库主目录结构
    print("1. 创建知识库目录结构...")
    knowledge_base_dir = Path("knowledge")
    debate_dir = knowledge_base_dir / "debate"
    paper_dir = knowledge_base_dir / "paper"
    wiki_dir = knowledge_base_dir / "wiki"
    
    for directory in [knowledge_base_dir, debate_dir, paper_dir, wiki_dir]:
        directory.mkdir(exist_ok=True)
        print(f"   ✓ 创建目录: {directory}")
    
    print()
    
    # 2. 检查并移动现有文件到新结构
    print("2. 检查是否存在旧的目录结构...")
    
    # 检查旧的docs目录
    old_docs_dir = Path("docs")
    if old_docs_dir.exists():
        print(f"   发现旧的docs目录: {old_docs_dir}")
        # 移动非核心系统文件到知识库根目录
        for item in old_docs_dir.iterdir():
            if item.name != "index.faiss":  # 保留索引文件
                dest = knowledge_base_dir / item.name
                if item.is_file():
                    shutil.move(str(item), str(dest))
                    print(f"   ✓ 移动文件: {item.name}")
                elif item.is_dir():
                    shutil.move(str(item), str(dest))
                    print(f"   ✓ 移动目录: {item.name}")
    
    # 检查旧的wiki目录
    old_wiki_dir = Path("wiki")
    if old_wiki_dir.exists():
        print(f"   发现旧的wiki目录: {old_wiki_dir}")
        # 移动wiki内容到新的wiki目录
        for item in old_wiki_dir.iterdir():
            dest = wiki_dir / item.name
            if item.is_file():
                shutil.move(str(item), str(dest))
                print(f"   ✓ 移动wiki文件: {item.name}")
            elif item.is_dir():
                shutil.move(str(item), str(dest))
                print(f"   ✓ 移动wiki目录: {item.name}")
    
    # 检查旧的papers目录
    old_papers_dir = Path("papers")
    if old_papers_dir.exists():
        print(f"   发现旧的papers目录: {old_papers_dir}")
        # 移动论文内容到新的paper目录
        for item in old_papers_dir.iterdir():
            dest = paper_dir / item.name
            if item.is_file():
                shutil.move(str(item), str(dest))
                print(f"   ✓ 移动论文文件: {item.name}")
            elif item.is_dir():
                shutil.move(str(item), str(dest))
                print(f"   ✓ 移动论文目录: {item.name}")
    
    print()
    
    # 3. 更新配置文件
    print("3. 更新配置文件...")
    
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 更新配置
        config['knowledge_base'] = {'directory': 'knowledge/'}
        config['debate'] = {'logs_directory': 'knowledge/debate/'}
        config['paper'] = {'download_directory': 'knowledge/paper/'}
        config['wiki'] = {'pages_directory': 'knowledge/wiki/'}
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print("   ✓ 更新 config.yaml 配置文件")
    else:
        # 如果配置文件不存在，创建一个
        config = {
            'database': {'path': 'daip_live.db'},
            'knowledge_base': {'directory': 'knowledge/'},
            'debate': {'logs_directory': 'knowledge/debate/'},
            'paper': {'download_directory': 'knowledge/paper/'},
            'wiki': {'pages_directory': 'knowledge/wiki/'},
            'llm_provider': {
                'default_model': 'ollama/qwen3-vl:235b-cloud',
                'embedding_model': 'mock-embedding'
            },
            'mcp': {
                'permissions': {
                    'allowed_domains': ['arxiv.org', 'doi.org'],
                    'default': 'ask'
                }
            },
            'role_manager': {'roles_dir': 'roles/'}
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print("   ✓ 创建 config.yaml 配置文件")
    
    print()
    
    # 4. 显示新结构
    print("4. 新的知识库结构:")
    print("   knowledge/")
    print("   ├── debate/     # 辩论日志目录")
    print("   ├── paper/      # 论文下载目录")
    print("   └── wiki/       # Wiki页面目录")
    print()
    
    # 5. 创建README说明文件
    print("5. 创建知识库使用说明...")
    readme_content = """# 知识库目录结构

这是DAIP-LIVE系统的知识库目录结构：

## 目录说明

- `debate/` - 辩论日志和历史记录
- `paper/` - 论文、文档和其他资源
- `wiki/` - Wiki页面和知识条目

## 使用方法

- 系统会自动在此目录结构中同步和管理各类文档
- 所有知识库相关的操作都在此目录下进行
- 可以通过 `daip knowledge sync` 命令同步此目录
"""
    
    readme_path = knowledge_base_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✓ 创建知识库使用说明")
    
    print("\n" + "="*60)
    print("✅ 知识库目录结构更新完成！")
    print("\n新结构已创建，配置已更新。系统现在将使用以下目录：")
    print("- 知识库: knowledge/")
    print("- 论文: knowledge/paper/")
    print("- 辩论日志: knowledge/debate/")
    print("- Wiki: knowledge/wiki/")
    print("\n系统重启后，所有新的文档都将在新目录结构中管理。")


def validate_new_structure():
    """验证新的目录结构"""
    print("\n=== 验證新的目錄結構 ===")
    
    expected_dirs = [
        Path("knowledge"),
        Path("knowledge/debate"),
        Path("knowledge/paper"), 
        Path("knowledge/wiki")
    ]
    
    all_good = True
    for directory in expected_dirs:
        if directory.exists():
            print(f"   ✓ {directory}/ 存在")
        else:
            print(f"   ✗ {directory}/ 不存在")
            all_good = False
    
    if all_good:
        print("\n✅ 所有目录结构驗證通過！")
    else:
        print("\n❌ 部分目錄結構驗證失敗！")
    
    return all_good


if __name__ == "__main__":
    update_system_directories()
    validate_new_structure()