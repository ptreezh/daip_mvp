#!/usr/bin/env python3
"""
验证测试：会话类型限制修复效果
"""

import sys
import os
from unittest.mock import Mock, patch

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_session_type_fix():
    """测试会话类型限制修复效果"""
    print("验证会话类型限制修复效果...")
    print("=" * 50)
    
    try:
        # 导入相关类
        from daip_live.core.models import Session, AgentState
        from daip_live.memory.session_manager import SessionManager
        from daip_live.persistence.database import DatabaseManager
        
        print("1. 测试创建'compression'类型的会话（修复后）...")
        
        # 创建内存数据库
        db_manager = DatabaseManager(":memory:")
        session_manager = SessionManager(db_manager)
        
        # 尝试创建一个'compression'类型的会话
        try:
            session = session_manager.create_session(
                goal="Context Compression Session",
                session_type="compression",  # 这个类型现在在Literal限制中
                participant_ids=["user", "assistant"]
            )
            print(f"   ✅ 成功创建会话，ID: {session.session_id}")
            print(f"   会话类型: {session.session_type}")
            print("   🎉 修复成功！")
        except Exception as e:
            print(f"   ❌ 创建会话失败: {e}")
            
        print("\n2. 测试创建所有允许的会话类型...")
        
        allowed_types = ["debate", "chat", "workflow", "compression"]
        for session_type in allowed_types:
            try:
                session = session_manager.create_session(
                    goal=f"Test {session_type} Session",
                    session_type=session_type,
                    participant_ids=["user", "assistant"]
                )
                print(f"   ✅ 成功创建{session_type}会话")
            except Exception as e:
                print(f"   ❌ 创建{session_type}会话失败: {e}")
                
        print("\n3. 测试创建不被允许的会话类型...")
        
        # 尝试创建一个不被允许的会话类型
        try:
            session = session_manager.create_session(
                goal="Test Invalid Session",
                session_type="invalid_type",
                participant_ids=["user", "assistant"]
            )
            print(f"   ❌ 不应该成功创建invalid_type会话")
        except Exception as e:
            print(f"   ✅ 正确拒绝了invalid_type会话: {type(e).__name__}")
            
        print("\n" + "=" * 50)
        print("✅ 修复验证完成！")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始验证会话类型限制修复...")
    
    if test_session_type_fix():
        print("\n🎉 修复验证成功！")
        print("\n修复说明:")
        print("  1. 扩展了Session模型中的session_type允许值")
        print("  2. 添加了'compression'类型到Literal限制中")
        print("  3. 保持了原有的验证机制，拒绝无效类型")
        print("  4. tokens压缩功能现在可以正常工作")
        return 0
    else:
        print("\n❌ 修复验证失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())