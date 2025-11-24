"""
全面规范文档审查策略
"""
import os
from pathlib import Path

def comprehensive_specs_review():
    print("="*90)
    print("🔍 全面规范文档审查与功能映射")
    print("="*90)
    
    print("📋 扫描所有规格文档...")
    
    # 扫描所有规格目录
    specs_dir = Path("D:/DAIP/refactdoc/specs")
    all_specs = []
    
    for root, dirs, files in os.walk(specs_dir):
        for file in files:
            if file.endswith('.md'):
                full_path = Path(root) / file
                all_specs.append(full_path)
    
    print(f"📁 找到 {len(all_specs)} 个规格文档:")
    for spec in all_specs:
        print(f"   • {spec.relative_to(specs_dir)}")
    
    print()
    
    # 扫描src目录以发现所有功能模块
    print("🔧 扫描源代码以发现所有功能模块...")
    src_dir = Path("D:/DAIP/refactdoc/src/daip_live")
    modules = []
    
    for root, dirs, files in os.walk(src_dir):
        for dir_name in dirs:
            if not dir_name.startswith('__'):
                full_path = Path(root) / dir_name
                modules.append(full_path)
    
    print(f"📦 找到 {len(modules)} 个功能模块:")
    for module in sorted(modules):
        rel_path = module.relative_to(src_dir)
        print(f"   • {rel_path}")
    
    print()
    
    # 检查未映射的功能
    print("⚠️  检查未映射的功能...")
    
    # 已知有功能但可能缺少规格的功能模块
    unconfirmed_modules = [
        'agent_engine', 
        'knowledge', 
        'memory', 
        'model_provider', 
        'permissions', 
        'persistence',
        'wiki',
        'p4_role_manager_tools',
        'p8_debate_system',
        'tui_v1',
        'doc'
    ]
    
    print(f"🔍 详细检查核心功能模块是否有对应规格...")
    
    # 检查每个模块的功能
    checked_modules = {}
    
    # agent_engine 模块
    agent_engine_features = [
        "意图识别器 (Intent Recognizer)",
        "增强意图识别器 (Enhanced Intent Recognizer)",
        "个人助手功能 (Personal Assistant)",
        "参数验证系统 (Parameter Validation)",
        "澄清服务 (Clarification Service)"
    ]
    
    # knowledge 模块
    knowledge_features = [
        "知识库管理 (Knowledge Manager)",
        "语义搜索 (Semantic Search)",
        "FAISS向量索引 (Vector Indexing)",
        "知识同步 (Sync Capabilities)"
    ]
    
    # wiki 模块
    wiki_features = [
        "维基页面管理 (Wiki Page Management)",
        "多角色协作 (Multi-Role Collaboration)", 
        "内容创建 (Content Creation)",
        "页面搜索 (Page Search)"
    ]
    
    # doc 模块 - 论文下载和文档转换
    doc_features = [
        "论文搜索和下载 (Paper Search & Download)",
        "文档格式转换 (Document Conversion)",
        "PDF处理器 (PDF Processing)",
        "PPT生成器 (PPT Generator)"
    ]
    
    # debate_system 模块
    debate_features = [
        "多模型辩论 (Multi-Model Debate)",
        "辩论历史追踪 (Debate History)",
        "角色分配 (Role Assignment)", 
        "多轮辩论 (Multi-Round Debate)"
    ]
    
    checked_modules = {
        'agent_engine': agent_engine_features,
        'knowledge': knowledge_features, 
        'wiki': wiki_features,
        'doc': doc_features,
        'p8_debate_system': debate_features
    }
    
    print("\n📋 功能模块映射状态:")
    missing_specs = []
    
    for module, features in checked_modules.items():
        print(f"\n  📄 {module.upper()} 模块功能:")
        for feature in features:
            spec_found = any(module.lower() in str(spec).lower() for spec in all_specs)
            status = "✅" if spec_found else "❌"
            print(f"    {status} {feature}")
            if not spec_found:
                missing_specs.append((module, feature))
    
    print(f"\n📊 映射统计:")
    print(f"   总功能模块: {len(checked_modules)}")
    print(f"   缺失规格文档: {len(missing_specs)}")
    
    if missing_specs:
        print(f"\n⚠️  以下功能可能缺少规格文档:")
        for module, feature in missing_specs:
            print(f"   • {module}: {feature}")
    else:
        print(f"\n✅ 所有主要功能都已映射到规格文档!")
    
    print(f"\n🎯 全面审查策略:")
    print(f"   1. 创建缺失的规格文档")
    print(f"   2. 更新现有规格以反映实际实现") 
    print(f"   3. 确保所有功能都记录在主控文档中")
    print(f"   4. 建立文档变更跟踪机制")
    
    print("="*90)
    return missing_specs

if __name__ == "__main__":
    missing_specs = comprehensive_specs_review()
    print(f"\n📝 全面规格审查完成，发现 {len(missing_specs)} 个可能的缺失功能规格")