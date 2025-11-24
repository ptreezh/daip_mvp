"""
分析系统模型选择机制
"""
import sys
sys.path.insert(0, './src')

from daip_live.core.models import ProviderConfig

def analyze_model_selection():
    print("="*80)
    print("🔍 分析系统模型选择机制")
    print("="*80)
    
    # 检查默认模型配置
    print("📋 默认模型配置分析:")
    try:
        config = ProviderConfig()
        print(f"  默认模型: {config.model}")
        print(f"  默认基础URL: {config.base_url}")
    except Exception as e:
        print(f"  ❌ 默认模型配置访问失败: {e}")
    
    # 检查TUI中的模型初始化
    print(f"\n🔧 TUI模型初始化分析:")
    print("  模型名称: 在初始化时设置为 'llama3:8b'")
    print("  模型列表: 从系统环境中动态获取")
    print("  模型切换: 通过 /model 命令或界面操作进行")
    
    # 检查辩论系统中的模型分配
    print(f"\n🗣️ 多模型辩论系统模型分配:")
    print("  问题: 当前模型分配可能依赖硬编码")
    print("  期望: 系统应动态检测可用模型并智能分配")
    
    # 检查Ollama模型可用性检测
    print(f"\n🔍 Ollama模型可用性检测:")
    print("  现状: 可能没有实现动态模型检测")
    print("  需求: 系统应首次启动时扫描可用模型")
    print("  需求: 辩论时动态分配最合适的模型给不同角色")
    
    print(f"\n🔧 检查现有模型管理机制:")
    
    # 查找模型管理相关代码
    import os
    model_files = []
    for root, dirs, files in os.walk("D:/DAIP/refactdoc/src/daip_live"):
        for file in files:
            if 'model' in file.lower() and not file.endswith(('.pyc', '.pyo')):
                model_files.append(os.path.join(root, file))
    
    print(f"  发现模型相关文件:")
    for f in model_files[:10]:  # 显示前10个
        print(f"    • {os.path.relpath(f, 'D:/DAIP/refactdoc/src/daip_live')}")
    
    if len(model_files) > 10:
        print(f"    ... 还有 {len(model_files)-10} 个模型相关文件")
    
    print(f"\n⚠️  当前问题诊断:")
    print(f"  1. 硬编码模型: 系统可能在多处使用固定的模型名")
    print(f"  2. 缺失环境检测: 启动时未自动检测可用模型")  
    print(f"  3. 静态分配: 辩论角色可能使用固定模型而非动态最优选择")
    print(f"  4. 失败处理: 模型不可用时未自动检测和切换")
    
    print(f"\n🎯 建议的改进方案:")
    print(f"  1. 环境扫描: 系统启动时自动扫描Ollama可用模型")
    print(f"  2. 动态配置: 根据可用模型设置最优默认值")
    print(f"  3. 智能分配: 根据角色需求选择最适合模型")
    print(f"  4. 自愈机制: 模型失败时自动检测并切换")
    
    print("="*80)
    return True

if __name__ == "__main__":
    success = analyze_model_selection()
    print(f"\n分析完成: {'✅ 成功' if success else '❌ 失败'}")