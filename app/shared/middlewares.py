import jwt
from functools import wraps
from flask import request, jsonify, g
from config.settings import settings
from config.database import db, AnonymousTrialLog

def application_tier_gatekeeper():
    """
    Unified Security Guardrail:
    - Enforces 100-character prompt limits.
    - Authenticated Users: Allows seamless 12-hour active access.
    - Guests: Restricts access to EXACTLY 3 lifetime uses based on IP.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Capture and validate prompt length
            request_data = request.get_json(silent=True) or {}
            user_prompt = str(request_data.get("prompt", "")).strip()

            if len(user_prompt) > 100:
                return jsonify({
                    "status": "rejected",
                    "message": "Prompt exceeds the 100-character limitation constraint."
                }), 400

            # 2. Extract Token
            token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.args.get('token')

            # --- CASE A: REGISTERED USER ---
            if token:
                try:
                    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                    g.current_identity = {"user_id": decoded.get("user_id"), "role": "user"}
                    return f(*args, **kwargs)
                except jwt.ExpiredSignatureError:
                    return jsonify({"status": "session_expired", "message": "12-hour session expired. Please log in again."}), 401
                except jwt.InvalidTokenError:
                    return jsonify({"status": "unauthorized", "message": "Invalid token signature."}), 401

            # --- CASE B: ANONYMOUS GUEST (THE 3-TRIAL GUARDRAIL) ---
            else:
                client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

                # Query historical usage count from PostgreSQL
                trial_count = db.session.query(AnonymousTrialLog).filter(
                    AnonymousTrialLog.ip_address == client_ip
                ).count()

                # CRITICAL BARRIER: If they hit 3, block access completely
                if trial_count >= 3:
                    return jsonify({
                        "status": "registration_required",
                        "message": "You have exhausted your 3 free public guest trials. Please register or log in to continue."
                    }), 403

                # Set guest execution context
                g.current_identity = {"user_id": None, "role": "guest", "ip": client_ip}
                return f(*args, **kwargs)

        return decorated_function
    return decorator