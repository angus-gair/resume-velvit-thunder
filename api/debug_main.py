#!/usr/bin/env python3
"""
Debug script to test main.py import process
"""

print("=== Debugging main.py import process ===")

print("\n1. Testing individual router imports...")
try:
    from endpoints import router as core_router
    print(f"✅ Core router: {core_router.prefix}, {len(core_router.routes)} routes")
except ImportError as e:
    print(f"❌ Core router failed: {e}")

try:
    from admin_endpoints import router as admin_router
    print(f"✅ Admin router: {admin_router.prefix}, {len(admin_router.routes)} routes")
except ImportError as e:
    print(f"❌ Admin router failed: {e}")

print("\n2. Testing main.py import...")
try:
    import main
    print("✅ Main module imported successfully")
    
    # Check if routers are available in main
    if hasattr(main, 'core_router'):
        print(f"✅ core_router found in main: {main.core_router}")
    else:
        print("❌ core_router not found in main")
        
    if hasattr(main, 'admin_router'):
        print(f"✅ admin_router found in main: {main.admin_router}")
    else:
        print("❌ admin_router not found in main")
        
    # Check the app routes
    print(f"\n3. FastAPI app routes: {len(main.app.routes)}")
    for route in main.app.routes:
        if hasattr(route, 'path'):
            print(f"   - {route.path}")
        elif hasattr(route, 'path_regex'):
            print(f"   - {route.path_regex.pattern}")
            
except ImportError as e:
    print(f"❌ Main import failed: {e}")
except Exception as e:
    print(f"❌ Error accessing main attributes: {e}")

print("\nDone!") 