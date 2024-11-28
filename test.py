import streamlit as st
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, func, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# SQLAlchemy Base 선언
Base = declarative_base()

# 데이터베이스 URL 설정
DATABASE_URL = "sqlite:///zip.db"

# 데이터베이스 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 테이블 모델 정의
class User(Base):
    __tablename__ = 'user'
    user_id = Column(String, primary_key=True)
    user_password = Column(String, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    user_is_online = Column(Boolean, default=False)
    user_mannerscore = Column(Integer, default=0)
    profile_picture_path = Column(String, nullable=True)

class Friend(Base):
    __tablename__ = 'friend'
    friend_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    friend_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    status = Column(String, nullable=False)

class Group(Base):
    __tablename__ = 'group'
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String, unique=True, nullable=False)
    group_creator = Column(String, ForeignKey('user.user_id'), nullable=False)
    category = Column(Integer, nullable=True)
    date = Column(DateTime, default=func.now())
    location = Column(Integer, nullable=True)
    meeting_date = Column(String, nullable=True)
    meeting_time = Column(String, nullable=True)
    status = Column(String, default='진행 중')
    update_date = Column(DateTime, default=func.now(), onupdate=func.now())
    modify_date = Column(DateTime, default=func.now(), onupdate=func.now())

class GroupMember(Base):
    __tablename__ = 'group_member'
    group_member_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    role = Column(String, default='member', CheckConstraint("role IN ('admin', 'member')"))
    joined_at = Column(DateTime, default=func.now())

class FoodCategory(Base):
    __tablename__ = 'food_categories'
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, unique=True, nullable=False)

class Location(Base):
    __tablename__ = 'locations'
    location_id = Column(Integer, primary_key=True, autoincrement=True)
    location_name = Column(String, nullable=False)
    address_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)
    sender_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    message_text = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=func.now())

class Posting(Base):
    __tablename__ = 'posting'
    p_id = Column(Integer, primary_key=True, autoincrement=True)
    p_title = Column(String, nullable=False)
    p_content = Column(Text, nullable=False)
    p_image_path = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    p_location = Column(Integer, ForeignKey('locations.location_id'), nullable=True)
    p_category = Column(Integer, ForeignKey('food_categories.category_id'), nullable=True)
    like_num = Column(Integer, default=0)
    file = Column(Text, nullable=True)  # Adjust as needed
    upload_date = Column(DateTime, default=func.now())
    modify_date = Column(DateTime, default=func.now(), onupdate=func.now())

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    current_theme = Column(String, nullable=True)

# 데이터베이스 초기화 및 기본 데이터 삽입
def initialize_database():
    Base.metadata.create_all(engine)

    # 기본 데이터 삽입
    if not session.query(User).filter_by(user_id="default_user").first():
        default_user = User(
            user_id="default_user",
            user_password="default_password",  # 실제로는 비밀번호 해싱 필요
            user_email="default@example.com",
            profile_picture_path="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        )
        session.add(default_user)

    # Food Categories 기본값 삽입
    default_categories = ["한식", "중식", "양식", "일식", "디저트", "패스트푸드"]
    for category in default_categories:
        if not session.query(FoodCategory).filter_by(category=category).first():
            session.add(FoodCategory(category=category))
    
    session.commit()

# 유틸리티 함수
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password, plain_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# 회원가입 페이지
def signup_page():
    st.title("회원가입")
    user_id = st.text_input("아이디")
    user_email = st.text_input("이메일")
    user_password = st.text_input("비밀번호", type="password")
    if st.button("회원가입"):
        if not user_id or not user_email or not user_password:
            st.error("모든 필드를 입력해주세요.")
        elif len(user_password) < 8:
            st.error("비밀번호는 8자 이상이어야 합니다.")
        else:
            existing_user = session.query(User).filter_by(user_id=user_id).first()
            if existing_user:
                st.error("이미 존재하는 아이디입니다.")
            else:
                hashed_password = hash_password(user_password)
                new_user = User(
                    user_id=user_id,
                    user_password=hashed_password,
                    user_email=user_email
                )
                session.add(new_user)
                session.commit()
                st.success("회원가입이 완료되었습니다!")

# 로그인 페이지
def login_page():
    st.title("로그인")
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        user = session.query(User).filter_by(user_id=user_id).first()
        if user and check_password(user.user_password, user_password):
            st.session_state["user_id"] = user_id
            user.user_is_online = True
            session.commit()
            st.success(f"{user_id}님, 환영합니다!")
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")

# 메인 페이지
def main_page():
    st.title("메인 페이지")
    if "user_id" in st.session_state:
        st.success(f"로그인 상태: {st.session_state['user_id']}")
        if st.button("로그아웃"):
            user = session.query(User).filter_by(user_id=st.session_state['user_id']).first()
            if user:
                user.user_is_online = False
                session.commit()
            del st.session_state["user_id"]
            st.experimental_rerun()
    else:
        st.info("로그인이 필요합니다.")

# Streamlit 앱 실행
def main():
    initialize_database()
    if "user_id" not in st.session_state:
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    main()
