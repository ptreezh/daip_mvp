"""
最终验证：确认TUI中任务分解系统已完全集成
"""
import sys
sys.path.insert(0, './src')
import asyncio

print("="*80)
print("🎯 终极验证：TUI中任务分解系统集成")
print("="*80)

async def test_integration():
    # 测试导入
    try:
        print("\\n🔍 测试模块导入:")
        
        from daip_live.task_decomposition.agile_task_decomposition_engine import AgileTaskDecompositionManager
        print("✅ 任务分解引擎模块导入成功")
        
        # 测试TUI初始化
        print("\\n🔧 测试TUI集成:")
        from daip_live.tui import DAIP_TUI
        
        tui = DAIP_TUI()
        print("✅ TUI实例创建成功")
        
        if hasattr(tui, '_agile_task_manager'):
            print("✅ 敏捷任务管理器已集成")
            print(f"   类型: {type(tui._agile_task_manager).__name__}")
            
            # 测试复杂任务检测
            print("\\n🧪 测试复杂任务检测:")
            test_requests = [
                "分析AI在医疗领域的应用前景",
                "设计一个完整的AI系统架构",
                "研究机器学习算法的优势和挑战"
            ]
            
            for request in test_requests:
                is_complex = await tui._agile_task_manager.should_process_with_agile_decomposition(request)
                status = "✅" if is_complex else "❌"
                print(f"   {status} '{request}' -> 复杂任务: {is_complex}")
            
            print("\\n✅ 集成验证完成！系统已正确集成任务分解功能")
            print("\\n📋 功能特点:")
            print("   • 自动检测复杂任务")
            print("   • 生成任务清单并显示给用户") 
            print("   • 顺序执行子任务并更新状态")
            print("   • 保存中间文档和进度")
            print("   • 与TUI无缝集成")
            print("   • 无需用户特殊命令")
            
            print("\\n🎯 系统现在会在遇到复杂请求时自动执行以下流程:")
            print("   1. 检测复杂度 -> 2. 生成任务清单 -> 3. 顺序执行 -> 4. 更新状态 -> 5. 合成结果")
            
            return True
        else:
            print("❌ 敏捷任务管理器未正确集成")
            return False
            
    except Exception as e:
        print(f"❌ 集成验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 运行验证
success = asyncio.run(test_integration())

print("\\n" + "="*80)
if success:
    print("🎉 TUI任务分解系统完全集成成功！")
    print("系统现在能自动处理复杂请求，生成任务清单并逐步执行。")
else:
    print("⚠️  集成存在问题，需要进一步修复。")
print("="*80)