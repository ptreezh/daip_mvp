import sys
sys.path.insert(0, './src')

try:
    from daip_live.p8_debate_system.ollama_instance_manager import OllamaInstanceManager
    print('SUCCESS: OllamaInstanceManager imported successfully')
    
    # Test instantiation
    manager = OllamaInstanceManager()
    print('SUCCESS: OllamaInstanceManager instantiated successfully')
    
    # Check if the method exists
    print('generate_with_model method exists:', hasattr(manager, 'generate_with_model'))
    
except Exception as e:
    print(f'ERROR importing OllamaInstanceManager: {e}')
    import traceback
    traceback.print_exc()