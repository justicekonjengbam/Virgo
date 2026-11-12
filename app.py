import sys
from pathlib import Path
import datetime

# Compatibility fix for Python 3.10 environments
if not hasattr(datetime, "UTC"):
    datetime.UTC = datetime.timezone.utc

# Add backend directory to module search path
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Prevent self-shadowing if loaded as 'app'
current_app_mod = sys.modules.get("app")
if current_app_mod and not hasattr(current_app_mod, "__path__"):
    del sys.modules["app"]

import app.main

# Expose main and app so both 'app:app' and 'app.main:app' work from root
main = app.main
app = app.main.create_app()

try:
    import gradio as gr
    with gr.Blocks(title="VIRGO CabApp Backend") as demo:
        gr.Markdown("# 🚕 VIRGO CabApp Backend is Live!")
    from app.api.v1.router import api_router
    from app.api.v1.routes.health import router as health_router
    demo.app.include_router(health_router)
    demo.app.include_router(api_router, prefix="/api/v1")
except ImportError:
    demo = None

if __name__ == "__main__":
    if demo is not None:
        demo.launch()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
