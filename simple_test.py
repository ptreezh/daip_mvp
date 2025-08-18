# 测试 ForumService
print("测试 ForumService...")
try:
    from src.core_services.forum_service import forum_service
    stats = forum_service.get_session_statistics()
    print("✓ ForumService 正常")
    print(f"  统计信息: {stats}")
except Exception as e:
    print(f"✗ ForumService 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 ForumUserInputPanel
print("\n测试 ForumUserInputPanel...")
try:
    from frontend.components.forum_user_input_panel import ForumUserInputPanel
    input_panel = ForumUserInputPanel(session_id='test_session')
    print("✓ ForumUserInputPanel 正常")
except Exception as e:
    print(f"✗ ForumUserInputPanel 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 ForumContextPanel
print("\n测试 ForumContextPanel...")
try:
    from frontend.components.forum_context_panel import ForumContextPanel
    context_panel = ForumContextPanel(session_id='test_session')
    print("✓ ForumContextPanel 正常")
    context_panel.set_topic("测试话题")
    print("✓ ForumContextPanel set_topic 正常")
except Exception as e:
    print(f"✗ ForumContextPanel 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")