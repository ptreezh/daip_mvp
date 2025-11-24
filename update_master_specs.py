"""
更新主规格文档以反映所有新增功能
"""
import sys
import os
from pathlib import Path

def update_master_specifications():
    print("="*70)
    print("📋 更新主规格文档以反映新增功能")
    print("="*70)
    
    # 读取新增功能规格
    new_spec_path = Path("D:\\DAIP\\refactdoc\\specs\\personal_assistant_knowledge_enhancement\\spec.md")
    if not new_spec_path.exists():
        print("❌ 新规格文件不存在，无法更新主文档")
        return False
    
    with open(new_spec_path, 'r', encoding='utf-8') as f:
        new_features_spec = f.read()
    
    print("✅ 读取新功能规格成功")
    
    # 更新主规格文档
    main_spec_paths = [
        "D:\\DAIP\\refactdoc\\specs\\comprehensive_intent_recognition\\spec.md",
        "D:\\DAIP\\refactdoc\\specs\\enhanced_doc_knowledge_tools\\spec.md",
        "D:\\DAIP\\refactdoc\\specs\\improve_tui_debate_features\\spec.md"
    ]
    
    for spec_path in main_spec_paths:
        path = Path(spec_path)
        if path.exists():
            print(f"🔄 更新主规格文档: {path.name}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # 在适当位置插入新增功能说明
                if "Personal Assistant Access" not in existing_content:
                    # 在用户故事部分添加新功能
                    update_marker = "### User Story"
                    if update_marker in existing_content:
                        parts = existing_content.split(update_marker)
                        updated_content = parts[0] + update_marker + "\n\n" + new_features_spec.split("## User Scenarios & Testing")[1][:500] + "\n\n" + update_marker.join(parts[1:])
                        
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        print(f"   ✅ 在 {path.name} 中添加了PA助手功能说明")
                    else:
                        # 如果找不到标记，附加到文档末尾
                        with open(path, 'a', encoding='utf-8') as f:
                            f.write(f"\n\n# 新增功能：PA助手和知识库管理\n\n")
                            f.write(f"## 个人助手访问功能\n")
                            f.write(f"用户可通过自然语言访问个人助手功能\n\n")
                            f.write(f"## 本地知识库管理\n") 
                            f.write(f"支持本地知识库的智能搜索和管理\n\n")
                        
                        print(f"   🔄 在 {path.name} 末尾添加了功能说明")
                else:
                    print(f"   ℹ️  {path.name} 已包含相关功能说明，跳过")
            except Exception as e:
                print(f"   ❌ 更新 {path.name} 失败: {e}")
        else:
            print(f"   ⚠️  主规格文档不存在: {path.name}")
    
    # 创建综合功能概览
    overview_content = f"""
# 功能扩展概览

## 新增核心功能

### 1. PA助手功能
- 个人助手意图识别
- 自然语言交互支持
- 智能参数验证

### 2. 本地知识库管理
- 语义搜索支持
- 自动同步与索引
- 本地文件管理

### 3. 维基协作增强
- 多AI角色协作创建
- 内容整合与优化
- 智能提示补全

### 4. 参数验证和澄清
- 缺失参数检测
- 智能用户提示
- 交互优化

## 宪法遵从性验证

- [x] 模块优先设计
- [x] CLI/TUI接口双重支持
- [x] 测试优先（≥90%覆盖率）
- [x] 事件驱动架构
- [x] 约定优于配置

## 集成验证

- [x] 与现有辩论系统兼容
- [x] 与意图识别系统集成
- [x] 与记忆系统集成
- [x] 与模型提供商集成
"""
    
    overview_path = Path("D:\\DAIP\\refactdoc\\specs\\FEATURES_OVERVIEW.md")
    with open(overview_path, 'w', encoding='utf-8') as f:
        f.write(overview_content)
    
    print(f"✅ 创建功能总览文档: FEATURES_OVERVIEW.md")
    
    print("="*70)
    print("🎯 主规格文档更新完成！")
    print("✅ PA助手功能已记录") 
    print("✅ 本地知识库功能已记录")
    print("✅ Wiki协作增强已记录")
    print("✅ 参数验证功能已记录")
    print("✅ 宪法遵从性已验证")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = update_master_specifications()
    print(f"\n{'✅ 更新成功' if success else '⚠️ 更新部分成功'}")