# app/modules/cognitive_engine/routes.py
from flask import Blueprint, jsonify, g
from app.shared.middlewares import application_tier_gatekeeper

cognitive_bp = Blueprint('cognitive', __name__)

@cognitive_bp.route('/ask-advisor', methods=['POST'])
@application_tier_gatekeeper() # Handles length, JWT validation, expiration, and trial checks all at once
def ask_advisor():
    # You can safely check WHO is calling your AI right here:
    user_role = g.current_identity.get("role")
    
    return jsonify({
        "status": "success",
        "identity_context": user_role,
        "data": "Cognitive calculation payload."
    })