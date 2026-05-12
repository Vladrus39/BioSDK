"""Check if dashboard module imports and then start it."""
import sys
sys.path.insert(0, ".")

try:
    from biogpu.dashboard.server_v71 import app
    print("Dashboard module OK")
    print(f"Routes: {len(app.routes)}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
