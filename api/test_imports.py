#!/usr/bin/env python3
"""
Test script to verify router imports
"""

print("Testing router imports...")

try:
    from endpoints import router as core_router
    print("✅ Core router imported successfully")
    print(f"   Prefix: {core_router.prefix}")
    print(f"   Routes: {len(core_router.routes)}")
except ImportError as e:
    print(f"❌ Failed to import core router: {e}")

try:
    from admin_endpoints import router as admin_router
    print("✅ Admin router imported successfully")
    print(f"   Prefix: {admin_router.prefix}")
    print(f"   Routes: {len(admin_router.routes)}")
except ImportError as e:
    print(f"❌ Failed to import admin router: {e}")

print("\nTesting main app import...")
try:
    import main
    print("✅ Main app imported successfully")
except ImportError as e:
    print(f"❌ Failed to import main app: {e}")

print("\nDone!") 