#!/usr/bin/env python3
"""
Debug script to examine routes in each router
"""

print("=== Debugging router routes ===")

print("\n1. Core router routes:")
try:
    from endpoints import router as core_router
    print(f"Core router prefix: {core_router.prefix}")
    print(f"Core router routes: {len(core_router.routes)}")
    for i, route in enumerate(core_router.routes):
        if hasattr(route, 'path'):
            print(f"   {i+1}. {route.methods} {route.path}")
        elif hasattr(route, 'path_regex'):
            print(f"   {i+1}. {route.path_regex.pattern}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n2. Admin router routes:")
try:
    from admin_endpoints import router as admin_router
    print(f"Admin router prefix: {admin_router.prefix}")
    print(f"Admin router routes: {len(admin_router.routes)}")
    for i, route in enumerate(admin_router.routes):
        if hasattr(route, 'path'):
            print(f"   {i+1}. {route.methods} {route.path}")
        elif hasattr(route, 'path_regex'):
            print(f"   {i+1}. {route.path_regex.pattern}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n3. Main app routes:")
try:
    import main
    print(f"Main app routes: {len(main.app.routes)}")
    for i, route in enumerate(main.app.routes):
        if hasattr(route, 'path'):
            print(f"   {i+1}. {route.methods} {route.path}")
        elif hasattr(route, 'path_regex'):
            print(f"   {i+1}. {route.path_regex.pattern}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nDone!") 