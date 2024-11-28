import streamlit as st
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, func, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import string
import bcrypt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from datetime import datetime
import secrets
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import os

# SQLAlchemy Base 선언
Base = declarative_base()

# 데이터베이스 URL 설정
DATABASE_URL = "sqlite:///zip.db"

# 데이터베이스 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
#-----------------------------------------------페이지 전환 ----------------------------------------------------------

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
                    st.session_state['user_password'] = user_password
                    change_page('after_login')  # 로그인 후 홈화면으로 이동
                else:
                    st.error("로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해 주세요.")
    with col2:
        if st.button("뒤로가기", key="login_back_button"):
            go_back()  # 뒤로가기 로직 호출



def usermanager_page():
    st.title("사용자 관리 페이지")
    
    # 사용자에게 이메일 입력 받기
    email = st.text_input('이메일을 입력하세요: ')

    # "확인" 버튼을 눌렀을 때
    if st.button("확인", key="forgot_confirm_button"):
        smtp_email = "kgus0203001@gmail.com"  # 발신 이메일 주소
        smtp_password = "your_smtp_password_here"  # 발신 이메일 비밀번호 (보안상의 이유로 환경 변수나 다른 방법으로 관리하는 것이 좋음)
        
        user_manager = UserManager(smtp_email, smtp_password)

        # 이메일 등록 여부 확인
        user_info = user_manager.is_email_registered(email)
        if user_info:
            st.success(f"비밀번호 복구 메일을 전송했습니다.")
            # 복구 이메일 전송
            token = user_manager.generate_token()  # 토큰 생성
            user_manager.save_recovery_token(email, token)  # 토큰 저장
            user_manager.send_recovery_email(email, token)  # 이메일 전송
        else:
            st.warning("등록되지 않은 이메일입니다.")
    
    # "뒤로가기" 버튼을 눌렀을 때 첫 페이지로 이동
    if st.button("뒤로가기", key="forgot_back_button"):
        change_page("Home")  # change_page는 페이지 이동 함수로 정의되어 있어야 합니다。

def change_page(page_name):
    """페이지 이동 함수"""
    st.session_state['current_page'] = page_name  # 세션에 현재 페이지 정보 저장
    st.rerun()  # 페이지를 다시 로드하여 새 페이지로 전환

        
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


def id_pw_change_page():
    st.title("<ID/PW 변경>")

    # 현재 로그인된 사용자 ID 가져오기
    user_id = st.session_state.get('logged_in_user')
    if not user_id:
        st.error("사용자 정보가 없습니다. 다시 로그인해주세요.")
        change_page('Login')  # 로그인 페이지로 이동
        return

    # 초기화 상태 설정
    if "id_pw_change_step" not in st.session_state:
        st.session_state['id_pw_change_step'] = "select_action"

    if "current_user_id" not in st.session_state:
        st.session_state['current_user_id'] = user_id

    # ID 또는 PW 변경 선택
    if st.session_state['id_pw_change_step'] == "select_action":
        action = st.radio("변경할 항목을 선택하세요", ["ID 변경", "비밀번호 변경"])
        if st.button("다음"):
            st.session_state['action'] = action
            st.session_state['id_pw_change_step'] = "input_new_value"

    # 새로운 ID/PW 입력 및 저장
    elif st.session_state['id_pw_change_step'] == "input_new_value":
        new_value = st.text_input(f"새로 사용할 {st.session_state['action']}를 입력하세요")
        if new_value and st.button("저장"):
            change = login.ChangeIDPW(
                user_id=st.session_state['current_user_id'],
                new_value=new_value
            )
            if st.session_state['action'] == "ID 변경" and change.update_id():
                st.success("ID가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.")
                st.session_state.user.clear()  # 세션 초기화로 로그아웃 처리
                change_page("Home")  # 첫 페이지로 이동
            elif st.session_state['action'] == "비밀번호 변경" and change.update_password():
                st.success("비밀번호가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.")
                st.session_state.user.clear()  # 세션 초기화로 로그아웃 처리
                change_page("Home")  # 첫 페이지로 이동
                
# 로그인 후 홈화면
def after_login():
    # 타이틀을 중앙에 크게 배치
    st.markdown("<h1 style='text-align: center;'>맛ZIP</h1>", unsafe_allow_html=True)
    # 사용자 정보
    user_id = st.session_state.get("user_id")
    user_password = st.session_state.get("user_password")
    # 로그인 정보 없을 시 처리
    if not user_id:
        st.error("로그인 정보가 없습니다. 다시 로그인해주세요.")
        change_page('Login')
        return

    # 친구 관리 사이드바 추가
    friend_and_group_sidebar(user_id)
    # 데이터베이스 연결
    conn = sqlite3.connect('zip.db')
    cursor = conn.cursor()

    # 사용자 프로필 정보 가져오기
    cursor.execute("SELECT profile_picture_path FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    # 프로필 이미지 경로 설정 (없을 경우 기본 이미지 사용)
    profile_image_url = result[0] if result and result[0] else 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png'
    # 사용자 ID 표시 및 로그아웃 버튼
    signin = SignIn(user_id, user_password)
    col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
    with col1:
        # 프로필 이미지를 클릭하면 페이지 이동
        st.image(profile_image_url, use_container_width=100)
    with col2:
        st.write(f"**{user_id}**")
    with col3:
        signin.log_out_event()
    with col4:
        if st.button("내 프로필", key="profile_button"):
            change_page("Setting")
    if st.button('View Post', key='posting_button'):
        change_page('View Post')
        
    post_manager=PostManager()
    post_manager.display_posts_on_home()


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
    # Only create missing tables, do not recreate existing ones
    Base.metadata.create_all(engine, checkfirst=True)

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

#---------------------------------------------------------------db만들기 ----------------------------



class UserManager:
    def __init__(self, smtp_email, smtp_password, db_url="sqlite:///zip.db"):
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.db_url = db_url
        self.engine = create_engine(self.db_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        """새로운 세션을 생성"""
        return self.Session()

    def is_email_registered(self, email):
        """이메일이 데이터베이스에 등록되어 있는지 확인"""
        session = self.create_session()
        user = session.query(User).filter_by(user_email=email).first()
        session.close()
        return user is not None

    def generate_token(self, length=16):
        """비밀번호 복구를 위한 랜덤 토큰 생성"""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    def send_recovery_email(self, email, token):
        """이메일로 비밀번호 복구 토큰을 전송"""
        subject = "Password Recovery Token"
        body = (
            f"안녕하세요,\n\n"
            f"비밀번호 복구 요청이 접수되었습니다. 아래의 복구 토큰을 사용하세요:\n\n"
            f"{token}\n\n"
            f"이 요청을 본인이 하지 않은 경우, 이 이메일을 무시해 주세요."
        )

        # MIME 메시지 생성
        msg = MIMEMultipart()
        msg['From'] = Header(self.smtp_email, 'utf-8')
        msg['To'] = Header(email, 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()  # 암호화 시작
                connection.login(user=self.smtp_email, password=self.smtp_password)  # 로그인
                connection.sendmail(from_addr=self.smtp_email, to_addrs=email, msg=msg.as_string())  # 이메일 전송
            print(f"Recovery email sent to {email}.")
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def save_recovery_token(self, email, token):
        """토큰을 데이터베이스에 저장"""
        session = self.create_session()
        recovery = PasswordRecovery(user_email=email, token=token)
        session.add(recovery)
        session.commit()
        session.close()

    def verify_token(self, email, token):
        """사용자가 입력한 토큰 검증"""
        session = self.create_session()
        recovery = session.query(PasswordRecovery).filter_by(user_email=email, token=token).first()
        session.close()
        # 토큰이 1시간 이내에 생성된 경우에만 유효
        if recovery and (datetime.utcnow() - recovery.created_at).seconds < 3600:
            return True
        return False

    def reset_password(self, email, new_password):
        """비밀번호를 새로 설정"""
        session = self.create_session()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user = session.query(User).filter_by(user_email=email).first()
        if user:
            user.user_password = hashed_password
            session.commit()
        session.close()

    def recover_password(self, email, new_password, token):
        """토큰을 통해 비밀번호 복구"""
        if not self.verify_token(email, token):
            print("유효하지 않은 토큰입니다.")
            return
        self.reset_password(email, new_password)
        print("비밀번호가 성공적으로 복구되었습니다.")
# 데이터베이스 모델 정의
class User(Base):
    __tablename__ = 'user'
    user_id = Column(String, primary_key=True)
    user_password = Column(String, nullable=False)
    user_email = Column(String, unique=True, nullable=False)
    user_is_online = Column(Boolean, default=False)

#-------------------------------------------------------------로그인---------------------------------------------------
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
    # hashed_password가 문자열이라면 bytes로 변환
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

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
        
    def log_out_event(self):
        # This can be triggered by a logout button
        if st.button("로그아웃", key="logout_button"):
            dao = UserDAO()
            dao.update_user_online(st.session_state["user_id"], 0)  # Set is_online to 0 in D
            st.session_state.user_id = ''  # Clear the session variable
            st.session_state.user_password =''
            st.warning("로그아웃 완료")
            pages.change_page('Home')

class LocationGet:

    # locations 테이블에 저장
    def save_location(self, location_name, address_name, latitude, longitude):
        new_location = Location(
            location_name=location_name,
            address_name=address_name,
            latitude=latitude,
            longitude=longitude
        )
        session.add(new_location)
        session.commit()

    # 저장된 장소들 가져오기
    def get_all_locations(self):
        locations = session.query(Location).all()
        return locations\
        
class LocationSearch:
    def __init__(self):
        self.selected_location_id = None
    
    def search_location(self, query):
        url = f"https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {
            "Authorization": "KakaoAK 6c1cbbc51f7ba2ed462ab5b62d3a3746"  # API 키를 헤더에 포함
        }
        params = {
            "query": query,  # 검색할 장소 이름
            "category_group_code": "SW8,FD6,CE7"  # 카테고리 코드 (예: 음식점, 카페 등)
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])
            if documents:
                return documents
            else:
                st.error("검색 결과가 없습니다.")
                return None
        else:
            st.error(f"API 요청 오류: {response.status_code}")
            return None
    
    def save_or_get_location(self, name, address, latitude, longitude):
        """위치가 존재하는지 확인하고, 없으면 새로 저장"""
        location = self.db_session.query(Location).filter_by(location_name=name, address_name=address).first()
        
        if location:
            return location.location_id  # 이미 존재하면 location_id 반환

        # 새로운 위치 저장
        new_location = Location(
            location_name=name,
            address_name=address,
            latitude=latitude,
            longitude=longitude
        )
        self.db_session.add(new_location)
        self.db_session.commit()
        return new_location.location_id

    def display_location_on_map(self):
        col1, col2 = st.columns([8, 1])
        with col1:
            query = st.text_input("검색할 장소를 입력하세요:", "영남대역")  # 기본값: 영남대역
        with col2:
            st.button("검색")

        if query:
            # 카카오 API로 장소 검색
            results = self.search_location(query)

        if results:
            # 지역 정보 추출
            locations = [(place["place_name"], place["address_name"], float(place["y"]), float(place["x"]))
                        for place in results]

            # 지역 이름 선택
            selected_place = st.selectbox("검색 결과를 선택하세요:", [name for name, _, _, _ in locations])
            location_data = []
            # 선택된 장소의 정보 찾기
            for place in locations:
                if place[0] == selected_place:
                    name, address, latitude, longitude = place

                    # Append to location data
                    location_data.append({
                        'name': name,
                        'address': address,
                        'latitude': latitude,
                        'longitude': longitude
                    })

                    # Display place details
                    col3, col4 = st.columns([4, 1])
                    with col3:
                        st.write(f"장소 이름: {name}")
                        st.write(f"주소: {address}")
                        # 여기서 데이터베이스에 저장
                        self.selected_location_id = self.save_or_get_location(
                            name, address, latitude, longitude)
            if location_data:
                df = pd.DataFrame(location_data)
                st.map(df[['latitude', 'longitude']])

    def get_selected_location_id(self):
        """선택된 location_id를 반환"""
        return self.selected_location_id
   
class PostManager:
    def __init__(self, upload_folder='uploaded_files'):
        self.upload_folder = upload_folder
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        self.locations_df = None
        if "posts" not in st.session_state:
            st.session_state.posts = []
            self.fetch_and_store_posts()

    def save_file(self, file):
        if file:
            file_path = os.path.join(self.upload_folder, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            return file_path
        return ''

    def add_post(self, title, content, image_file, file_file, category):
        location_search=LocationSearch()
        location_id=location_search.get_selected_id
        
        image_path = self.save_file(image_file) if image_file else ''
        file_path = self.save_file(file_file) if file_file else ''
        upload_date = modify_date = datetime.now()

        # Create a new post object
        new_post = Posting(
            p_title=title,
            p_content=content,
            p_image_path=image_path,
            file_path=file_path,
            p_location=location_id,
            p_category=category,
            upload_date=upload_date,
            modify_date=modify_date
        )
        session.add(new_post)
        session.commit()

    def update_post(self, post_id, title, content, image_file, file_file, category):
        post = session.query(Posting).filter_by(p_id=post_id).first()

        if post:
            image_path = self.save_file(image_file) if image_file else post.p_image_path
            file_path = self.save_file(file_file) if file_file else post.file_path
            post.p_title = title
            post.p_content = content
            post.p_image_path = image_path
            post.file_path = file_path
            post.p_category = category
            post.modify_date = datetime.now()
            session.commit()

    def delete_post(self, p_id):
        post = session.query(Posting).filter_by(p_id=p_id).first()
        if post:
            session.delete(post)
            session.commit()

    def get_all_posts(self):
        return session.query(Posting).all()

    def fetch_and_store_posts(self):
        posts = session.query(Posting.p_id, Posting.p_title).all()
        st.session_state.posts = posts

    def toggle_like(self, post_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()
        if post:
            if post.like_num == 1:
                post.like_num = 0
                st.warning("좋아요를 취소했습니다.")
            else:
                post.like_num = 1
                st.success("포스팅을 좋아요 했습니다!")
            session.commit()

    def display_like_button(self, post_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()
        if post:
            btn_label = "좋아요 취소" if post.like_num == 1 else "좋아요"
            if st.button(btn_label, key=post_id, use_container_width=True):
                self.toggle_like(post_id)

    def get_category_options(self):
        return session.query(FoodCategory).all()

    def edit_post(self, post_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()

        if post:
            title = st.text_input("게시물 제목", value=post.p_title, key=f"post_title_{post.p_id}")
            content = st.text_area("게시물 내용", value=post.p_content, key=f"post_content_{post.p_id}")
            image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'], key=f"image_upload_{post.p_id}")
            file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'], key=f"file_upload_{post.p_id}")

            selected_category_name = st.selectbox(
                "카테고리", [category.category for category in self.get_category_options()],
                key=f"category_selectbox_{post.p_id}"
            )
            categories = self.get_category_options()
            category_dict = {category.category: category.category_id for category in categories}
            selected_category_id = category_dict[selected_category_name]

            if st.button("게시물 수정", key=f"button_{post.p_id}", use_container_width=True):
                self.update_post(post_id, title, content, image_file, file_file, selected_category_id)
                st.success("게시물이 수정되었습니다.")
        else:
            st.error("해당 게시물이 존재하지 않습니다.")

    def display_posts(self):
        posts = self.get_all_posts()
        for post in posts:
            st.write(f"Post ID: {post.p_id}, Title: {post.p_title}")
            st.write(f"Content: {post.p_content}")
            if post.p_image_path and os.path.exists(post.p_image_path):
                st.image(post.p_image_path, width=200)
            self.display_like_button(post.p_id)

            # 게시물 삭제 버튼
            if st.button(f"삭제", key=f"delete_{post.p_id}", use_container_width=True):
                self.delete_post(post.p_id)
                st.success(f"게시물 '{post.p_title}'가 삭제되었습니다.")
                return self.display_posts()

            # 게시물 수정 버튼
            with st.expander("수정"):
                self.edit_post(post.p_id)

            st.write(f"**등록 날짜**: {post.upload_date}, **수정 날짜**: {post.modify_date}")
            st.write("---")


            
# 페이지 함수 매핑
page_functions = {
    'Home': home_page,
    'Signup': signup_page,
    'Login': login_page,
    'ID PW 변경': id_pw_change_page,
    'User manager' : usermanager_page,
    'after_login': after_login,
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
    

