#!/usr/bin/env python3
"""
测试单独的导入
"""
import sys
print("Starting import test...")
sys.path.insert(0, 'src')

print("1. Testing basic imports...")
try:
    from daip_live.core.models import ProviderConfig
    print("✅ ProviderConfig imported")
except Exception as e:
    print(f"❌ Failed to import ProviderConfig: {e}")

try:
    from daip_live.core.exceptions import ModelError
    print("✅ ModelError imported")
except Exception as e:
    print(f"❌ Failed to import ModelError: {e}")

print("2. Testing provider import...")
try:
    from daip_live.model_provider.provider import LiteLLMProvider
    print("✅ LiteLLMProvider imported")
except Exception as e:
    print(f"❌ Failed to import LiteLLMProvider: {e}")

print("3. Testing creating provider...")
try:
    provider = LiteLLMProvider()
    print("✅ Provider created")
except Exception as e:
    print(f"❌ Failed to create provider: {e}")

print("Import test completed")