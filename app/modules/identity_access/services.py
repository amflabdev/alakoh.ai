# app/modules/identity_access/services.py
import jwt
import datetime
import bcrypt
from config.settings import settings
from config.database import db
from app.modules.identity_access.models import UserProfile

class IdentityAccessService:
    """Pure Domain logic orchestrating user registrations and authentication sequences."""

    @staticmethod
    def register_new_candidate(email, raw_password, full_name, target_role) -> bool:
        # Prevent database duplicate records
        existing_user = UserProfile.query.filter_by(email=email).first()
        if existing_user:
            return False

        # Generate secure slow salt hash configuration
        salt = bcrypt.gensalt(rounds=12)
        hashed_pass = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

        # Build structural model instance
        new_profile = UserProfile(
            email=email,
            password_hash=hashed_pass,
            full_name=full_name,
            target_role=target_role
        )
        db.session.add(new_profile)
        db.session.commit()
        return True

    @staticmethod
    def authenticate_user(email, raw_password) -> str:
        """Validates credentials. Returns an asymmetric signed JWT string if successful, or None."""
        user = UserProfile.query.filter_by(email=email).first()
        if not user:
            return None

        # Cross check cryptographic signatures
        if bcrypt.checkpw(raw_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Construct JWT claims token payload data context
            payload = {
                "user_id": user.email,
                "user_name": user.full_name,
                "role": "private_tier",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=4)
            }
            # Sign the cryptographically sealed token via our application server secret
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
            return token
            
        return None