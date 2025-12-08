#!/usr/bin/env python3
"""Test script to check DAIP-LIVE functionality"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_tui():
    """Test TUI loading"""
    try:
        from daip_live.tui_modular import DAIP_TUI
        print("✅ TUI Module loaded successfully")
        return True
    except Exception as e:
        print(f"❌ TUI loading failed: {e}")
        return False

def test_debate_system():
    """Test debate system loading"""
    try:
        from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
        print("✅ Enhanced Debate Manager loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Debate Manager loading failed: {e}")
        return False

def test_role_system():
    """Test role and model management"""
    try:
        from daip_live.p4_role_manager_tools.role_manager import RoleManager
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        print("✅ Role Management System loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Role System loading failed: {e}")
        return False

def test_model_provider():
    """Test model provider"""
    try:
        from daip_live.model_provider.provider import LiteLLMProvider
        print("✅ Model Provider loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Model Provider loading failed: {e}")
        return False

def test_config():
    """Test configuration system"""
    try:
        from daip_live.config import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.get_config()
        print("✅ Configuration system loaded successfully")
        print(f"   Database path: {config.database.path}")
        print(f"   Default model: {config.llm_provider.default_model}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing DAIP-LIVE System Components...\n")

    tests = [
        ("Configuration System", test_config),
        ("Model Provider", test_model_provider),
        ("Role System", test_role_system),
        ("Debate System", test_debate_system),
        ("TUI System", test_tui),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n📋 Testing {name}:")
        results.append((name, test_func()))

    print("\n" + "="*50)
    print("📊 TEST SUMMARY:")
    print("="*50)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status:8} {name}")
        if not passed:
            all_passed = False

    print("="*50)
    if all_passed:
        print("\n🎉 ALL COMPONENTS LOADED SUCCESSFULLY!")
        print("\n💡 USAGE:")
        print("   1. Run TUI: python -c \"from daip_live.tui_modular import DAIP_TUI; DAIP_TUI().run()\"")
        print("   2. Check config: python test_system.py")
        print("   3. Test individual components as needed")
        print("\n🤖 多模型辩论功能状态: ✅ 可用")
        print("   - Enhanced Debate Manager: 已加载")
        print("   - Role-based model assignment: 已加载")
        print("   - Multi-round debating: 已加载")
    else:
        print("\n⚠️  SOME COMPONENTS FAILED TO LOAD")
        print("   Please check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()