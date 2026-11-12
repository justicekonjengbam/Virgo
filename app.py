import sys
from pathlib import Path
import datetime

# ZeroGPU compatibility for Hugging Face
try:
    import spaces
    @spaces.GPU
    def hf_gpu_dummy():
        return True
except Exception:
    pass

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

from app.main import create_app
from app.api.v1.router import api_router
from app.api.v1.routes.health import router as health_router

# Initialize backend database and services
fastapi_app = create_app()

import gradio as gr

with gr.Blocks(title="VIRGO CabApp Backend") as demo:
    gr.Markdown("""
    # 🚕 VIRGO CabApp Backend is Live!
    
    The backend API is running and ready to handle ride bookings, driver dispatch, and user authentication.
    
    * **Status:** Online
    * **Health Check:** `/health`
    * **API Docs:** `/docs`
    """)

# Include all 76 backend API routes directly into Gradio's web application
demo.app.include_router(health_router)
demo.app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    demo.launch()
