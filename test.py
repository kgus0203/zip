import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt

# Database setup
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    user_id = Column(String, primary_key=True)
    user_password = Column(String)
    user_email = Column(String)
    user_is_online = Column(Integer, default=0)
    user_mannerscore = Column(Integer, default=0)
    profile_picture_path = Column(String)
    
    def __init__(self, user_id, user_password, user_email):
        self.user_id = user_id
        self.user_password = user_password
        self.user_email = user_email

class Friend(Base):
    __tablename__ = 'friend'
    
    friend_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    friend_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    status = Column(String, nullable=False)
    
    user = relationship('User', foreign_keys=[user_id])
    friend_user = relationship('User', foreign_keys=[friend_user_id])

class Group(Base):
    __tablename__ = 'group'
    
    group_id = Column(Integer, primary_key=True)
    group_name = Column(String, unique=True, nullable=False)
    group_creator = Column(String, ForeignKey('user.user_id'), nullable=False)
    category = Column(Integer)
    location = Column(Integer)
    meeting_date = Column(DateTime)
    status = Column(String, default='진행 중')

# Create connection using Streamlit's st.connection
def create_connection():
    conn = st.connection("sql", type="sql")
    return conn

# Create all tables if they do not exist
def create_db():
    conn = create_connection()
    with conn.session as s:
        Base.metadata.create_all(bind=conn.engine)  # Creates tables in the DB if they don't exist

# Insert user into the database
def insert_user(user_id, user_password, user_email):
    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
    
    conn = create_connection()
    with conn.session as s:
        new_user = User(user_id=user_id, user_password=hashed_password, user_email=user_email)
        s.add(new_user)
        s.commit()
        st.success(f"User {user_id} has been successfully registered!")

# Check if user exists
def check_user_exists(user_id):
    conn = create_connection()
    with conn.session as s:
        user = s.query(User).filter_by(user_id=user_id).first()
        return user is not None

# Verify password
def verify_password(user_id, password):
    conn = create_connection()
    with conn.session as s:
        user = s.query(User).filter_by(user_id=user_id).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.user_password.encode('utf-8')):
            return True
        return False

# Login page
def login_page():
    st.title("Login Page")
    
    user_id = st.text_input("User ID")
    user_password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        if user_id and user_password:
            if verify_password(user_id, user_password):
                st.session_state["user_id"] = user_id
                st.success(f"Welcome back, {user_id}!")
            else:
                st.error("Invalid user ID or password.")
        else:
            st.error("Please enter both user ID and password.")

# Sign up page
def signup_page():
    st.title("Signup Page")
    
    user_id = st.text_input("User ID")
    user_password = st.text_input("Password", type='password')
    user_email = st.text_input("Email")
    
    if st.button("Signup"):
        if user_id and user_password and user_email:
            if check_user_exists(user_id):
                st.error("This user ID already exists. Please choose a different one.")
            else:
                insert_user(user_id, user_password, user_email)
        else:
            st.error("Please fill all fields.")

# Home page
def home_page():
    st.title("Home Page")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Login"):
            st.session_state["current_page"] = "Login"
            st.experimental_rerun()
    with col2:
        if st.button("Signup"):
            st.session_state["current_page"] = "Signup"
            st.experimental_rerun()

# Page routing logic
def page_routing():
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Home'
    
    if st.session_state['current_page'] == 'Home':
        home_page()
    elif st.session_state['current_page'] == 'Login':
        login_page()
    elif st.session_state['current_page'] == 'Signup':
        signup_page()

# Main function to run the app
def main():
    create_db()  # Initialize DB and tables
    page_routing()  # Handle page navigation

# Run the application
if __name__ == "__main__":
    main()
