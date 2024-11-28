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
# 페이지 전환 함수
def change_page(page_name):
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if st.session_state["current_page"] != page_name:
        st.session_state["history"].append(st.session_state["current_page"])
    st.session_state["current_page"] = page_name
    st.rerun()


# 뒤로가기 함수
def go_back():
    if 'history' in st.session_state and st.session_state.history:
        st.session_state.current_page = st.session_state.history.pop()  # 이전 페이지로 이동
        st.rerun()
    else:
        st.warning("이전 페이지가 없습니다.")  # 방문 기록이 없을 경우 처리
        st.rerun()

# 홈 페이지 함수 (로그인 전)
def home_page():
    col1, col2, col3 = st.columns([1, 1, 1])  # 동일한 너비의 세 개 열 생성
    with col1:
        if st.button("로그인", key="home_login_button"):
            change_page('Login')  # 로그인 페이지로 이동
    with col2:
        if st.button("회원가입", key="home_signup_button"):
            change_page('Signup')  # 회원가입 페이지로 이동
    with col3:
        if st.button("ID/PW 찾기", key="home_forgot_button"):
            change_page('User manager')  # ID/PW 찾기 페이지로 이동

#로그인 페이지
def login_page():
    st.title("로그인")
    user_id = st.text_input("아이디", key="login_user_id_input")
    user_password = st.text_input("비밀번호", type='password', key="login_password_input")

    col1, col2 = st.columns([1, 1])  # 버튼을 나란히 배치
    with col1:
        if st.button("로그인", key="login_submit_button"):
            if not user_id or not user_password:
                st.error("아이디와 비밀번호를 입력해 주세요.")
            else:
                sign_in = SignIn(user_id, user_password)
                if sign_in.sign_in_event():  # 로그인 성공 시
                    st.session_state['user_id'] = user_id  # 로그인한 사용자 ID 저장
                    st.session.state['user_password']=user_password
                    change_page('after_login')  # 로그인 후 홈화면으로 이동
                else:
                    st.error("로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해 주세요.")
    with col2:
        if st.button("뒤로가기", key="login_back_button"):
            go_back()  # 뒤로가기 로직 호출



#회원가입 페이지
def signup_page():
    st.title("회원가입")

    # 사용자 입력 받기
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type='password')
    email = st.text_input("이메일")
    # 회원가입 처리 객체 생성
    signup = SignUp(user_id, user_password, email)
    col1, col2 = st.columns([1, 1])  # 버튼을 나란히 배치
    with col1:
        if st.button("회원가입", key="signup_submit_button"):
            if not user_id or not user_password or not email:
                st.error("모든 필드를 입력해 주세요.")
            else:
                if not signup.validate_email(email):
                    st.error("유효한 이메일 주소를 입력해 주세요.")
                    return
                # 비밀번호 길이 체크
                if not signup.check_length():
                    return  # 비밀번호가 너무 짧으면 더 이상 진행하지 않음

                # 사용자 ID 중복 체크
                if not signup.check_user():
                    return  # 중복 아이디가 있으면 더 이상 진행하지 않음

                # 모든 검증을 통과하면 회원가입 진행
                signup.sign_up_event()

    with col2:
        if st.button("뒤로가기", key="signup_back_button"):
            go_back()  # 뒤로가기 로직 호출


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
    role = Column(
        String,
        CheckConstraint("role IN ('admin', 'member')"),  # 위치 인수 대신 키워드로 전달
        default='member'
    )
    joined_at = Column(Text, nullable=False, default="CURRENT_TIMESTAMP")

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

#------------------db만들기 ----------------------------

# SQLAlchemy Base 선언
Base = declarative_base()

# 데이터베이스 연결 설정
DATABASE_URL = "sqlite:///zip.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# 데이터베이스 모델 정의
class User(Base):
    __tablename__ = 'user'
    user_id = Column(String, primary_key=True)
    user_password = Column(String, nullable=False)
    user_email = Column(String, unique=True, nullable=False)
    user_is_online = Column(Boolean, default=False)

# 데이터베이스 초기화
def initialize_database():
    Base.metadata.create_all(engine)

# DAO 클래스
class UserDAO:
    def __init__(self):
        self.session = SessionLocal()

    def check_user_id_exists(self, user_id):
        """아이디 존재 여부 체크"""
        try:
            return self.session.query(User).filter_by(user_id=user_id).first()
        except Exception as e:
            st.error(f"DB 오류: {e}")
            return None

    def insert_user(self, user_id, user_password, user_email):
        """새 사용자 추가"""
        hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(user_id=user_id, user_password=hashed_password, user_email=user_email)
        try:
            self.session.add(new_user)
            self.session.commit()
            st.success("회원가입이 완료되었습니다!")
        except Exception as e:
            self.session.rollback()
            st.error(f"DB 오류: {e}")

    def update_user_online(self, user_id, is_online):
        """사용자 온라인 상태 업데이트"""
        try:
            user = self.session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.user_is_online = is_online
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            st.error(f"DB 오류: {e}")

    def check_password(self, hashed_password, plain_password):
        """비밀번호 일치 여부 확인"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# 회원가입 클래스
class SignUp:
    def __init__(self, user_id, user_password, user_email):
        self.user_id = user_id
        self.user_password = user_password
        self.user_email = user_email

    def sign_up_event(self):
        dao = UserDAO()
        if not self.check_length():
            return False
        if not self.check_user():
            return False
        dao.insert_user(self.user_id, self.user_password, self.user_email)
        return True

    def check_length(self):
        """비밀번호 길이 체크"""
        if len(self.user_password) < 8:
            st.error("비밀번호는 최소 8자 이상이어야 합니다.")
            return False
        return True

    def check_user(self):
        """아이디 중복 체크"""
        dao = UserDAO()
        if dao.check_user_id_exists(self.user_id):
            st.error("이미 사용 중인 아이디입니다.")
            return False
        return True

# 로그인 처리 클래스
class SignIn:
    def __init__(self, user_id, user_password):
        self.user_id = user_id
        self.user_password = user_password

    def sign_in_event(self):
        dao = UserDAO()
        user = dao.check_user_id_exists(self.user_id)
        if user:
            if dao.check_password(user.user_password, self.user_password):
                st.session_state["user_id"] = self.user_id  # 세션에 사용자 ID 저장
                dao.update_user_online(self.user_id, True)  # 온라인 상태 업데이트
                st.success(f"{self.user_id}님, 로그인 성공!")
                return True
            else:
                st.error("비밀번호가 틀렸습니다.")
        else:
            st.error("아이디가 존재하지 않습니다.")
        return False

# 로그인 페이지
def login_page():
    st.title("로그인")
    user_id = st.text_input("아이디")
    user_password = st.text_input("비밀번호", type='password')

    col1, col2 = st.columns(2)
    with col1:
        if st.button("로그인"):
            if not user_id or not user_password:
                st.error("아이디와 비밀번호를 입력해 주세요.")
            else:
                sign_in = SignIn(user_id, user_password)
                if sign_in.sign_in_event():
                    st.session_state['current_page'] = 'Home'  # 로그인 성공 시 페이지 이동
    with col2:
        if st.button("뒤로가기"):
            st.session_state['current_page'] = 'Signup'
            
# 페이지 함수 매핑
page_functions = {
    'Home': home_page,
    'Signup': signup_page,
    'Login': login_page,
}
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'



initialize_database()
# 현재 페이지 디버깅
st.write(f"Current Page: {st.session_state['current_page']}")  # 디버깅용 코드

# 현재 페이지 렌더링
if st.session_state["current_page"] in page_functions:
    page_functions[st.session_state["current_page"]]()  # 매핑된 함수 호출
else:
    st.error(f"페이지 {st.session_state['current_page']}를 찾을 수 없습니다.")
    

