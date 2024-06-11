import streamlit as st
import pandas as pd
import time
import os

# Define a function to read data from CSV
def read_csv_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"CSV file '{file_path}' not found.")
        return None
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None

# Define a function to write data to CSV
def write_csv_data(file_path, data):
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

# Define a function to authenticate users
def authenticate(username, password, file_path='users.csv'):
    try:
        df = pd.read_csv(file_path)
        user_row = df[(df['Username'] == username) & (df['Password'] == password)]
        if not user_row.empty:
            st.session_state.user_details = user_row.iloc[0].to_dict()  # Store user details in session state
            return True
        else:
            return False
    except FileNotFoundError:
        st.error(f"CSV file '{file_path}' not found.")
        return False
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return False

# Define the login page
def login():
    st.markdown("<h1 style='text-align: center; color: #FF6347;'>Login Page</h1>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Sign In"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.current_page = "browse"  # Redirect to browse page upon successful login
        else:
            st.error("Authentication failed. Please check your username and password.")
    
    # Back to Front Page option
    if st.button("Back to frontpage"):
        st.session_state.current_page = "front"
        st.experimental_rerun()

# Define the sign-up page
def signup():
    st.markdown("<h1 style='text-align: center; color: #32CD32;'>Sign Up Page</h1>", unsafe_allow_html=True)
    
    # Input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    phone_number = st.text_input("Phone Number")
    waist = st.number_input("Waist Measurement", min_value=0.0, step=0.1)
    bust = st.number_input("Bust Measurement", min_value=0.0, step=0.1)
    hip = st.number_input("Hip Measurement", min_value=0.0, step=0.1)
    
    # Disclaimer checkbox
    disclaimer = st.checkbox("I agree to the terms and conditions")
    
    # Create Account button
    if st.button("Create Account"):
        if not disclaimer:
            st.error("Account can't be created unless you agree to the terms.")
        else:
            # Read existing data
            user_data_file = 'users.csv'
            if os.path.exists(user_data_file):
                existing_data = pd.read_csv(user_data_file).to_dict('records')
            else:
                existing_data = []
            
            # Append new user data
            new_user = {
                "Username": username,
                "Password": password,
                "Phone Number": phone_number,
                "Waist Measurement": waist,
                "Bust Measurement": bust,
                "Hip Measurement": hip
            }
            existing_data.append(new_user)
            
            # Write updated data to CSV
            write_csv_data(user_data_file, existing_data)
            
            st.success("Account created successfully!")
            time.sleep(2)  # Simulate a delay
            st.session_state.current_page = "front"
            st.experimental_rerun()
    elif st.button("Back to frontpage"):
        st.session_state.current_page = "front"
        st.experimental_rerun()

# Define the browse page
def browse(df):
    st.sidebar.markdown("<h2 style='text-align: center; color: #1E90FF;'>Browse Page</h2>", unsafe_allow_html=True)
    
    # Navigation bar with logout option
    if st.session_state.logged_in:
        nav_choice = st.sidebar.radio("Navigate", ["Browse", "Saved Outfits", "Logout"])
    else:
        nav_choice = st.sidebar.radio("Navigate", ["Browse", "Back to Front Page"])

    if nav_choice == "Browse":
        # Filter out rows where ImageURL is not NaN
        df = df[pd.notna(df['ImageURL'])]
        
        # Display images and buttons in a grid layout
        num_columns = 3
        for i in range(0, len(df), num_columns):
            row_data = df.iloc[i:i+num_columns]
            row = st.columns(num_columns)
            for index, data in row_data.iterrows():
                with row[index % num_columns]:
                    st.image(data['ImageURL'], use_column_width=True)
                    if st.session_state.logged_in:
                        st.button(f"Save Outfit", key=f"button_save_{index}")
                    else:
                        st.button(f"View Outfit", key=f"button_view_{index}")
    elif nav_choice == "Saved Outfits" and st.session_state.logged_in:
        st.markdown("<h2 style='text-align: center; color: #FF69B4;'>Saved Outfits</h2>", unsafe_allow_html=True)
        # You can implement your logic to display saved outfits here
    elif nav_choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.current_page = "front"
        st.experimental_rerun()
    elif nav_choice == "Back to Front Page":
        st.session_state.current_page = "front"
        st.experimental_rerun()

# Main function to run the app
def main():
    st.set_page_config(page_title="Threads in the Matrix", page_icon="🧵")
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "front"
    
    if st.session_state.current_page == "front":
        front_page()
    elif st.session_state.current_page == "signup":
        signup()
    elif st.session_state.current_page == "login":
        login()
    elif st.session_state.current_page == "browse":
        df = read_csv_data('images.csv')
        if df is not None:
            browse(df)

# Front page with navigation options
def front_page():
    st.markdown("<h1 style='text-align: center; color: #FF4500;'>Welcome to Threads in the Matrix</h1>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #4682B4;'>Choose an option:</h2>", unsafe_allow_html=True)
    if st.button("Sign Up"):
        st.session_state.current_page = "signup"
    if st.button("Sign In"):
        st.session_state.current_page = "login"
    
    view_once = st.button("View Once")
    
    # Show terms and conditions checkbox if View Once is clicked
    if view_once or 'view_once' in st.session_state:
        st.session_state.view_once = True
        terms_accepted = st.checkbox("I agree to the terms and conditions")
        if terms_accepted:
            st.session_state.current_page = "browse"
            st.experimental_rerun()

if __name__ == "__main__":
    main()
