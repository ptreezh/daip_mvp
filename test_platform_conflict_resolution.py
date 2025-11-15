import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print('Testing import after platform directory rename...')

try:
    # Import the modules needed to check if platform conflict is resolved
    import platform as builtin_platform  # Import Python's built-in platform module
    print(f'✅ Built-in platform module: {builtin_platform.system()}')
    
    # Now test our platform adapters
    from src.daip_live.p7_gui_v1.platform_adapters.base import get_current_platform_adapter
    adapter = get_current_platform_adapter()
    platform_name = adapter.get_platform_name()
    print(f'✅ Our platform adapter: {platform_name}')
    
    # Test that ViewModel functions work correctly
    from src.daip_live.p7_gui_v1.viewmodel.base import ViewModel
    
    vm = ViewModel()
    vm.set_property('test_prop', 'test_value')
    assert vm.get_property('test_prop') == 'test_value'
    print('✅ ViewModel property management works')
    
    # Test that CustomTkinter imports without platform conflict now
    print('\nTrying to import customtkinter...')
    import customtkinter as ctk
    print('✅ CustomTkinter imported successfully!')
    
    print('\n🎉 Platform naming conflict appears to be resolved!')
    print('✅ Built-in platform module accessible')
    print('✅ Our platform adapters work')
    print('✅ ViewModels functional')
    print('✅ CustomTkinter can be imported')
    print('✅ Ready for GUI application launch')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()