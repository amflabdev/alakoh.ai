import streamlit as st
import requests

# Core REST backend API configuration network nodes
FLASK_CORE_URL = "http://127.0.0.1:5000" 
FLASK_AUTH_API = f"{FLASK_CORE_URL}/auth"
CHAT_ENGINE_API = f"{FLASK_CORE_URL}/auth/ask-advisor"

st.set_page_config(page_title="Alakoh Workspace Terminal", layout="wide")
st.title("🧙‍♂️ Alakoh Cognitive Workspace Terminal")

# --- INITIALIZE SESSION STATE REGISTRY ---
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "require_auth"  # Options: require_auth, guest, authenticated

# =====================================================================
# 🔍 CORE SECURITY CHECK FUNCTION
# =====================================================================
def check_session_status() -> str:
    """
    Evaluates the application session state to determine access privilege tiers.
    Returns: 'AUTHORIZED', 'GUEST', or 'UNAUTHORIZED'
    """
    if st.session_state.auth_token and st.session_state.view_mode == "authenticated":
        return "AUTHORIZED"
    elif st.session_state.view_mode == "guest":
        return "GUEST"
    else:
        return "UNAUTHORIZED"


# =====================================================================
# 🔐 GATEKEEPER VIEW PANEL (login.html & register.html Replacement)
# =====================================================================
current_tier = check_session_status()

if current_tier == "UNAUTHORIZED":
    st.warning("🔐 Gateway Security Barrier Active: Please authenticate or check the application workspace layout as a temporary guest.")
    
    # Guest testing facility selection column row
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("💡 Guest Access Rules: You can submit up to 3 advisor prompts per 24 hours without creating an account.")
    with col2:
        if st.button("🚀 Run System as Guest", use_container_width=True):
            st.session_state.view_mode = "guest"
            st.session_state.auth_token = None
            st.rerun()

    st.markdown("---")

    # Interactive component tabs to switch form context profiles effortlessly
    tab1, tab2 = st.tabs(["🔐 Authenticate Identity Profile", "📝 Register New System Account"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username", key="l_user").strip()
            password = st.text_input("Password", type="password", key="l_pass").strip()
            submitted = st.form_submit_button("Log In")
            
            if submitted:
                if not username or not password:
                    st.warning("Input parameter vectors cannot be left blank.")
                else:
                    try:
                        response = requests.post(f"{FLASK_AUTH_API}/login", json={"username": username, "password": password})
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.auth_token = data.get("token")
                            st.session_state.view_mode = "authenticated"
                            st.success("Identity verified! Loading terminal environment surfaces...")
                            st.rerun()
                        else:
                            st.error("Access Denied: Invalid credentials pattern matching string submitted.")
                    except requests.exceptions.ConnectionError:
                        st.error("API Connection error—Backend Flask core server is offline.")
                    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Choose Username", key="reg_user").strip()
            new_email = st.text_input("Enter Email Address", key="reg_email").strip()
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass").strip()
            registered = st.form_submit_button("Register Account")
            
            if registered:
                if not new_user or not new_email or not new_pass:
                    st.warning("All input context parameters are required for data schema insertion.")
                else:
                    try:
                        response = requests.post(f"{FLASK_AUTH_API}/register", json={"username": new_user, "email": new_email, "password": new_pass})
                        if response.status_code == 201:
                            st.success("🎉 Registration success! Toggle over to the 'Log In' tab to authenticate.")
                        else:
                            st.error("Registration denied: Chosen username or email matching pattern is already taken.")
                    except requests.exceptions.ConnectionError:
                        st.error("API Connection error—Backend Flask core server is offline.")
                            
    st.stop()  # Lock Screen Fence: Stops layout processing if current_tier is UNAUTHORIZED


# =====================================================================
# 🔮 MAIN CHAT WORKSPACE (Runs only for GUEST or AUTHORIZED tiers)
# =====================================================================

# Re-evaluate privilege status tier for accurate UI layout changes
current_tier = check_session_status()

# Build side profile utility layout boxes depending on checking logic results
with st.sidebar:
    st.markdown("### 🛠️ Workspace Session Monitor")
    
    if current_tier == "AUTHORIZED":
        st.success("🟢 Security Level: AUTHORIZED USER")
        st.caption("✨ Privileges Active: Unlimited Gemini LLM requests enabled.")
    elif current_tier == "GUEST":
        st.info("🔵 Security Level: PUBLIC GUEST TIER")
        st.caption("⚠️ Limitations Active: 3 rolling prompts per 24 hours.")
        
    st.markdown("---")
    if st.button("門 Close Session Workspace / Log Out", use_container_width=True):
        st.session_state.auth_token = None
        st.session_state.view_mode = "require_auth"
        st.rerun()

st.caption(f"Active System Subsystem Connection Signature: **{current_tier}**")
user_prompt = st.chat_input("Enter prompt inquiry to advisor (Strict 100 character boundary limits enforced):")

if user_prompt:
    cleaned_prompt = str(user_prompt).strip()
    
    if len(cleaned_prompt) > 100:
        st.error(f"Input Verification Failure: String length ({len(cleaned_prompt)}) slips outside the 100 character constraint.")
        st.stop()

    headers = {}
    if st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"

    with st.spinner("Invoking Gemini Agent Compute Matrix loops..."):
        try:
            response = requests.post(CHAT_ENGINE_API, json={"prompt": cleaned_prompt}, headers=headers)
            
            # Catch guest tier limitations boundary exhaustion (3 daily tokens used up)
            if response.status_code == 403:
                st.session_state.view_mode = "require_auth"
                st.rerun()
            
            # Catch expired 12-hour active signature authentication session windows
            elif response.status_code == 401:
                st.session_state.auth_token = None
                st.session_state.view_mode = "require_auth"
                st.rerun()
                
            elif response.status_code == 200:
                result_payload = response.json()
                st.markdown(f"### 🔮 AI Advisor Response:\n{result_payload.get('data', 'Empty response payload structure details.')}")
            else:
                try:
                    error_msg = response.json().get("message", "Unknown execution calculation fault.")
                except Exception:
                    error_msg = response.text if response.text else "Raw gateway exception trace dropped."
                st.error(f"API Backend Error [{response.status_code}]: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            st.error("Sync Failure: Gateway connection broken. Check your core background terminal processes.")