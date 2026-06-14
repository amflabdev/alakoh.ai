from flask import Blueprint, jsonify, request, g
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone

# Import configurations and the shared database layout context
from config.settings import settings
from config.database import db, User, AnonymousTrialLog
from app.shared.middlewares import application_tier_gatekeeper

# Official Google GenAI SDK imports
from google import genai
from google.genai import types

# 1. Initialize the central Gemini client node utilizing your environment settings key
gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# FIXED: Removed duplicate 'auth_bp = Blueprint(...)' initialization line to prevent registry overwrites
auth_bp = Blueprint('auth', __name__)


# =====================================================================
# FUNCTION CALLING (TOOLS DIRECTORY SECTION)
# =====================================================================
def get_advisor_career_directory(role_name: str) -> str:
    """
    Retrieves precise strategy details, prerequisites, and operational parameters for a specific advisor career path.
    Use this tool whenever a user asks questions regarding corporate advisory roles, consulting paths, or industry licensing requirements.
    
    Args:
        role_name: The string name of the career trajectory (e.g., 'financial advisor', 'ai consultant')
    """
    # Normalized sample career dictionary blueprint dataset
    career_database = {
        "financial advisor": "Requires Series 65 or 66 regulatory licensure. Key path focuses: private wealth strategy and portfolio balancing.",
        "ai consultant": "Requires systems optimization, cloud computing architecture validation, and LLM orchestration. Key path focus: enterprise scale digital transformation.",
        "career coach": "Requires international coaching federation (ICF) training footprints. Key path focus: talent optimization and human resource scaling mechanics."
    }
    
    normalized_input = str(role_name).lower().strip()
    return career_database.get(
        normalized_input, 
        f"The requested role '{role_name}' is not indexed inside our local advisory pathway directory framework."
    )


# =====================================================================
# CORE API BLUEPRINT ROUTES
# =====================================================================

@auth_bp.route('/ask-advisor', methods=['POST'])
@application_tier_gatekeeper()
def ask_advisor():
    request_data = request.get_json(silent=True) or {}
    prompt = request_data.get("prompt")
    
    if not prompt:
        return jsonify({"status": "error", "message": "The text prompt field context payload cannot be empty."}), 400
    
    try:
        # 2. Call the Gemini API. Passing our local Python function directly inside 
        # the config tools list allows the SDK to completely handle the function execution loops automatically!
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash', # Recommended lightweight model for real-time tool orchestration
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[get_advisor_career_directory],
                temperature=0.3 # Kept low to ensure factual directory retrieval behaviors
            )
        )
        
        # Pull the finalized processed text data output
        ai_response = response.text
        
        # 3. LOG GUEST CONSUMPTION ONLY AFTER SUCCESSFUL AI GENERATION
        if g.current_identity.get("role") == "guest":
            guest_ip = g.current_identity["ip"]
            
            new_log = AnonymousTrialLog(ip_address=guest_ip)
            db.session.add(new_log)
            db.session.commit()
            
        return jsonify({
            "status": "success",
            "data": ai_response
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Cognitive Engine Failure: {str(e)}"
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """Constructs a clean, unique profile inside the PostgreSQL database."""
    request_data = request.get_json(silent=True) or {}
    username = request_data.get("username", "").strip()
    email = request_data.get("email", "").strip()
    password = request_data.get("password", "").strip()

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "All verification parameters are required."}), 400

    # Safety Barrier: Prevent overlapping username registrations
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        return jsonify({"status": "error", "message": "Identity collision: Username or Email is already registered."}), 409

    try:
        # Securely hash the password before saving to the database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_account = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role="user"
        )
        
        db.session.add(new_account)
        db.session.commit()
        return jsonify({"status": "success", "message": "Profile created successfully."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Database write failure: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticates credentials and dispenses an automatic 12-hour expiration JWT."""
    request_data = request.get_json(silent=True) or {}
    username = request_data.get("username", "").strip()
    password = request_data.get("password", "").strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Credentials cannot be empty values."}), 400

    # Query the database for the user identity record
    target_user = User.query.filter_by(username=username).first()

    # Compare the decrypted input password with the database hash representation safely
    if not target_user or not check_password_hash(target_user.password_hash, password):
        return jsonify({"status": "error", "message": "Access Denied: Invalid username or password matching pattern."}), 401

    # Generate a secure JWT token that naturally expires after half a day (12 hours)
    expiration_window = datetime.now(timezone.utc) + timedelta(hours=12)
    token_payload = {
        "user_id": target_user.id,
        "user_name": target_user.username,
        "role": target_user.role,
        "exp": expiration_window
    }
    
    generated_token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm="HS256")

    return jsonify({
        "status": "success",
        "message": "Authentication successful.",
        "token": generated_token
    }), 200