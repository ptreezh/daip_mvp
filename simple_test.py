import sys
import os
print("Adding path to sys.path")
sys.path.insert(0, './src')

print("Trying import...")
try:
    from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
    print("✅ Import successful")
    
    print("Creating instance...")
    rec = EnhancedIntentRecognizer()
    print("✅ Instance created successfully")
    
    print("Testing '辩论' recognition...")
    intent = rec.recognize_intent('辩论')
    print(f"✅ Recognition result: {intent.name if intent else 'None'}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()