# 修正验证代码中的路径变量错误
import os
from pathlib import Path
import yaml

# 读取配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 正确获取路径
wiki_dir = config.get('wiki', {}).get('pages_directory', 'knowledge/wiki/')
paper_dir = config.get('paper', {}).get('download_directory', 'knowledge/paper/')
debate_dir = config.get('debate', {}).get('logs_directory', 'knowledge/debate/')

# 使用相对路径（相对于项目根目录）
knowledge_base_dir = Path(config.get('knowledge_base', {}).get('directory', 'knowledge'))

print("✅ 修正后的路径配置验证:")
print(f"  - 知识库主目录: {knowledge_base_dir}/")
print(f"  - Wiki页面目录: {wiki_dir}")
print(f"  - 论文下载目录: {paper_dir}") 
print(f"  - 辩论日志目录: {debate_dir}")

# 检查实际路径是否存在
wiki_full_path = Path(os.getcwd()) / wiki_dir
paper_full_path = Path(os.getcwd()) / paper_dir
debate_full_path = Path(os.getcwd()) / debate_dir

print(f"\n实际路径检查:")
print(f"  - Wiki路径: {wiki_full_path} ({'存在' if wiki_full_path.exists() else '不存在'})")
print(f"  - 论文路径: {paper_full_path} ({'存在' if paper_full_path.exists() else '不存在'})")
print(f"  - 辩论路径: {debate_full_path} ({'存在' if debate_full_path.exists() else '不存在'})")

# 创建不存在的目录
for path, name in [(wiki_full_path, "Wiki"), (paper_full_path, "论文"), (debate_full_path, "辩论")]:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"  - 已创建 {name} 目录: {path}")
    else:
        print(f"  - {name} 目录已存在: {path}")

print(f"\n✅ 所有路径现在都已正确配置并创建！")