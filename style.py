import lib as lib
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="SkillSprint", page_icon="⚡", layout="wide")

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: radial-gradient(circle at top left, #0d1420 0%, #05070c 60%);
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background: #0a0e17;
        border-right: 1px solid rgba(0,255,163,0.25);
        box-shadow: 4px 0 20px rgba(0,255,163,0.06);
    }
    section[data-testid="stSidebar"] * { color: #cbd5e1; }

    h1, h2, h3 {
        color: #f1f5f9 !important;
        font-weight: 800 !important;
        text-shadow: 0 0 12px rgba(0,255,163,0.25);
    }

    .brand-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 38px; font-weight: 800; letter-spacing: 2px;
        background: linear-gradient(90deg, #00ffa3, #3b82f6, #8b5cf6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block;
        filter: drop-shadow(0 0 14px rgba(0,255,163,0.45));
    }
    .brand-tagline {
        color: #64748b; font-size: 12px; letter-spacing: 3px;
        margin-top: -4px; text-transform: uppercase;
    }

    .ss-divider {
        height: 2px; width: 100%; margin: 14px 0 28px 0;
        background: linear-gradient(90deg, #00ffa3, #3b82f6 40%, #8b5cf6 70%, transparent);
        box-shadow: 0 0 12px rgba(0,255,163,0.6), 0 0 24px rgba(59,130,246,0.4);
        border-radius: 2px;
    }

    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(90deg, #00ffa3, #3b82f6);
        color: #05070c; border: none; border-radius: 10px;
        padding: 0.55em 1.4em; font-weight: 700;
        box-shadow: 0 0 10px rgba(0,255,163,0.3);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 0 22px rgba(0,255,163,0.7);
    }

    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: #0f1520 !important; color: #e5e7eb !important;
        border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00ffa3 !important;
        box-shadow: 0 0 10px rgba(0,255,163,0.5) !important;
    }

    .stRadio > div { gap: 8px; }
    .stRadio > div > label {
        background: #0d1320;
        border: 1px solid rgba(0,255,163,0.25);
        border-radius: 10px;
        padding: 8px 18px;
        margin-right: 6px;
    }

    div[data-testid="stForm"] {
        background: #0d1320;
        border: 1px solid rgba(0,255,163,0.2);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 0 20px rgba(0,255,163,0.05);
    }

    /* ============ CUSTOM NEON LEADERBOARD (replaces st.dataframe) ============ */
    .lb-container {
        background: #0a0e17;
        border: 1px solid rgba(0,255,163,0.3);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 0 30px rgba(0,255,163,0.1);
        margin-bottom: 24px;
    }
    .lb-header, .lb-row {
        display: flex; align-items: center;
        padding: 14px 22px;
    }
    .lb-header {
        background: #0d1420;
        font-family: 'Orbitron', sans-serif;
        color: #00ffa3;
        letter-spacing: 1.5px;
        font-size: 13px;
        border-bottom: 1px solid rgba(0,255,163,0.2);
    }
    .lb-row {
        text-decoration: none !important;
        color: #e5e7eb !important;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        transition: all 0.15s ease;
        cursor: pointer;
    }
    .lb-row:hover {
        background: rgba(0,255,163,0.08);
        transform: translateX(4px);
    }
    .lb-rank { width: 70px; font-family:'Orbitron', sans-serif; font-weight:800; font-size:18px; }
    .lb-player { flex: 1; font-weight: 600; font-size: 15px; }
    .lb-score-wrap { width: 280px; display: flex; align-items: center; gap: 12px; }
    .lb-bar-track { flex: 1; height: 8px; border-radius: 6px; background: rgba(255,255,255,0.08); overflow: hidden; }
    .lb-bar-fill {
        height: 100%; border-radius: 6px;
        background: linear-gradient(90deg, #00ffa3, #3b82f6);
        box-shadow: 0 0 10px rgba(0,255,163,0.6);
    }
    .lb-score-num { width: 40px; text-align: right; font-weight: 700; }

    .rank-gold { background: linear-gradient(90deg, rgba(255,215,0,0.14), transparent); border-left: 4px solid #FFD700; }
    .rank-gold .lb-rank { color: #FFD700; text-shadow: 0 0 10px rgba(255,215,0,0.7); }
    .rank-silver { background: linear-gradient(90deg, rgba(192,192,192,0.12), transparent); border-left: 4px solid #C0C0C0; }
    .rank-silver .lb-rank { color: #E5E5E5; text-shadow: 0 0 8px rgba(192,192,192,0.6); }
    .rank-bronze { background: linear-gradient(90deg, rgba(205,127,50,0.12), transparent); border-left: 4px solid #CD7F32; }
    .rank-bronze .lb-rank { color: #E0995E; text-shadow: 0 0 8px rgba(205,127,50,0.6); }
    .rank-default .lb-rank { color: #94a3b8; }

    .row-selected {
        background: rgba(139,92,246,0.20) !important;
        border-left: 4px solid #8b5cf6 !important;
        box-shadow: inset 0 0 20px rgba(139,92,246,0.15);
    }
    /* ============ END LEADERBOARD STYLES ============ */

    .ss-card {
        background: linear-gradient(160deg, #1a1030 0%, #10152a 100%);
        border: 1px solid rgba(139,92,246,0.6);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 30px rgba(139,92,246,0.35), inset 0 0 20px rgba(139,92,246,0.05);
    }
    .ss-badge {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        background: rgba(0,255,163,0.15); color: #00ffa3;
        font-size: 12px; font-weight: 700; letter-spacing: 0.5px;
        box-shadow: 0 0 8px rgba(0,255,163,0.4);
    }
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
    """Neon leaderboard: real st.button per row for reliable clicks,
    but restyled via container-key CSS so it looks like a flat glowing row, not a button."""
    st.markdown('<h2 style="font-family:Orbitron, sans-serif;">🏆 LEADERBOARD</h2>', unsafe_allow_html=True)
    st.caption("Click any player to view their full profile")

    if not all_students:
        st.info("The database is currently empty")
        return

    raw_data = list(all_students.values())
    df = pd.DataFrame(raw_data)
    df = df.rename(columns={"username": "student_name", "rank": "score"})
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    other_cols = [c for c in df.columns if c not in ["Rank", "student_name", "score"]]

    max_score = int(df["score"].max() or 1)

    if "selected_player" not in st.session_state:
        st.session_state["selected_player"] = None
    selected_name = st.session_state["selected_player"]

    st.markdown(
        '<div class="lb-container">'
        '<div class="lb-header">'
        '<div class="lb-rank">RANK</div>'
        '<div class="lb-player">PLAYER</div>'
        '<div class="lb-score-wrap">SCORE</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    for idx, row in df.iterrows():
        rank  = int(row["Rank"])
        name  = row["student_name"]
        score = row["score"]
        pct   = max(4, int((score / max_score) * 100)) if max_score else 4

        slug = re.sub(r'[^a-zA-Z0-9_]', '', str(name)) or f"user{idx}"
        row_key = f"row_{idx}_{slug}"
        is_selected = (name == selected_name)

        if is_selected:
            row_bg, border_color = "rgba(139,92,246,0.20)", "#8b5cf6"
        elif rank == 1:
            row_bg, border_color = "rgba(255,215,0,0.14)", "#FFD700"
        elif rank == 2:
            row_bg, border_color = "rgba(192,192,192,0.12)", "#C0C0C0"
        elif rank == 3:
            row_bg, border_color = "rgba(205,127,50,0.12)", "#CD7F32"
        else:
            row_bg, border_color = "transparent", "rgba(255,255,255,0.08)"

        badge_color = {1: "#FFD700", 2: "#E5E5E5", 3: "#E0995E"}.get(rank, "#94a3b8")

        with st.container(key=row_key):
            col_rank, col_name, col_score = st.columns([0.8, 3, 3])
            with col_rank:
                st.markdown(
                    f'<div style="font-family:Orbitron,sans-serif;font-weight:800;'
                    f'font-size:18px;color:{badge_color};padding-top:6px;">{rank}</div>',
                    unsafe_allow_html=True
                )
            with col_name:
                if st.button(name, key=f"select_{row_key}", use_container_width=True):
                    st.session_state["selected_player"] = name
                    st.rerun()
            with col_score:
                st.markdown(
                    f'<div class="lb-score-wrap">'
                    f'<div class="lb-bar-track"><div class="lb-bar-fill" style="width:{pct}%;"></div></div>'
                    f'<div class="lb-score-num">{score}</div></div>',
                    unsafe_allow_html=True
                )

        # Row-specific styling: paints the whole row and strips the button chrome
        st.markdown(f"""
        <style>
        .st-key-{row_key} {{
            background: {row_bg} !important;
            border-left: 4px solid {border_color} !important;
            border-radius: 6px;
            padding: 8px 10px 8px 14px !important;
            margin-bottom: 4px;
        }}
        .st-key-{row_key}:hover {{
            background: rgba(0,255,163,0.08) !important;
        }}
        .st-key-{row_key} .stButton > button {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #e5e7eb !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 4px 0 !important;
        }}
        .st-key-{row_key} .stButton > button:hover {{
            color: #00ffa3 !important;
            transform: none !important;
            box-shadow: none !important;
        }}
        </style>
        """, unsafe_allow_html=True)

    # Sidebar profile panel
    with st.sidebar:
        if selected_name and selected_name in df["student_name"].values:
            user_profile = df[df["student_name"] == selected_name].iloc[0]
            st.markdown('<div class="ss-card">', unsafe_allow_html=True)
            st.markdown('<span class="ss-badge">PLAYER</span>', unsafe_allow_html=True)
            st.header(f"{user_profile['student_name']}")
            st.subheader(f"Rank {int(user_profile['Rank'])} ({user_profile['score']} pts)")
            st.divider()
            st.markdown("ALL STUDENT DATA")
            for key in other_cols:
                clean_key = key.replace("_", " ").title()
                st.write(f"{clean_key}: {user_profile[key]}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.header("Profile viewer")
            st.info("Click a player on the leaderboard to see their full profile")
inject_css()
render_topbar()

#This a collaboration project, so anyone is welcome to ask for help.

if "successful_log_sign" not in st.session_state:
        st.session_state["successful_log_sign"] = False
if "user" not in st.session_state:
        st.session_state["user"] = None
if "user_role" not in st.session_state:
        st.session_state["user_role"] = None


         

#SIGN_UP/LOGIN MODAL
def sign_up_login_modal():
    successful_log_sign = False #If true, the main page will be displayed with some user information
    st.title("SkillSprint") #STYLING

    lgnorsgn  = st.radio("New here ?", options = ("Yes", "No"),
    horizontal=True,
    label_visibility="collapsed")
    if lgnorsgn == "Yes":
        #SIGNUP MODAL
        st.subheader("Sign up")
        sgn_form   = st.form("sign up")
        username  = sgn_form.text_input("Username :")
        email     = sgn_form.text_input("Email :")
        password  = sgn_form.text_input("Password :", type="password")
        confirm_password  = sgn_form.text_input("Confirm password :", type="password")
        campus    = sgn_form.radio("What campus are you from : ", options= ("Newtown","Brynston","Umhlanga"))
        short_bio = sgn_form.text_area("Tell us about yourself", max_chars= 100)
        student_repo_link = sgn_form.text_input("Link to your student repository :")
        student_or_lecturer = sgn_form.radio("Are you a student or a lecturer ?", options= ("Student","Lecturer"))
        #Simple form validation
        form_valid = False
        if sgn_form.form_submit_button("Submit"):
                if username == "":
                        st.warning("Please enter name")
                        form_valid = False
                elif any(cha.isdigit() for cha in username):
                        st.warning("Username cannot contain numbers")
                        form_valid = False
                elif len(username) < 5:
                        st.warning("Username must be at least 5 characters long")
                        form_valid = False
                elif email == "":
                        st.warning("Please enter email")
                        form_valid = False
                elif password == "":
                        st.warning("Please enter password")
                        form_valid = False
                elif len(password) < 8:
                        st.warning("Password must be at least 8 characters long")
                        form_valid = False
                elif password != confirm_password:
                        st.warning("Passwords do not match")
                        form_valid = False
                if short_bio == "":
                        st.warning("Please enter a short bio")
                        form_valid = False
                if student_repo_link == "":
                        st.warning("Please enter a link to your student repository")
                        form_valid = False
                else:
                        form_valid = True
                        st.success("Form submitted successfully")      
                        st.success("User created successfully")
                        st.info("Please login to continue")
                        st.session_state['successful_log_sign'] = True
                #Simple form validation
                #Adds account to firebase, creates user object, and store user information in firebase database and loads main page   
                if form_valid:
                        New_user = lib.Student(username, campus, email, password, short_bio, student_repo_link, 0, student_or_lecturer)
                        auth_user = lib.auth.create_user_with_email_and_password(email, password)
                        user_id = auth_user["localId"]
                        lib.db.child("user").child(user_id).set( {"username": username, "campus": campus, "email": email, "short_bio": short_bio, "student_repo_link": student_repo_link, "rank": 0, "role": student_or_lecturer})
                        st.session_state['user'] = auth_user
                        st.session_state['user_role'] = student_or_lecturer
    #LOGIN MODAL              
    else:
                st.subheader("Login")
                lg_form   = st.form("login")
                email  = lg_form.text_input("Email :")
                password  = lg_form.text_input("Password :", type="password")
                #Check if user exists in firebase database and validate password, if valid load main page, else show error message
                if lg_form.form_submit_button("Submit"):
                        try:
                                user = lib.auth.sign_in_with_email_and_password(email, password)
                                st.session_state['successful_log_sign'] = True
                                st.success("Login successful")
                                st.session_state['user'] = user
                                successful_log_sign = True
                                #Check if user is a student or lecturer and load the appropriate page
                                user_id = user["localId"]
                                user_data = lib.db.child("user").child(user_id).get().val()
                                if user_data:
                                        st.session_state["user_role"] = user_data.get("role")
                        except:
                                st.error("Invalid username or password")
    #LOGIN MODAL 
#SIGN_UP/LOGIN MODAL
#STUDENT PAGE
def Student_page(Current_user):
         
        user_data = lib.db.child("user").child(Current_user["localId"]).get().val()
        print("ON STUDENT PAGE")

        #User information
        name      = user_data["username"]
        email     = user_data["email"]
        campus    = user_data["campus"]
        rank      = user_data["rank"]
        short_bio = user_data["short_bio"]
        repo_link = user_data["student_repo_link"]
        #User information
        #Database information
        all_users    = lib.db.child("user").get().val() or {}
        all_students = {k: v for k, v in all_users.items() if v.get("role") == "Student"}
        #Database iformation
        st.title(f"Welcome, {name}!")

        render_leaderboard(all_students)
#STUDENT PAGE

#LECTURER PAGE
def Lecturer_page(Current_user):
      user_data = lib.db.child("user").child(Current_user["localId"]).get().val()
      print("ON LECTURER PAGE")

      #User information
      name      = user_data["username"]
      email     = user_data["email"]
      campus    = user_data["campus"]
      rank      = user_data["rank"]
      short_bio = user_data["short_bio"]
      repo_link = user_data["student_repo_link"]
      #User information
      st.title(f"Welcome, {name}!")

      all_students = lib.db.child("user").get().val()
      render_leaderboard(all_students)
      #END OF lEADERBOARD


#LECTURER PAGE

#PAGE NAVIGATION LOGIC
if not st.session_state["successful_log_sign"] or st.session_state["user"] is None:
        sign_up_login_modal()
elif st.session_state["user_role"] == "Student":
        Student_page(st.session_state["user"])
elif st.session_state["user_role"] == "Lecturer":
        Lecturer_page(st.session_state["user"])
#PAGE NAVIGATION LOGIC
