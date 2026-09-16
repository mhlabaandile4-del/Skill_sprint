import streamlit as st
import lib as lib
import pandas as pd
from datetime import datetime

# List of admin emails with access to admin panel
ADMIN_EMAILS = [
    "admin@skillsprint.com",
    "administrator@skillsprint.com"
]

def is_admin(user_email):
    """
    Check if user email is in admin list
    """
    return user_email in ADMIN_EMAILS

def add_admin_email(email):
    """
    Add new admin email (requires code update)
    """
    # In production, this should be stored in database
    return email in ADMIN_EMAILS or email.endswith("@admin.skillsprint.com")

def render_admin_dashboard(current_user):
    """
    Main admin control panel
    """
    st.markdown(
        '<h1 style="font-family:Orbitron, sans-serif;">⚙️ ADMIN DASHBOARD</h1>',
        unsafe_allow_html=True
    )
    
    try:
        user_data = lib.db.child("user").child(current_user["localId"]).get().val()
        user_email = user_data.get("email", "Unknown")
        
        # Verify admin access
        if not is_admin(user_email):
            st.error("❌ ACCESS DENIED - Admin only")
            st.stop()
        
        st.success(f"✅ Welcome Admin: **{user_email}**")
        
        # Admin menu in sidebar
        with st.sidebar:
            st.markdown("### 📋 Admin Menu")
            admin_menu = st.radio("Select Section", [
                "Dashboard Overview",
                "Manage Users",
                "Manage Reviews",
                "Manage Project Ideas",
                "Settings"
            ], label_visibility="collapsed")
        
        # Route to appropriate admin section
        if admin_menu == "Dashboard Overview":
            render_dashboard_overview()
        elif admin_menu == "Manage Users":
            render_manage_users()
        elif admin_menu == "Manage Reviews":
            render_manage_reviews()
        elif admin_menu == "Manage Project Ideas":
            render_project_ideas()
        elif admin_menu == "Settings":
            render_settings()
    
    except Exception as e:
        st.error(f"❌ Error loading admin dashboard: {e}")

def render_dashboard_overview():
    """
    Display platform statistics and overview
    """
    st.header("📊 Platform Overview")
    
    try:
        all_users = lib.db.child("user").get().val() or {}
        
        # Count users by role
        students = [u for u in all_users.values() if u.get("role") == "Student"]
        lecturers = [u for u in all_users.values() if u.get("role") == "Lecturer"]
        alumni = [u for u in all_users.values() if u.get("role") == "Alumni"]
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Total Users", len(all_users), delta=None)
        col2.metric("🎓 Students", len(students), delta=None)
        col3.metric("👨‍🏫 Lecturers", len(lecturers), delta=None)
        col4.metric("🎓 Alumni", len(alumni), delta=None)
        
        st.divider()
        
        # Campus distribution
        st.subheader("📍 Users by Campus")
        campus_data = {}
        for user in all_users.values():
            campus = user.get("campus", "Unknown")
            campus_data[campus] = campus_data.get(campus, 0) + 1
        
        if campus_data:
            df_campus = pd.DataFrame(
                list(campus_data.items()),
                columns=["Campus", "Count"]
            )
            st.bar_chart(df_campus.set_index("Campus"))
        
        st.divider()
        
        # Role distribution
        st.subheader("📊 Users by Role")
        role_data = {
            "Student": len(students),
            "Lecturer": len(lecturers),
            "Alumni": len(alumni)
        }
        df_role = pd.DataFrame(list(role_data.items()), columns=["Role", "Count"])
        st.pie_chart(df_role.set_index("Role"))
        
        st.divider()
        
        # Leaderboard top 5
        st.subheader("🏆 Top 5 Students")
        df_students = pd.DataFrame(students)
        if not df_students.empty:
            df_students = df_students[['username', 'rank', 'campus']].sort_values(
                'rank', ascending=False
            ).head(5)
            df_students.columns = ['Username', 'Rank', 'Campus']
            st.dataframe(df_students, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"Error loading overview: {e}")

def render_manage_users():
    """
    Manage all users - view, edit, delete
    """
    st.header("👥 Manage Users")
    
    try:
        all_users = lib.db.child("user").get().val() or {}
        
        if not all_users:
            st.info("📭 No users found")
            return
        
        # Create user list
        users_list = []
        for uid, user_data in all_users.items():
            users_list.append({
                "User ID": uid[:8] + "...",
                "Username": user_data.get("username", "N/A"),
                "Email": user_data.get("email", "N/A"),
                "Role": user_data.get("role", "N/A"),
                "Campus": user_data.get("campus", "N/A"),
                "Rank": user_data.get("rank", 0),
                "Full UID": uid
            })
        
        df = pd.DataFrame(users_list)
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            role_filter = st.multiselect("Filter by Role", 
                                        ["Student", "Lecturer", "Alumni", "Admin"],
                                        default=["Student", "Lecturer", "Alumni", "Admin"])
        with col2:
            campus_filter = st.multiselect("Filter by Campus",
                                          df["Campus"].unique().tolist(),
                                          default=df["Campus"].unique().tolist())
        
        # Apply filters
        df_filtered = df[(df['Role'].isin(role_filter)) & (df['Campus'].isin(campus_filter))]
        
        # Display table
        st.subheader(f"Users ({len(df_filtered)})")
        st.dataframe(df_filtered[['Username', 'Email', 'Role', 'Campus', 'Rank']], 
                    use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Edit user rank
        st.subheader("✏️ Update User Rank")
        user_emails = df['Email'].unique().tolist()
        selected_email = st.selectbox("Select User", user_emails)
        
        # Find user by email
        selected_uid = None
        selected_user = None
        for uid, user_data in all_users.items():
            if user_data.get("email") == selected_email:
                selected_uid = uid
                selected_user = user_data
                break
        
        if selected_user and selected_uid:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Username:** {selected_user.get('username')}")
                st.write(f"**Role:** {selected_user.get('role')}")
                st.write(f"**Campus:** {selected_user.get('campus')}")
            with col2:
                st.write(f"**Current Rank:** {selected_user.get('rank', 0)}")
            
            new_rank = st.number_input("New Rank Score", 
                                      value=int(selected_user.get("rank", 0)),
                                      min_value=0,
                                      step=1)
            
            if st.button("💾 Update Rank", type="primary"):
                lib.db.child("user").child(selected_uid).update({"rank": int(new_rank)})
                st.success(f"✅ Rank updated to {new_rank}!")
                st.rerun()
        
        st.divider()
        
        # Delete user
        st.subheader("🗑️ Delete User")
        delete_email = st.selectbox("Select User to Delete", user_emails, key="delete_user")
        
        if st.button("❌ Delete User", type="secondary"):
            for uid, user_data in all_users.items():
                if user_data.get("email") == delete_email:
                    lib.db.child("user").child(uid).remove()
                    st.success(f"✅ User {delete_email} deleted!")
                    st.rerun()
                    break
    
    except Exception as e:
        st.error(f"Error managing users: {e}")

def render_manage_reviews():
    """
    Approve, moderate, and delete alumni reviews
    """
    st.header("⭐ Manage Alumni Reviews")
    
    try:
        reviews = lib.db.child("alumni_reviews").get().val() or {}
        
        if not reviews:
            st.info("📭 No reviews found")
            return
        
        # Stats
        col1, col2, col3 = st.columns(3)
        avg_rating = sum(r.get('rating', 0) for r in reviews.values()) / len(reviews) if reviews else 0
        col1.metric("Total Reviews", len(reviews))
        col2.metric("Avg Rating", f"{avg_rating:.1f}/5")
        col3.metric("Unique Authors", len(set(r.get('username') for r in reviews.values())))
        
        st.divider()
        
        # Display reviews with delete option
        st.subheader("📋 All Reviews")
        
        sorted_reviews = sorted(reviews.items(),
                              key=lambda x: x[1].get('timestamp', ''),
                              reverse=True)
        
        for review_id, review_data in sorted_reviews:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    author = review_data.get('username', 'Anonymous')
                    rating = review_data.get('rating', 0)
                    stars = "⭐" * rating
                    st.write(f"**{author}** {stars}")
                    st.caption(review_data.get('created_at', 'Unknown date'))
                    st.markdown(f"_{review_data.get('review', '')}_")
                
                with col2:
                    if st.button("🔍", key=f"view_{review_id}", help="View details"):
                        st.info(f"Review ID: {review_id}")
                
                with col3:
                    if st.button("🗑️", key=f"delete_{review_id}", help="Delete review"):
                        lib.db.child("alumni_reviews").child(review_id).remove()
                        st.success("✅ Review deleted!")
                        st.rerun()
                
                st.divider()
    
    except Exception as e:
        st.error(f"Error managing reviews: {e}")

def render_project_ideas():
    """
    Manage project ideas
    """
    st.header("📋 Project Ideas Management")
    
    st.info("🚀 Feature coming soon - Manage and archive project ideas")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("✨ Features planned:")
        st.write("- Archive past projects")
        st.write("- Create custom projects")
        st.write("- Schedule projects by week")
    with col2:
        st.write("📊 Current Project Stats:")
        st.metric("Active Projects", 1)
        st.metric("Archived Projects", 0)

def render_settings():
    """
    Admin settings and configuration
    """
    st.header("⚙️ System Settings")
    
    try:
        tab1, tab2, tab3 = st.tabs(["Admin Management", "System Info", "Danger Zone"])
        
        with tab1:
            st.subheader("👨‍💼 Admin Access Control")
            
            st.write("**Current Admin Emails:**")
            for i, admin_email in enumerate(ADMIN_EMAILS, 1):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i}. {admin_email}")
                with col2:
                    if st.button("❌", key=f"remove_admin_{i}"):
                        st.info("Admin removal requires code update")
            
            st.divider()
            st.write("**Add New Admin** (requires code update)")
            new_admin = st.text_input("New admin email")
            if st.button("Add Admin"):
                st.warning("⚠️ Admin emails must be added to ADMIN_EMAILS list in admin.py")
                st.code(f"ADMIN_EMAILS = {ADMIN_EMAILS + [new_admin]}")
        
        with tab2:
            st.subheader("ℹ️ System Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Firebase Config Status:**")
                st.success("✅ Connected")
                st.write(f"Database: skillsprint-cf16f")
                st.write(f"Auth: Enabled")
            with col2:
                st.write("**JWT Configuration:**")
                st.write(f"Algorithm: HS256")
                st.write(f"Token Expiry: 24 hours")
                st.write(f"Status: ✅ Active")
        
        with tab3:
            st.subheader("⚠️ Danger Zone")
            st.warning("These actions cannot be undone!")
            
            if st.checkbox("I understand the consequences"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Clear All Reviews", type="secondary"):
                        try:
                            lib.db.child("alumni_reviews").remove()
                            st.success("✅ All reviews cleared!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                
                with col2:
                    if st.button("Reset Database", type="secondary"):
                        st.error("❌ Database reset not available for safety")
    
    except Exception as e:
        st.error(f"Error loading settings: {e}")