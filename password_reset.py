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
    .password-strength {
        height: 4px;
        background: #0f1520;
        border-radius: 2px;
        margin-top: 6px;
        overflow: hidden;
    }
    .password-strength-bar {
        height: 100%;
        width: 0%;
        transition: width 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for form tracking
    if "auth_form_type" not in st.session_state:
        st.session_state["auth_form_type"] = "login"  # login, signup, forgot_password
    
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
                
                # Turnstile CAPTCHA
                from turnstile import get_turnstile_widget_html
                st.markdown(get_turnstile_widget_html(), unsafe_allow_html=True)
                
                turnstile_token = st.text_input("Turnstile Token (for verification)", type="password", label_visibility="collapsed", help="This is auto-filled by Cloudflare")
                
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
                            # Verify Turnstile token
                            if turnstile_token:
                                from turnstile import verify_turnstile_token
                                if not verify_turnstile_token(turnstile_token):
                                    st.error("❌ Bot detection failed. Please try again.")
                            
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
            
            st.markdown(
                '<div class="toggle-form">Already have an account? '
                '<span class="form-link" onclick="document.querySelector(\'button[aria-label="Back to Login"]\').click()">Login here</span></div>',
                unsafe_allow_html=True
            )
            
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
                
                # Turnstile CAPTCHA
                from turnstile import get_turnstile_widget_html
                st.markdown(get_turnstile_widget_html(), unsafe_allow_html=True)
                
                turnstile_token = st.text_input("Turnstile Token (for verification)", type="password", label_visibility="collapsed", help="This is auto-filled by Cloudflare")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if not email or not password:
                        st.error("❌ Please enter email and password")
                    else:
                        try:
                            # Verify Turnstile token
                            if turnstile_token:
                                from turnstile import verify_turnstile_token
                                if not verify_turnstile_token(turnstile_token):
                                    st.error("❌ Bot detection failed. Please try again.")
                            
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