#!/usr/bin/env python3
"""
Debug script to test router inclusion process
"""

print("=== Debugging router inclusion ===")

# Test the exact import logic from main.py
print("\n1. Testing import logic from main.py...")

core_router = None
admin_router = None

try:
    from endpoints import router as core_router
    from admin_endpoints import router as admin_router
    print("✅ Both routers imported successfully")
    print(f"   Core router: {core_router} (prefix: {core_router.prefix})")
    print(f"   Admin router: {admin_router} (prefix: {admin_router.prefix})")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    core_router = None
    admin_router = None

print(f"\n2. Router variables after import:")
print(f"   core_router is None: {core_router is None}")
print(f"   admin_router is None: {admin_router is None}")

print(f"\n3. Testing inclusion conditions:")
print(f"   if core_router: {bool(core_router)}")
print(f"   if admin_router: {bool(admin_router)}")

print(f"\n4. Testing manual inclusion:")
try:
    from fastapi import FastAPI
    test_app = FastAPI()
    
    print(f"   Test app routes before inclusion: {len(test_app.routes)}")
    
    if core_router:
        test_app.include_router(core_router)
        print(f"   ✅ Core router included. Routes now: {len(test_app.routes)}")
    else:
        print(f"   ❌ Core router not included (is None)")
        
    if admin_router:
        test_app.include_router(admin_router)
        print(f"   ✅ Admin router included. Routes now: {len(test_app.routes)}")
    else:
        print(f"   ❌ Admin router not included (is None)")
        
    print(f"\n   Final test app routes: {len(test_app.routes)}")
    for route in test_app.routes:
        if hasattr(route, 'path'):
            print(f"      - {route.path}")
            
except Exception as e:
    print(f"❌ Manual inclusion failed: {e}")

print("\nDone!") 