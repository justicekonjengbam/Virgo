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

# Create the FastAPI application
fastapi_app = app.main.create_app()

try:
    import gradio as gr

    with gr.Blocks(title="VIRGO CabApp Backend") as demo:
        gr.Markdown("""
        # 🚕 VIRGO CabApp Backend is Live!
        
        The backend API is running and ready to handle ride bookings, driver dispatch, and user authentication.
        
        * **Status:** Online
        * **Health Check:** `/health`
        * **API Docs:** `/docs`
        """)

    # Mount Gradio onto the FastAPI app so both UI and API endpoints work seamlessly
    app = gr.mount_gradio_app(fastapi_app, demo, path="/")
except ImportError:
    app = fastapi_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
