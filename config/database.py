import os
from flask_sqlalchemy import SQLAlchemy
import faiss
from config.settings import settings
from datetime import datetime, timezone

# Initialize the shared PostgreSQL Relational Database Engine handle
db = SQLAlchemy()

# =====================================================================
# 1. FAISS VECTOR COMPUTE STORAGE ENGINE (Replaces ChromaDB)
# =====================================================================
class FAISSVectorStoreManager:
    """
    Central Vector Infrastructure Vault. Replaces ChromaDB to handle 
    high-speed local indexing and searching of embedding models.
    """
    def __init__(self, index_path: str, dimension: int = 768):
        """
        Initializes FAISS. Defaulting to 768 dimensions matching 
        Gemini 2.5 Text Embedding Model specifications.
        """
        self.index_path = index_path
        self.dimension = dimension
        self.index = self._initialize_index()

    def _initialize_index(self):
        """Loads an existing index from local storage directory or builds a clean one."""
        if os.path.exists(self.index_path):
            try:
                return faiss.read_index(self.index_path)
            except Exception:
                # Fallback safeguard in case of disk allocation structural corruptions
                return faiss.IndexFlatL2(self.dimension)
        else:
            # IndexFlatL2 measures exact L2 (Euclidean) distance vector mappings
            return faiss.IndexFlatL2(self.dimension)

    def save_to_disk(self):
        """Commits the in-memory FAISS indices matrix securely back to local storage."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)


# Global singleton instance hook for the AI cognitive layer modules to import
faiss_manager = FAISSVectorStoreManager(
    index_path=settings.FAISS_INDEX_PATH,
    dimension=768
)


# =====================================================================
# 2. POSTGRESQL SCHEMAS FOR USER MANAGEMENT & APPLICATION LIMITS
# =====================================================================
class User(db.Model):
    """
    Core Register and Login table layout. Tracks verified ecosystem actors.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class AnonymousTrialLog(db.Model):
    """
    Gatekeeper ledger tracking. Collects incoming client IPs 
    to restrict unauthenticated guests to exactly 3 lifetime trial runs.
    """
    __tablename__ = 'anonymous_trial_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    
    # CRITICAL: This column tracks exactly when the prompt was used
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class UserQueryLog(db.Model):
    """
    Analytical logging database ledger for authenticated user activities.
    """
    __tablename__ = 'user_query_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())