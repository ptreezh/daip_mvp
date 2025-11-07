#!/usr/bin/env python3
"""
测试用例：重现会话类型限制问题
"""

import sys
import os
from unittest.mock import Mock, patch

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_session_type_restriction():
    """测试会话类型限制问题"""
    print("测试会话类型限制问题...")
    print("=" * 50)
    
    try:
        # 导入相关类
        from daip_live.core.models import Session, AgentState
        from daip_live.memory.session_manager import SessionManager
        from daip_live.persistence.database import DatabaseManager
        
        print("1. 测试创建'compression'类型的会话...")
        
        # 创建内存数据库
        db_manager = DatabaseManager(":memory:")
        session_manager = SessionManager(db_manager)
        
        # 尝试创建一个'compression'类型的会话
        try:
            session = session_manager.create_session(
                goal="Context Compression Session",
                session_type="compression",  # 这个类型不在Literal限制中
                participant_ids=["user", "assistant"]
            )
            print(f"   ✅ 成功创建会话，ID: {session.session_id}")
            print(f"   会话类型: {session.session_type}")
        except Exception as e:
            print(f"   ❌ 创建会话失败: {e}")
            print("   问题确认：Session模型限制了session_type必须是'debate', 'chat', 'workflow'之一")
            
        print("\n2. 测试创建允许的会话类型...")
        
        # 尝试创建一个允许的会话类型
        try:
            session = session_manager.create_session(
                goal="Test Chat Session",
                session_type="chat",  # 这个类型在Literal限制中
                participant_ids=["user", "assistant"]
            )
            print(f"   ✅ 成功创建chat会话，ID: {session.session_id}")
            print(f"   会话类型: {session.session_type}")
        except Exception as e:
            print(f"   ❌ 创建chat会话失败: {e}")
            
        print("\n3. 测试创建'debate'类型的会话...")
        
        # 尝试创建一个debate会话类型
        try:
            session = session_manager.create_session(
                goal="Test Debate Session",
                session_type="debate",  # 这个类型在Literal限制中
                participant_ids=["pro_arguer", "con_arguer"]
            )
            print(f"   ✅ 成功创建debate会话，ID: {session.session_id}")
            print(f"   会话类型: {session.session_type}")
        except Exception as e:
            print(f"   ❌ 创建debate会话失败: {e}")
            
        print("\n" + "=" * 50)
        print("测试完成！问题已确认。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试会话类型限制问题...")
    
    if test_session_type_restriction():
        print("\n📋 问题分析:")
        print("  Session模型中的session_type字段被限制为Literal['debate', 'chat', 'workflow']")
        print("  但在TUI中创建压缩会话时使用了'session_type'='compression'")
        print("  这导致了Pydantic验证错误")
        return 0
    else:
        print("\n❌ 测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())