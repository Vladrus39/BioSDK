"""BioSDK Runner — uses resonance .venv Python with proper PYTHONPATH."""
import sys
from pathlib import Path

# Add BioSDK to path
BIOSDK = Path(__file__).parent
if str(BIOSDK) not in sys.path:
    sys.path.insert(0, str(BIOSDK))

print(f"BioSDK path: {BIOSDK}")
print(f"Python: {sys.executable}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["dashboard", "daemon", "test", "benchmark", "audit"])
    args = parser.parse_args()
    
    if args.command == "dashboard":
        from biogpu.dashboard.server_v71 import app
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8420)
    elif args.command == "daemon":
        from biogpu.production.daemon_v612 import main
        main()
    elif args.command == "test":
        import subprocess
        subprocess.run([sys.executable, "-m", "pytest", str(BIOSDK / "tests" / "current"), "-v", "--tb=short"])
    elif args.command == "audit":
        from biogpu.production.foundation_v60 import build_production_foundation
        audit = build_production_foundation(Path("outputs/audit_test"))
        import json
        print(json.dumps(audit, indent=2, default=str))
