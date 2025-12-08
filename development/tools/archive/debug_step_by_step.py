#!/usr/bin/env python3
"""
逐步调试脚本
"""
import sys
print("Step 1: Basic imports")
sys.path.insert(0, 'src')

print("Step 2: Import model checker")
try:
    from daip_live.p8_debate_system.model_availability_checker import ModelAvailabilityChecker
    print("✅ ModelAvailabilityChecker imported")
except Exception as e:
    print(f"❌ Failed to import ModelAvailabilityChecker: {e}")
    exit(1)

print("Step 3: Create checker instance")
try:
    checker = ModelAvailabilityChecker()
    print("✅ Checker instance created")
except Exception as e:
    print(f"❌ Failed to create checker: {e}")
    exit(1)

print("Step 4: Test pre-flight check (sync part)")
try:
    import asyncio
    async def test_check():
        try:
            result = await checker.pre_flight_check()
            return result
        except Exception as e:
            return False, f"Error in pre_flight_check: {e}"

    print("   Starting async test...")
    result = asyncio.run(test_check())
    print(f"✅ Pre-flight check result: {result}")
except Exception as e:
    print(f"❌ Failed pre-flight check: {e}")
    import traceback
    traceback.print_exc()

print("Step 5: All basic tests completed")