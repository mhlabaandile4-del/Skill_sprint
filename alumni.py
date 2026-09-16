import streamlit as st
import lib as lib
from datetime import datetime
import pandas as pd

def add_alumni_review(user_id, username, rating, review_text):
    """
    Store alumni review in Firebase database
    """
    try:
        review_timestamp = datetime.now().isoformat()
        review_data = {
            "user_id": user_id,
            "username": username,
            "rating": int(rating),
            "review": review_text.strip(),
            "timestamp": review_timestamp,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        lib.db.child("alumni_reviews").push(review_data)
        return True
    except Exception as e:
        print(f"Error adding review: {e}")
        return False

def get_all_alumni_reviews():
    """
    Fetch all alumni reviews from Firebase
    """
    try:
        reviews = lib.db.child("alumni_reviews").get().val() or {}
        return reviews
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return {}

def delete_alumni_review(review_id):
    """
    Delete a specific alumni review
    """
    try:
        lib.db.child("alumni_reviews").child(review_id).remove()
        return True
    except Exception as e:
        print(f"Error deleting review: {e}")
        return False

def get_user_reviews(user_id):
    """
    Get all reviews by a specific user
    """
    try:
        reviews = lib.db.child("alumni_reviews").get().val() or {}
        user_reviews = {k: v for k, v in reviews.items() if v.get("user_id") == user_id}
        return user_reviews
    except Exception as e:
        print(f"Error fetching user reviews: {e}")
        return {}

def render_alumni_section(current_user):
    """
    Main alumni section - view and post reviews
    """
    st.markdown(
        '<h2 style="font-family:Orbitron, sans-serif;">🎓 ALUMNI REVIEWS</h2>',
        unsafe_allow_html=True
    )
    
    try:
        user_data = lib.db.child("user").child(current_user["localId"]).get().val()
        username = user_data.get("username", "Anonymous")
        user_id = current_user["localId"]
        
        # Create tabs for better UX
        tab1, tab2 = st.tabs(["Post Review", "View All Reviews"])
        
        with tab1:
            st.subheader("Share Your SkillSprint Experience")
            st.write("Help other alumni learn from your journey!")
            
            with st.form("alumni_review_form", clear_on_submit=True):
                rating = st.slider("Rate your SkillSprint experience", 1, 5, 5, 
                                  help="1 = Poor, 5 = Excellent")
                review = st.text_area("Write your review", 
                                     placeholder="What did you learn? What was your experience?",
                                     max_chars=500,
                                     height=150)
                
                submit_button = st.form_submit_button("📤 Post Review", use_container_width=True)
                
                if submit_button:
                    if review.strip():
                        if add_alumni_review(user_id, username, rating, review):
                            st.success("✅ Review posted successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Failed to post review. Please try again.")
                    else:
                        st.warning("⚠️ Please write a review before posting")
        
        with tab2:
            st.subheader("Community Reviews")
            reviews = get_all_alumni_reviews()
            
            if reviews:
                # Sort by timestamp (newest first)
                sorted_reviews = sorted(reviews.items(), 
                                      key=lambda x: x[1].get('timestamp', ''), 
                                      reverse=True)
                
                # Stats
                col1, col2, col3 = st.columns(3)
                avg_rating = sum(r[1].get('rating', 0) for r in sorted_reviews) / len(sorted_reviews)
                col1.metric("Total Reviews", len(sorted_reviews))
                col2.metric("Avg Rating", f"{avg_rating:.1f}/5")
                col3.metric("Alumni", len(set(r[1].get('username') for r in sorted_reviews)))
                
                st.divider()
                
                for review_id, review_data in sorted_reviews:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            author = review_data.get('username', 'Anonymous')
                            st.write(f"**{author}**")
                        
                        with col2:
                            rating = review_data.get('rating', 0)
                            stars = "⭐" * rating
                            st.write(stars)
                        
                        with col3:
                            posted = review_data.get('created_at', 'Unknown date')
                            st.caption(f"📅 {posted}")
                        
                        review_text = review_data.get('review', '')
                        st.markdown(f"_{review_text}_")
                        st.divider()
            else:
                st.info("🌱 No reviews yet. Be the first to share your experience!")
    
    except Exception as e:
        st.error(f"❌ Error loading alumni section: {e}")

def render_alumni_stats(current_user):
    """
    Display alumni statistics on dashboard
    """
    try:
        reviews = get_all_alumni_reviews()
        if reviews:
            avg_rating = sum(r.get('rating', 0) for r in reviews.values()) / len(reviews)
            return {
                'total_reviews': len(reviews),
                'avg_rating': round(avg_rating, 1),
                'total_alumni': len(set(r.get('username') for r in reviews.values()))
            }
        return {'total_reviews': 0, 'avg_rating': 0, 'total_alumni': 0}
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {'total_reviews': 0, 'avg_rating': 0, 'total_alumni': 0}