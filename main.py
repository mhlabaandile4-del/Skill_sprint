import lib as lib
import streamlit as st
import pandas as pd
import re
from ai import get_project_idea
from auth import create_jwt_token, verify_jwt_token, is_token_valid
import alumni
import admin

st.set_page_config(page_title="SkillSprint", page_icon="⚡", layout="wide")

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(circle at top left, #0d1420 0%, #05070c 60%); color: #e5e7eb; }
    section[data-testid="stSidebar"] { background: #0a0e17; border-right: 1px solid rgba(0,255,163,0.25); box-shadow: 4px 0 20px rgba(0,255,163,0.06); }
    section[data-testid="stSidebar"] * { color: #cbd5e1; }
    h1, h2, h3 { color: #f1f5f9 !important; font-weight: 800 !important; text-shadow: 0 0 12px rgba(0,255,163,0.25); }
    .brand-title { font-family: 'Orbitron', sans-serif; font-size: 38px; font-weight: 800; letter-spacing: 2px; background: linear-gradient(90deg, #00ffa3, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .brand-tagline { color: #64748b; font-size: 12px; letter-spacing: 3px; margin-top: -4px; text-transform: uppercase; }
    .ss-divider { height: 2px; width: 100%; margin: 14px 0 28px 0; background: linear-gradient(90deg, #00ffa3, #3b82f6 40%, #8b5cf6 70%, transparent); box-shadow: 0 0 12px rgba(0,255,163,0.6), 0 0 24px rgba(59,130,246,0.3); }
    .stButton > button, .stFormSubmitButton > button { background: linear-gradient(90deg, #00ffa3, #3b82f6); color: #05070c; border: none; border-radius: 10px; padding: 0.55em 1.4em; font-weight: 700; transition: all 0.3s ease; }
    .stButton > button:hover, .stFormSubmitButton > button:hover { transform: translateY(-1px); box-shadow: 0 0 22px rgba(0,255,163,0.7); }
    .stTextInput input, .stTextArea textarea, .stNumberInput input { background: #0f1520 !important; color: #e5e7eb !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color: #00ffa3 !important; box-shadow: 0 0 10px rgba(0,255,163,0.5) !important; }
    .stRadio > div { gap: 8px; }
    .stRadio > div > label { background: #0d1320; border: 1px solid rgba(0,255,163,0.25); border-radius: 10px; padding: 8px 18px; margin-right: 6px; }
    div[data-testid="stForm"] { background: #0d1320; border: 1px solid rgba(0,255,163,0.2); border-radius: 16px; padding: 24px; box-shadow: 0 0 20px rgba(0,255,163,0.05); }
    .ss-card { background: linear-gradient(160deg, #1a1030 0%, #10152a 100%); border: 1px solid rgba(139,92,246,0.6); border-radius: 16px; padding: 20px; box-shadow: 0 0 30px rgba(139,92,246,0.35); }
    .ss-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; background: rgba(0,255,163,0.15); color: #00ffa3; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; box-shadow: 0 0 8px rgba(0,255,163,0.3); }
    </style>
    """, unsafe_allow_html=True)

def render_topbar():
    st.markdown(
        '<div class="brand-title">⚡ SKILLSPRINT</div>'
        '<div class="brand-tagline">BUILD · SUBMIT · COMPETE</div>'
        '<div class="ss-divider"></div>',
        unsafe_allow_html=True
    )

def render_leaderboard(all_students):
    st.markdown('<h2 style="font-family:Orbitron, sans-serif;">🏆 LEADERBOARD</h2>', unsafe_allow_html=True)
    st.caption("Click any player to view their full profile")

    if not all_students:
        st.info("The database is currently empty")
        return

    df = pd.DataFrame(list(all_students.values()))
    df = df.rename(columns={"username": "student_name", "rank": "score"})
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    other_cols = [column for column in df.columns if column not in ["Rank", "student_name", "score"]]
    max_score = int(df["score"].max() or 1)

    if "selected_player" not in st.session_state:
        st.session_state["selected_player"] = None
    selected_name = st.session_state["selected_player"]

    for index, row in df.iterrows():
        rank = int(row["Rank"])
        name = row["student_name"]
        score = row["score"]
        percentage = max(4, int((score / max_score) * 100))
        slug = re.sub(r"[^a-zA-Z0-9_]", "", str(name)) or f"user{index}"
        row_key = f"row_{index}_{slug}"
        badge_color = {1: "#FFD700", 2: "#E5E5E5", 3: "#E0995E"}.get(rank, "#94a3b8")
        selected = name == selected_name
        row_background = "rgba(139,92,246,0.20)" if selected else "rgba(0,255,163,0.06)"

        with st.container(key=row_key):
            rank_column, name_column, score_column = st.columns([0.8, 3, 3])
            with rank_column:
                st.markdown(f'<div style="font-family:Orbitron,sans-serif;font-weight:800;font-size:18px;color:{badge_color};padding-top:6px;">{rank}</div>', unsafe_allow_html=True)
            with name_column:
                if st.button(name, key=f"select_{row_key}", use_container_width=True):
                    st.session_state["selected_player"] = name
                    st.rerun()
            with score_column:
                st.markdown(f'<div style="padding-top:8px;color:#e5e7eb;">{score} pts <span style="color:#00ffa3;">({percentage}%)</span></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <style>
        .st-key-{row_key} {{ background: {row_background} !important; border-left: 4px solid {badge_color} !important; border-radius: 6px; padding: 8px 10px 8px 14px !important; margin-bottom: 4px; }}
        .st-key-{row_key} .stButton > button {{ background: transparent !important; border: none !important; box-shadow: none !important; color: #e5e7eb !important; font-weight: 600 !important; }}
        .st-key-{row_key} .stButton > button:hover {{ color: #00ffa3 !important; transform: none !important; box-shadow: none !important; }}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        if selected_name and selected_name in df["student_name"].values:
            user_profile = df[df["student_name"] == selected_name].iloc[0]
            st.markdown('<div class="ss-card"><span class="ss-badge">PLAYER</span>', unsafe_allow_html=True)
            st.header(str(user_profile["student_name"]))
            st.subheader(f"Rank {int(user_profile['Rank'])} ({user_profile['score']} pts)")
            st.divider()
            for key in other_cols:
                st.write(f"{key.replace('_', ' ').title()}: {user_profile[key]}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.header("Profile viewer")
            st.info("Click a player on the leaderboard to see their full profile")

inject_css()
render_topbar()

# Initialize session state
if "project_idea" not in st.session_state:
    st.session_state["project_idea"] = None
if "project_idea_loading" not in st.session_state:
    st.session_state["project_idea_loading"] = False
if "successful_log_sign" not in st.session_state:
    st.session_state["successful_log_sign"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None

def ensure_project_idea():
    if st.session_state.get("project_idea") is not None:
        return

    if st.session_state.get("project_idea_loading"):
        st.info("Generating your project idea, please wait...")
        return

    st.session_state["project_idea_loading"] = True
    try:
        with st.spinner("Generating your project idea..."):
            st.session_state["project_idea"] = get_project_idea()
    finally:
        st.session_state["project_idea_loading"] = False

# PROFESSIONAL LOGIN/SIGNUP MODAL
def sign_up_login_modal():
    """Professional login/signup modal with forgot password and bot detection"""
    successful_log_sign = False
    ensure_project_idea()
    
    # Professional CSS styling
    st.markdown("""
    <style>
    .auth-container {
        max-width: 450px;
        margin: 50px auto;
        background: linear-gradient(160deg, #1a1030 0%, #10152a 100%);
        border: 1px solid rgba(0,255,163,0.3);
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 0 40px rgba(0,255,163,0.2);
    }
    .auth-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .auth-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(90deg, #00ffa3, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .auth-subtitle {
        color: #64748b;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .form-group {
        margin-bottom: 20px;
    }
    .form-label {
        color: #cbd5e1;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 8px;
        display: block;
    }
    .form-input {
        width: 100%;
        padding: 12px 14px;
        background: #0f1520 !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px;
        font-size: 14px;
    }
    .form-input:focus {
        border-color: #00ffa3 !important;
        box-shadow: 0 0 10px rgba(0,255,163,0.5) !important;
    }
    .btn-primary {
        width: 100%;
        padding: 12px;
        background: linear-gradient(90deg, #00ffa3, #3b82f6);
        color: #05070c;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 15px;
        cursor: pointer;
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,255,163,0.4);
    }
    .form-divider {
        text-align: center;
        margin: 20px 0;
        color: #64748b;
        font-size: 13px;
    }
    .form-link {
        color: #00ffa3;
        text-decoration: none;
        font-weight: 600;
        cursor: pointer;
    }
    .form-link:hover {
        text-decoration: underline;
    }
    .toggle-form {
        text-align: center;
        margin-top: 20px;
        color: #cbd5e1;
        font-size: 14px;
    }
    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border-left: 3px solid #ef4444;
        color: #fecaca;
        padding: 10px 12px;
        border-radius: 4px;
        font-size: 13px;
        margin-bottom: 15px;
    }
    .success-message {
        background: rgba(34, 197, 94, 0.1);
        border-left: 3px solid #22c55e;
        color: #86efac;
        padding: 10px 12px;
        border-radius: 4px;
        font-size: 13px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for form tracking
    if "auth_form_type" not in st.session_state:
        st.session_state["auth_form_type"] = "login"
    
    # Center the container
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown(
            '<div class="auth-header">'
            '<div class="auth-title">⚡ SKILLSPRINT</div>'
            '<div class="auth-subtitle">BUILD · SUBMIT · COMPETE</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # FORGOT PASSWORD FLOW
        if st.session_state["auth_form_type"] == "forgot_password":
            st.markdown('<h3 style="text-align: center; color: #cbd5e1;">Reset Password</h3>', unsafe_allow_html=True)
            
            reset_email = st.text_input("Enter your email address", placeholder="you@example.com")
            
            col_reset_a, col_reset_b = st.columns(2)
            
            with col_reset_a:
                if st.button("Send Reset Link", use_container_width=True):
                    if not reset_email:
                        st.error("Please enter your email")
                    else:
                        try:
                            from password_reset import generate_reset_token, send_reset_email
                            token = generate_reset_token(reset_email)
                            if send_reset_email(reset_email, token):
                                st.success("✅ Password reset link sent! Check your email.")
                                st.session_state["auth_form_type"] = "login"
                            else:
                                st.error("❌ Failed to send reset email")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            with col_reset_b:
                if st.button("Back to Login", use_container_width=True):
                    st.session_state["auth_form_type"] = "login"
                    st.rerun()
        
        # SIGNUP FLOW
        elif st.session_state["auth_form_type"] == "signup":
            st.markdown('<h3 style="text-align: center; color: #cbd5e1;">Create Account</h3>', unsafe_allow_html=True)
            
            with st.form("sign_up", clear_on_submit=False):
                st.markdown('<label class="form-label">Username</label>', unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Your username (5+ chars)", label_visibility="collapsed")
                
                st.markdown('<label class="form-label">Email</label>', unsafe_allow_html=True)
                email = st.text_input("Email", placeholder="you@example.com", label_visibility="collapsed")
                
                st.markdown('<label class="form-label">Password</label>', unsafe_allow_html=True)
                password = st.text_input("Password", type="password", placeholder="Min 8 chars, 1 uppercase, 1 digit", label_visibility="collapsed")
                
                st.markdown('<label class="form-label">Confirm Password</label>', unsafe_allow_html=True)
                confirm_password = st.text_input("Confirm Password", type="password", label_visibility="collapsed")
                
                st.markdown('<label class="form-label">Campus</label>', unsafe_allow_html=True)
                campus = st.selectbox("Campus", options=("Newtown", "Brynston", "Umhlanga"), label_visibility="collapsed")
                
                st.markdown('<label class="form-label">About You</label>', unsafe_allow_html=True)
                short_bio = st.text_area("Tell us about yourself", max_chars=100, label_visibility="collapsed")
                
                st.markdown('<label class="form-label">Student Repository Link</label>', unsafe_allow_html=True)
                student_repo_link = st.text_input("GitHub/GitLab repository link", label_visibility="collapsed")
                
                st.markdown('<label class="form-label">Role</label>', unsafe_allow_html=True)
                user_role = st.selectbox("Select your role", options=("Student", "Lecturer", "Alumni", "Admin"), label_visibility="collapsed")
                
                form_valid = False
                if st.form_submit_button("Create Account", use_container_width=True):
                    errors = []
                    
                    # Validation
                    if not username or username == "":
                        errors.append("Username is required")
                    elif len(username) < 5:
                        errors.append("Username must be at least 5 characters")
                    elif any(cha.isdigit() for cha in username):
                        errors.append("Username cannot contain numbers")
                    
                    if not email:
                        errors.append("Email is required")
                    else:
                        from auth import validate_email_format
                        if not validate_email_format(email):
                            errors.append("Invalid email format")
                    
                    if not password:
                        errors.append("Password is required")
                    else:
                        from auth import validate_password_strength
                        is_strong, msg = validate_password_strength(password)
                        if not is_strong:
                            errors.append(msg)
                    
                    if password != confirm_password:
                        errors.append("Passwords do not match")
                    
                    if not short_bio:
                        errors.append("Please tell us about yourself")
                    
                    if user_role == "Student" and not student_repo_link:
                        errors.append("Repository link is required for students")
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        try:
                            # Create user
                            New_user = lib.Student(username, campus, email, password, short_bio, student_repo_link, 0, user_role)
                            auth_user = lib.auth.create_user_with_email_and_password(email, password)
                            user_id = auth_user["localId"]
                            
                            # Store in database
                            lib.db.child("user").child(user_id).set({
                                "username": username,
                                "campus": campus,
                                "email": email,
                                "short_bio": short_bio,
                                "student_repo_link": student_repo_link,
                                "rank": 0,
                                "role": user_role
                            })
                            
                            jwt_token = create_jwt_token(user_id, email, user_role)
                            st.session_state['user'] = auth_user
                            st.session_state['user_role'] = user_role
                            st.session_state['jwt_token'] = jwt_token
                            st.session_state['successful_log_sign'] = True
                            st.success("✅ Account created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Signup failed: {str(e)}")
            
            if st.button("Back to Login", use_container_width=True, key="back_to_login_signup"):
                st.session_state["auth_form_type"] = "login"
                st.rerun()
        
        # LOGIN FLOW (DEFAULT)
        else:
            st.markdown('<h3 style="text-align: center; color: #cbd5e1;">Welcome Back</h3>', unsafe_allow_html=True)
            
            with st.form("login"):
                st.markdown('<label class="form-label">Email</label>', unsafe_allow_html=True)
                email = st.text_input("Email", placeholder="you@example.com", label_visibility="collapsed")
                
                st.markdown('<label class="form-label">Password</label>', unsafe_allow_html=True)
                password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if not email or not password:
                        st.error("❌ Please enter email and password")
                    else:
                        try:
                            user = lib.auth.sign_in_with_email_and_password(email, password)
                            user_id = user["localId"]
                            user_data = lib.db.child("user").child(user_id).get().val()
                            
                            if user_data:
                                user_role = user_data.get("role", "Student")
                                jwt_token = create_jwt_token(user_id, email, user_role)
                                
                                st.session_state['successful_log_sign'] = True
                                st.session_state['user'] = user
                                st.session_state['user_role'] = user_role
                                st.session_state['jwt_token'] = jwt_token
                                st.success("✅ Login successful!")
                                st.rerun()
                            else:
                                st.error("❌ User data not found")
                        except Exception as e:
                            st.error("❌ Invalid email or password")
            
            # Forgot password and signup links
            col_forgot, col_signup = st.columns(2)
            with col_forgot:
                if st.button("🔑 Forgot Password?", use_container_width=True):
                    st.session_state["auth_form_type"] = "forgot_password"
                    st.rerun()
            
            with col_signup:
                if st.button("📝 Create Account", use_container_width=True):
                    st.session_state["auth_form_type"] = "signup"
                    st.rerun()

# STUDENT PAGE
def Student_page(Current_user):
    user_data = lib.db.child("user").child(Current_user["localId"]).get().val()
    
    name = user_data["username"]
    email = user_data["email"]
    campus = user_data["campus"]
    rank = user_data["rank"]
    short_bio = user_data["short_bio"]
    repo_link = user_data["student_repo_link"]
    
    all_users = lib.db.child("user").get().val() or {}
    all_students = {k: v for k, v in all_users.items() if v.get("role") == "Student"}
    
    st.title(f"Welcome, {name}! 🎓")
    
    ensure_project_idea()
    if st.session_state.get("project_idea") is not None:
        st.header("📋 This Week's Challenge")
        st.info(st.session_state["project_idea"])
    
    with st.form("update_repository"):
        updated_repo_link = st.text_input("Student repository link", value=repo_link)
        if st.form_submit_button("Save repository link"):
            if not updated_repo_link.strip():
                st.error("Repository link cannot be empty")
            else:
                lib.db.child("user").child(Current_user["localId"]).update({
                    "student_repo_link": updated_repo_link.strip()
                })
                st.success("✅ Repository link updated")
                st.rerun()
    
    render_leaderboard(all_students)
    
    # Logout button
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.success("Logged out successfully!")
            st.rerun()

# LECTURER PAGE
def Lecturer_page(Current_user):
    user_data = lib.db.child("user").child(Current_user["localId"]).get().val()
    
    name = user_data["username"]
    email = user_data["email"]
    campus = user_data["campus"]
    
    all_users = lib.db.child("user").get().val() or {}
    all_students = {k: v for k, v in all_users.items() if v.get("role") == "Student"}
    
    st.title(f"Welcome, {name}! 👨‍🏫")
    
    st.header("Student Management")
    
    if all_students:
        student_ids = list(all_students.keys())
        selected_student_id = st.selectbox(
            "Select Student",
            student_ids,
            format_func=lambda student_id: all_students[student_id].get("username", student_id)
        )
        selected_student = all_students[selected_student_id]
        
        with st.form("update_student_rank"):
            updated_rank = st.number_input(
                "Rank score",
                min_value=0,
                value=int(selected_student.get("rank", 0)),
                step=1
            )
            if st.form_submit_button("Save student rank"):
                lib.db.child("user").child(selected_student_id).update({
                    "rank": int(updated_rank)
                })
                st.success("✅ Student rank updated")
                st.rerun()
    
    render_leaderboard(all_students)
    
    # Logout button
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.success("Logged out successfully!")
            st.rerun()

# ALUMNI PAGE
def Alumni_page(Current_user):
    user_data = lib.db.child("user").child(Current_user["localId"]).get().val()
    name = user_data["username"]
    
    st.title(f"Welcome back, {name}! 🎓")
    
    # Alumni reviews section
    alumni.render_alumni_section(Current_user)
    
    # Logout button
    with st.sidebar:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.success("Logged out successfully!")
            st.rerun()

# PAGE NAVIGATION LOGIC
if not st.session_state["successful_log_sign"] or st.session_state["user"] is None:
    sign_up_login_modal()
elif st.session_state["user_role"] == "Admin":
    admin.render_admin_dashboard(st.session_state["user"])
elif st.session_state["user_role"] == "Student":
    Student_page(st.session_state["user"])
elif st.session_state["user_role"] == "Lecturer":
    Lecturer_page(st.session_state["user"])
elif st.session_state["user_role"] == "Alumni":
    Alumni_page(st.session_state["user"])