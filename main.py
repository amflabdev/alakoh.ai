import os
import sys
import subprocess
import time
from datetime import timedelta
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# Core configurations and settings vault
from config.settings import settings
# FIXED: Import the unified db layer and faiss memory instance
from config.database import db, faiss_manager 
from app.modules.identity_access.routes import auth_bp

# Explicitly pull configurations out of environmental files
load_dotenv()

def run_streamlit_process():
    """Spawns the Streamlit UI dashboard application as an independent background process."""
    dashboard_path = os.path.join("app", "modules", "advisor_workspace", "dashboard.py")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        dashboard_path, 
        "--server.port", str(settings.STREAMLIT_PORT),
        "--server.headless", "true"
    ]
    
    print(f"🚀 Mounting Background Streamlit AI Engine Node on Port {settings.STREAMLIT_PORT}...")
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def create_app():
    """Application Factory Blueprint Configuration Engine."""
    app = Flask(
        __name__,
        template_folder="app/modules/identity_access/templates", # Renders your login.html cleanly
        static_folder="app/shared/static"
    )
    
    # Core Global Configurations and Context Engines
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    
    CORS(app, supports_credentials=True)

    # Initialize PostgreSQL Relational Hooks Context 
    db.init_app(app)
    
    with app.app_context():
        # Auto-generates users and anonymous logs within your database schemas
        db.create_all()
        print("🚀 PostgreSQL Relational Engine Tables Synchronized.")

    # FAISS is automatically initialized and loaded on import via 'faiss_manager'
    print(f"🧠 FAISS Vector Index verified at memory pathway boundary: {settings.FAISS_INDEX_PATH}")

    # Route Registry Mapping Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/")
    def base_landing_node():
        """
        Redirects root website visitors away from Flask's empty surface
        and drops them directly into the Streamlit AI Agent Dashboard.
        """
        from flask import redirect
        # Dynamic address point mapping matching your Streamlit host definitions
        streamlit_url = f"http://{settings.HOST}:{settings.STREAMLIT_PORT}"
        return redirect(streamlit_url)

    return app

if __name__ == "__main__":
    # 1. Fire up the Streamlit interface node sub-process
    run_streamlit_process()
    
    # 2. Briefly pause to let the Streamlit socket register smoothly before gateway opens
    time.sleep(1.5)
    
    # 3. Boot the primary monolithic Flask API Gatekeeper
    app = create_app()
    print(f"🔥 Core Flask Gateway Active at http://{settings.HOST}:{settings.PORT}")
    
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
        use_reloader=False # Absolute must! Prevents reloader from spawning duplicate Streamlit tasks
    )