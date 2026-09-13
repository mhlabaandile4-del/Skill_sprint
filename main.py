import lib as lib
import streamlit as st
import pandas as pd

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

    lgnorsgn  = st.radio("New here ?", options = ("Yes", "No")) 
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
        #Start working on the student page, add a simple leaderboard that shows the top 10 students based on their rank.
        st.title(f"Welcome, {name}!")


        # AI PROMPT
       

        st.title("Leaderboard")      
        st.write("Click any row to view full profile details")
        
        if all_students:
                raw_data = list(all_students.values())
                df       = pd.DataFrame(raw_data)
        
                df       = df.rename(columns={"username": "student_name", "rank": "score"})
                df       = df.sort_values(by="score", ascending=False).reset_index(drop = True)
                df["Rank"] = df.index + 1
        
                df["Rank"] = df["Rank"].map({1: "1", 2: "2", 3: "3"}).fillna(df["Rank"])
        
                display_cols =["Rank", "student_name" , "score"]
                other_cols   = [col for col in df.columns if col not in display_cols]
                ordered_df   = df[display_cols + other_cols]

                selection = st.dataframe(
                        ordered_df[display_cols],
                        use_container_width=True,
                        hide_index=True,
                        on_select= "rerun",
                        selection_mode= "single-row"
                )
                with st.sidebar:
                        selected_rows = selection.get("selection", {}).get("rows", [])

                        if selected_rows:
                                row_index    = selected_rows[0]
                                user_profile = ordered_df.iloc[row_index]

                                st.header(f"{user_profile["student_name"]}")
                                st.subheader(f"Rank {user_profile["Rank"]} ({user_profile["score"]} pts)")
                                st.divider()

                                st.markdown("ALL STUDENT DATA")
                                for key in other_cols:
                                        clean_key = key.replace("_", " ").title()
                                        st.write(f"{clean_key}: {user_profile[key]}")

                        else:
                                st.header("Profile viewer")
                                st.info("Click a student on the main leaderboard table to see their full profile")

        else:
                st.info("The database is currently empty")
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
        
      #Make a the lecturer page that shows a list of all students and their information, and allows the lecturer to update the students rank with a simple form.
      all_students = lib.db.child("user").get().val()

      # AI PROMPT
      st.title("Leaderboard")      
      st.write("Click any row to view full profile details")
              
      if all_students:
                raw_data = list(all_students.values())
                df       = pd.DataFrame(raw_data)
              
                df       = df.rename(columns={"username": "student_name", "rank": "score"})
                df       = df.sort_values(by="score", ascending=False).reset_index(drop = True)
                df["Rank"] = df.index + 1
              
                df["Rank"] = df["Rank"].map({1: "1", 2: "2", 3: "3"}).fillna(df["Rank"])
              
                display_cols =["Rank", "student_name" , "score"]
                other_cols   = [col for col in df.columns if col not in display_cols]
                ordered_df   = df[display_cols + other_cols]
      
                selection = st.dataframe(
                        ordered_df[display_cols],
                        use_container_width=True,
                        hide_index=True,
                        on_select= "rerun",
                        selection_mode= "single-row"
                      )
                with st.sidebar:
                        selected_rows = selection.get("selection", {}).get("rows", [])
      
                        if selected_rows:
                                row_index    = selected_rows[0]
                                user_profile = ordered_df.iloc[row_index]
      
                                st.header(f"{user_profile["student_name"]}")
                                st.subheader(f"Rank {user_profile["Rank"]} ({user_profile["score"]} pts)")
                                st.divider()
      
                                st.markdown("ALL STUDENT DATA")
                                for key in other_cols:
                                        clean_key = key.replace("_", " ").title()
                                        st.write(f"{clean_key}: {user_profile[key]}")
      
                        else:
                                st.header("Profile viewer")
                                st.info("Click a student on the main leaderboard table to see their full profile")
      
      else:
        st.info("The database is currently empty")
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



