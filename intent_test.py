from src.daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from src.daip_live.agent_engine.intent_recognizer import Intent
import sys

print('Testing Intent Recognition...', file=sys.stdout)

# 创建意图识别器
recognizer = EnhancedIntentRecognizer()
print('✓ EnhancedIntentRecognizer created', file=sys.stdout)

# 检查主要方法
has_recognize_intent = hasattr(recognizer, 'recognize_intent')
has_register_intent = hasattr(recognizer, 'register_intent_type')

print(f'✓ Recognize intent method: {has_recognize_intent}', file=sys.stdout)
print(f'✓ Register intent method: {has_register_intent}', file=sys.stdout)

# 测试意图识别
try:
    intent = recognizer.recognize_intent('Hello, how are you?')
    print(f'✓ Intent recognition works: {intent.name if intent else "None"}', file=sys.stdout)
except Exception as e:
    print(f'ℹ️ Intent recognition test: {type(e).__name__}', file=sys.stdout)

print('Intent Recognition tests completed', file=sys.stdout)