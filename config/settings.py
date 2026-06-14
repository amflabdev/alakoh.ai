import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class AppSettings:
    """Central configuration vault. Validates variables at boot time."""
    
    def __init__(self):
        # Flask Core Web Settings
        self.HOST: str = os.getenv("APP_HOST", "127.0.0.1")
        self.PORT: int = int(os.getenv("APP_PORT", 5000))
        self.DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
        self.SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY")
        
        self.STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", 8501))
        
        # --- NEW: JWT DYNAMIC EXPIRATION CONFIGURATION ---
        # Reads hours from .env, falls back to 12 hours if not provided
        self.JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", 12))
        self.JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=self.JWT_EXPIRY_HOURS)

        # PostgreSQL Relational Engine Settings
        self.SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL")
        self.SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

        # Intelligence Compute Settings
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

        # FAISS Framework Configurations
        self.FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_DIR", "./faiss_local_store")

        # Execute Boot-Time Validation Safeguards
        self._validate_environment()

    def _validate_environment(self):
        """Ensures all mission-critical secrets are present before boot."""
        if not self.SECRET_KEY:
            raise ValueError("CRITICAL SECURITY ERROR: FLASK_SECRET_KEY must be declared in .env")
            
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError("CRITICAL STORAGE ERROR: DATABASE_URL is missing from configurations.")
            
        if not self.GEMINI_API_KEY:
            raise ValueError("CRITICAL COGNITIVE ERROR: GEMINI_API_KEY must be active.")

# Global singleton configuration instantiation instance
settings = AppSettings()