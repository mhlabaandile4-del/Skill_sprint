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
    .brand-title { font-family: 'Orbitron', sans-serif; font-size: 38px; font-weight: 800; letter-spacing: 2px; background: linear-gradient(90deg, #00ffa3, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; filter: drop-shadow(0 0 14px rgba(0,255,163,0.45)); }
    .brand-tagline { color: #64748b; font-size: 12px; letter-spacing: 3px; margin-top: -4px; text-transform: uppercase; }
    .ss-divider { height: 2px; width: 100%; margin: 14px 0 28px 0; background: linear-gradient(90deg, #00ffa3, #3b82f6 40%, #8b5cf6 70%, transparent); box-shadow: 0 0 12px rgba(0,255,163,0.6), 0 0 24px rgba(59,130,246,0.4); border-radius: 2px; }
    .stButton > button, .stFormSubmitButton > button { background: linear-gradient(90deg, #00ffa3, #3b82f6); color: #05070c; border: none; border-radius: 10px; padding: 0.55em 1.4em; font-weight: 700; box-shadow: 0 0 10px rgba(0,255,163,0.3); transition: transform 0.15s ease, box-shadow 0.15s ease; }
    .stButton > button:hover, .stFormSubmitButton > button:hover { transform: translateY(-1px); box-shadow: 0 0 22px rgba(0,255,163,0.7); }
    .stTextInput input, .stTextArea textarea, .stNumberInput input { background: #0f1520 !important; color: #e5e7eb !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color: #00ffa3 !important; box-shadow: 0 0 10px rgba(0,255,163,0.5) !important; }
    .stRadio > div { gap: 8px; }
    .stRadio > div > label { background: #0d1320; border: 1px solid rgba(0,255,163,0.25); border-radius: 10px; padding: 8px 18px; margin-right: 6px; }
    div[data-testid="stForm"] { background: #0d1320; border: 1px solid rgba(0,255,163,0.2); border-radius: 16px; padding: 24px; box-shadow: 0 0 20px rgba(0,255,163,0.05); }
    .ss-card { background: linear-gradient(160deg, #1a1030 0%, #10152a 100%); border: 1px solid rgba(139,92,246,0.6); border-radius: 16px; padding: 20px; box-shadow: 0 0 30px rgba(139,92,246,0.35), inset 0 0 20px rgba(139,92,246,0.05); }
    .ss-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; background: rgba(0,255,163,0.15); color: #00ffa3; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; box-shadow: 0 0 8px rgba(0,255,163,0.4); }
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

# SIGN UP / LOGIN MODAL
def sign_up_login_modal():
    successful_log_sign = False
    ensure_project_idea()
    st.title("SkillSprint")

    if st.session_state.get("project_idea_loading"):
        st.info("Generating your project idea before login...")
        st.caption("Please wait a moment while we prepare the challenge.")

    lgnorsgn = st.radio("New here?", options=("Yes", "No"))
    
    if lgnorsgn == "Yes":
        # SIGNUP
        st.subheader("Sign up")
        sgn_form = st.form("sign up")
        username = sgn_form.text_input("Username :")
        email = sgn_form.text_input("Email :")
        password = sgn_form.text_input("Password :", type="password")
        confirm_password = sgn_form.text_input("Confirm password :", type="password")
        campus = sgn_form.radio("What campus are you from:", options=("Newtown", "Brynston", "Umhlanga"))
        short_bio = sgn_form.text_area("Tell us about yourself", max_chars=100)
        student_repo_link = sgn_form.text_input("Link to your student repository :")
        user_role = sgn_form.radio("Are you a student, lecturer, alumni, or admin?", 
                                   options=("Student", "Lecturer", "Alumni", "Admin"))
        
        form_valid = False
        if sgn_form.form_submit_button("Submit"):
            if username == "":
                st.warning("Please enter name")
            elif any(cha.isdigit() for cha in username):
                st.warning("Username cannot contain numbers")
            elif len(username) < 5:
                st.warning("Username must be at least 5 characters long")
            elif email == "":
                st.warning("Please enter email")
            elif password == "":
                st.warning("Please enter password")
            elif len(password) < 8:
                st.warning("Password must be at least 8 characters long")
            elif password != confirm_password:
                st.warning("Passwords do not match")
            elif short_bio == "":
                st.warning("Please enter a short bio")
            elif student_repo_link == "" and user_role == "Student":
                st.warning("Please enter a link to your student repository")
            else:
                form_valid = True

            if form_valid:
                try:
                    New_user = lib.Student(username, campus, email, password, short_bio, 
                                          student_repo_link, 0, user_role)
                    auth_user = lib.auth.create_user_with_email_and_password(email, password)
                    user_id = auth_user["localId"]
                    
                    # Store user in database
                    lib.db.child("user").child(user_id).set({
                        "username": username,
                        "campus": campus,
                        "email": email,
                        "short_bio": short_bio,
                        "student_repo_link": student_repo_link,
                        "rank": 0,
                        "role": user_role
                    })
                    
                    # Create JWT token
                    jwt_token = create_jwt_token(user_id, email, user_role)
                    
                    st.session_state['user'] = auth_user
                    st.session_state['user_role'] = user_role
                    st.session_state['jwt_token'] = jwt_token
                    st.session_state['successful_log_sign'] = True
                    st.success("✅ User created successfully! Logging in...")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Sign up failed: {str(e)}")
    else:
        # LOGIN
        st.subheader("Login")
        lg_form = st.form("login")
        email = lg_form.text_input("Email :")
        password = lg_form.text_input("Password :", type="password")
        
        if lg_form.form_submit_button("Submit"):
            try:
                user = lib.auth.sign_in_with_email_and_password(email, password)
                user_id = user["localId"]
                user_data = lib.db.child("user").child(user_id).get().val()
                
                if user_data:
                    user_role = user_data.get("role", "Student")
                    
                    # Create JWT token
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