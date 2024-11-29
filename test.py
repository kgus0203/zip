import streamlit as st
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, func, CheckConstraint
)
from sqlalchemy.orm import sessionmaker
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
import requests

# SQLAlchemy Base 선언
Base = declarative_base()

# 데이터베이스 URL 설정
DATABASE_URL = "sqlite:///zip.db"

# 데이터베이스 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
# -----------------------------------------------페이지 전환 ----------------------------------------------------------


class Page:

    def __init__(self):
        # 세션 상태 초기화
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'Home'

        # TurnPages 클래스 인스턴스 생성
        self.turn_pages = TurnPages(self)

    def render_page(self):
        # 페이지 렌더링
        page_functions = {
            'Home': self.home_page,
            'Login': self.turn_pages.login_page,
            'Signup': self.turn_pages.signup_page,
            'after_login': self.turn_pages.after_login,
            'View Post': self.turn_pages.view_post,
            'Setting': self.turn_pages.setting_page,
            'User manager': self.turn_pages.usermanager_page,
            'ID PW 변경': self.turn_pages.id_pw_change_page,
        }

        # 현재 페이지 렌더링
        if st.session_state.current_page in page_functions:
            page_functions[st.session_state.current_page]()  # 매핑된 함수 호출
        else:
            st.warning(f"페이지 '{st.session_state.current_page}'을 찾을 수 없습니다.")  # 잘못된 페이지 처리

    # 페이지 전환 함수
    def change_page(self, page_name: str):
        # 방문 기록을 세션에 저장
        if "history" not in st.session_state:
            st.session_state["history"] = []

        if st.session_state["current_page"] != page_name:
            # 페이지를 새로 고침 할 때만 history에 추가
            st.session_state["history"].append(st.session_state["current_page"])
            st.session_state["current_page"] = page_name
            st.rerun()  # rerun 호출을 experimental_rerun으로 변경하여 더 안정적으로 동작

    # 뒤로가기 함수
    def go_back(self):
        # 세션에 기록된 이전 페이지로 돌아가기
        if 'history' in st.session_state and st.session_state.history:
            st.session_state.current_page = st.session_state.history.pop()  # 이전 페이지로 이동
            st.rerun()  # 재귀 문제를 피할 수 있는 안정적인 rerun 방식
        else:
            st.warning("이전 페이지가 없습니다.")  # 방문 기록이 없을 경우 처리
            st.rerun()  # 재귀 문제를 피할 수 있는 안정적인 rerun 방식

    # 홈 페이지 함수 (로그인 전)
    def home_page(self):
        col1, col2, col3 = st.columns([1, 1, 1])  # 동일한 너비의 세 개 열 생성
        with col1:
            if st.button("로그인", key="home_login_button"):
                self.change_page('Login')  # 로그인 페이지로 이동
        with col2:
            if st.button("회원가입", key="home_signup_button"):
                self.change_page('Signup')  # 회원가입 페이지로 이동
        with col3:
            if st.button("ID/PW 찾기", key="home_forgot_button"):
                self.change_page('User manager')  # ID/PW 찾기 페이지로 이동


class TurnPages:
    def __init__(self, page: Page):
        self.page = page

    def id_pw_change_page(self):
        st.title("<ID/PW 변경>")

        # 현재 로그인된 사용자 ID 가져오기
        user_id = st.session_state.get('logged_in_user')
        if not user_id:
            st.error("사용자 정보가 없습니다. 다시 로그인해주세요.")
            self.page.change_page('Login')  # 로그인 페이지로 이동
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
                change = ChangeIDPW(
                    user_id=st.session_state['current_user_id'],
                    new_value=new_value
                )
                if st.session_state['action'] == "ID 변경" and change.update_id():
                    st.success("ID가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.")
                    st.session_state.user.clear()  # 세션 초기화로 로그아웃 처리
                    self.page.change_page("Home")  # 첫 페이지로 이동
                elif st.session_state['action'] == "비밀번호 변경" and change.update_password():
                    st.success("비밀번호가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.")
                    st.session_state.user.clear()  # 세션 초기화로 로그아웃 처리
                    self.page.change_page("Home")  # 첫 페이지로 이동


    def login_page(self):
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
                        self.page.change_page('after_login')  # 로그인 후 홈화면으로 이동
                    else:
                        st.error("로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해 주세요.")
        with col2:
            if st.button("뒤로가기", key="login_back_button"):
                self.page.go_back()  # 뒤로가기 로직 호출

    def signup_page(self):
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
                self.page.go_back()  # 뒤로가기 로직 호출

    def after_login(self):
        # 타이틀을 중앙에 크게 배치
        st.markdown("<h1 style='text-align: center;'>맛ZIP</h1>", unsafe_allow_html=True)

        # 사용자 정보
        user_id = st.session_state.get("user_id")

        # 로그인 정보 없을 시 처리
        if not user_id:
            st.error("로그인 정보가 없습니다. 다시 로그인해주세요.")
            self.page.change_page('Login')
            return

        # 사용자 프로필 정보 가져오기
        user = session.query(User).filter(User.user_id == user_id).first()

        session.close()

        # 프로필 이미지 경로 설정 (없을 경우 기본 이미지 사용)
        profile_image_url = user.profile_picture_path if user and user.profile_picture_path else 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png'

        # 사용자 ID 표시 및 로그아웃 버튼
        col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
        with col1:
            # 프로필 이미지를 클릭하면 페이지 이동
            st.image(profile_image_url, use_container_width=True)
        with col2:
            st.write(f"**{user_id}**")
        with col3:
            if st.button("logout_button", key="logout_button"):
                st.warning("logout_success")
                st.session_state.user = ''  # 세션 초기화
                self.page.change_page('Home')
        with col4:
            if st.button("profile_button", key="profile_button"):
                self.page.change_page("Setting")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("view_post_button", key='posting_button'):
                self.page.change_page('View Post')
        with col2:
            if st.button("group_button", key='group_button'):  # 번역 키 "group_button" 사용
                self.page.change_page("Group page")

        # 중앙 포스팅 리스트
        st.title("Recommended Restaurant Posts")

        # PostManager 클래스의 인스턴스 생성 후 display_posts_on_home 호출
        post_manager = PostManager()  # 인스턴스 생성
        post_manager.display_posts_on_home()  # display_posts_on_home 메서드 호출

    # 친구 표시 함수
    def display_friend(self, name, online):
        status_color = "status-on" if online else "status-off"
        st.sidebar.markdown(
            f"""
            <div class="friend-row">
                <span>{name}</span>
                <div class="status-circle {status_color}"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 친구 및 그룹 관리 사이드바
    def friend_and_group_sidebar(self, user_id):
        st.sidebar.title("그룹 관리")  # '그룹 관리'를 title 스타일로 표시
        if st.sidebar.button("그룹 관리"):
            st.session_state["current_page"] = "Group Management"  # 페이지를 'Group Management'로 설정
            st.rerun()  # 페이지 새로고침

        # 친구 관리 상위 요소
        st.sidebar.title("친구 관리")  # '친구 관리'도 title 스타일로 표시
        # 친구찾기 버튼
        if st.sidebar.button("친구찾기"):
            friend_user_id = st.text_input("추가할 친구 ID:")
            if st.button("팔로우 요청 보내기"):
                if friend_user_id:
                    follow_friend(user_id, friend_user_id)
                else:
                    st.error("친구 ID를 입력하세요.")

        # 친구 대기 버튼
        if st.sidebar.button("친구 대기"):
            pending_requests = friend.get_follow_requests(user_id)
            if pending_requests:
                st.subheader("친구 요청 대기 목록")
                for req in pending_requests:
                    st.write(f"요청자: {req['user_id']}")
                    if st.button(f"수락: {req['user_id']}"):
                        friend.handle_follow_request(user_id, req['user_id'], "accept")
                    if st.button(f"거절: {req['user_id']}"):
                        friend.handle_follow_request(user_id, req['user_id'], "reject")
            else:
                st.write("대기 중인 요청이 없습니다.")

        # 차단/해제 버튼
        if st.sidebar.button("차단/해제"):
            blocked_user_id = st.text_input("차단/해제할 친구 ID:")
            if st.button("차단"):
                st.write(f"{blocked_user_id}님을 차단했습니다.")  # 여기에 차단 로직 추가 가능
            if st.button("차단 해제"):
                st.write(f"{blocked_user_id}님 차단을 해제했습니다.")  # 여기에 차단 해제 로직 추가 가능

        # 친구 삭제 버튼
        if st.sidebar.button("삭제"):
            delete_user_id = st.text_input("삭제할 친구 ID:")
            if st.button("삭제 확인"):
                # 삭제 로직 호출
                st.write(f"{delete_user_id}님을 친구 목록에서 삭제했습니다.")  # 여기에 삭제 로직 추가 가능

    def upload_post(self):
        st.header("게시물 등록")
        title = st.text_input("게시물 제목")
        content = st.text_area("게시물 내용")
        image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'])
        file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'])

        # 카테고리 선택을 위한 Selectbox
        post_manager = PostManager('uploads')  # DB 경로 설정
        category_manager=CategoryManager()
        category_names = category_manager.get_category_names()  # 카테고리 이름만 가져옴

        # Selectbox에서 카테고리 선택
        selected_category_name = st.selectbox("카테고리", category_names)

        # 선택한 카테고리 이름에 해당하는 category_id 구하기
        categories = category_manager.get_category_options()
        category_dict = {category[1]: category[0] for category in categories}
        selected_category_id = category_dict[selected_category_name]

        location_search = LocationSearch()
        location_search.display_location_on_map()
        col1, col2 = st.columns([6, 2])
        with col1:
            if st.button("게시물 등록"):
                location_search.add_post(title, content, image_file, file_file, selected_category_id)
                st.success("게시물이 등록되었습니다.")
        with col2:
            if st.button("뒤로가기"):
                self.page.go_back()  # 뒤로가기 로직 호출

    # 세팅 페이지
    def setting_page(self):
        user_id = st.session_state.get("user_id")

        if not user_id:
            st.error("로그인 정보가 없습니다. 다시 로그인해주세요.")
            self.page.change_page('Login')
            return

        try:
            # 사용자 이메일 정보 가져오기
            user = session.query(User).filter(User.user_id == user_id).first()

            if user is None:
                st.error("사용자를 찾을 수 없습니다.")
                self.page.change_page('Login')
                return

            user_email = user.user_email

        finally:
            session.close()

        # 페이지 UI 구성
        col1, col2 = st.columns([8, 2])
        with col1:
            st.title("내 페이지")
        with col2:
            if st.button("뒤로가기"):
                self.page.go_back()

        # 사용자 프로필, 알림 설정 및 테마 버튼을 렌더링하는 뷰 클래스
        view =SetView(user_id, user_email)
        view.render_user_profile()
        view.render_alarm_settings()

        # 테마 관리 버튼
        theme_manager = ThemeManager()
        theme_manager.render_button()

        # 사용자의 게시물 렌더링
        view.render_posts()

    def usermanager_page(self):

        st.title("사용자 관리 페이지")
        email = st.text_input('이메일을 입력하세요: ')

        if st.button("확인", key="forgot_confirm_button"):
            smtp_email = "kgus0203001@gmail.com"  # 발신 이메일 주소
            smtp_password = "pwhj fwkw yqzg ujha"  # 발신 이메일 비밀번호
            user_manager = UserManager(smtp_email, smtp_password)

            # 이메일 등록 여부 확인
            user_info = user_manager.is_email_registered(email)
            if user_info:
                st.success(f"비밀번호 복구 메일을 전송했습니다")
                # 복구 이메일 전송
                user_manager.send_recovery_email(email)
            else:
                st.warning("등록되지 않은 이메일입니다.")

        if st.button("뒤로가기", key="forgot_back_button"):
            # 첫 페이지로 이동
            self.page.change_page("Home")

    # 게시글 목록
    def view_post(self):
        col1, col2, col3 = st.columns([6, 2, 2])  # 비율 6 : 2 : 2
        with col1:
            st.title("게시물 목록")  # 제목을 왼쪽에 배치
        with col2:
            if st.button("뒤로가기"):
                self.page.go_back()  # 뒤로가기 로직 호출
        with col3:
            if st.button("글 작성"):
                self.page.change_page('Upload Post')
        # PostManager 인스턴스를 생성
        post_manager = PostManager()
        # display_posts 메서드를 호출
        post_manager.display_posts()

# -------------------------------------디비-----------------------------------------------------------------------------

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
    id = Column(Integer, primary_key=True)
    current_theme = Column(String, nullable=True, default='dark')

class PasswordRecovery(Base):
    __tablename__ = 'password_recovery'
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 데이터베이스 초기화 및 기본 데이터 삽입
def initialize_database():
    try:
        # 테이블 생성 (앱 실행 시 한 번만)
        Base.metadata.create_all(engine, checkfirst=True)

        # 기본 데이터 삽입 (기본 데이터가 없다면 삽입)
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

    except Exception as e:
        session.rollback()  # 예외 발생 시 롤백
        print(f"Error initializing database: {e}")

    finally:
        session.close()  # 세션 닫기



# ---------------------------------------------------------------db만들기 ----------------------------


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


# -------------------------------------------------------------로그인---------------------------------------------------
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
            st.session_state.user_password = ''
            st.warning("로그아웃 완료")
            change_page('Home')


# ------------------------------------------포스팅---------------------------------

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
        return locations


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
        location = session.query(Location).filter_by(location_name=name, address_name=address).first()

        if location:
            return location.location_id  # 이미 존재하면 location_id 반환

        # 새로운 위치 저장
        new_location = Location(
            location_name=name,
            address_name=address,
            latitude=latitude,
            longitude=longitude
        )
        session.add(new_location)
        session.commit()
        return new_location.location_id

    def display_location_on_map(self):
        col1, col2 = st.columns([8, 1])
        with col1:
            query = st.text_input("검색할 장소를 입력하세요:", "영남대역", key='place')  # 기본값: 영남대역
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
        return self.selected_location_id

    def add_post(self, title, content, image_file, file_file, category):
        location_id = self.get_selected_location_id()  # Get the selected location_id
        post_manager = PostManager()
        image_path = post_manager.save_file(image_file) if image_file else ''
        file_path = post_manager.save_file(file_file) if file_file else ''
        upload_date = modify_date = datetime.now()

        # Create a new post object
        new_post = Posting(
            p_title=title,
            p_content=content,
            p_image_path=image_path,
            file_path=file_path,
            p_location=location_id,  # Foreign key to the location_id
            p_category=category,
            upload_date=upload_date,
            modify_date=modify_date
        )

        # Add the new post to the session and commit the transaction
        session.add(new_post)
        session.commit()


class PostManager:
    def __init__(self, upload_folder='uploaded_files'):
        self.upload_folder = upload_folder
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        self.locations_df = None
        if "posts" not in st.session_state:
            st.session_state.posts = []
            self.fetch_and_store_posts()
        self.category_manager = CategoryManager()

    def save_file(self, file):
        if file:
            file_path = os.path.join(self.upload_folder, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            return file_path
        return ''

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
                st.rerun()
            else:
                post.like_num = 1
                st.success("포스팅을 좋아요 했습니다!")
                st.rerun()
        session.commit()

    def display_like_button(self, post_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()
        if post:
            btn_label = "좋아요 취소" if post.like_num == 1 else "좋아요"
            if st.button(btn_label, key=post_id, use_container_width=True):
                self.toggle_like(post_id)



    def fetch_location_data(self, post_id):
        # Query the database using SQLAlchemy
        location_data = session.query(
            Location.location_name,
            Location.address_name,
            Location.latitude,
            Location.longitude
        ).join(Posting, Posting.p_location == Location.location_id).filter(Posting.p_id == post_id).all()

        # Convert the result to a Pandas DataFrame
        if location_data:
            self.locations_df = pd.DataFrame(location_data,
                                             columns=['location_name', 'address_name', 'latitude', 'longitude'])
        else:
            self.locations_df = pd.DataFrame(columns=['location_name', 'address_name', 'latitude', 'longitude'])

        return self.locations_df

    def create_location_name(self):
        # Check if the DataFrame is empty
        if self.locations_df is None or self.locations_df.empty:
            st.error("위치가 존재하지 않습니다")
            return

        # Display place details
        for index, row in self.locations_df.iterrows():
            name = row['location_name']
            address = row['address_name']
            st.write(f"장소 이름: {name}")
            st.write(f"주소: {address}")

    def display_map(self):

        if self.locations_df is None or self.locations_df.empty:
            st.error("위치 데이터가 없습니다.")
            return

        # Use the latitude and longitude columns to display the map
        st.map(self.locations_df[['latitude', 'longitude']], use_container_width=True)

    def edit_post(self, post_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()

        if post:
            title = st.text_input("게시물 제목", value=post.p_title, key=f"post_title_{post.p_id}")
            content = st.text_area("게시물 내용", value=post.p_content, key=f"post_content_{post.p_id}")
            image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'], key=f"image_upload_{post.p_id}")
            file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'],
                                         key=f"file_upload_{post.p_id}")

            selected_category_name = st.selectbox(
                "카테고리", [category.category for category in self.category_manager.get_category_options()],
                key=f"category_selectbox_{post.p_id}"
            )
            categories = self.category_manager.get_category_options()
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

            self.fetch_location_data(post.p_id)

            # 위치 데이터가 존재할 때만 지도 생성
            if self.locations_df is not None and not self.locations_df.empty:
                self.create_location_name()
                st.title("Location Map")
                self.display_map()

            st.write(f"**등록 날짜**: {post.upload_date}, **수정 날짜**: {post.modify_date}")
            st.write("---")

    def display_post(self, post_id):
        # 특정 게시물 가져오기
        post = self.get_post_by_id(post_id)

        if post:
            # 게시물 정보 출력
            st.write(f"**Post ID**: {post['p_id']}")
            st.write(f"**Title**: {post['p_title']}")
            st.write(f"**Content**: {post['p_content']}")

            # 이미지 출력
            if post.get('p_image_path') and os.path.exists(post['p_image_path']):
                st.image(post['p_image_path'], width=200)

            # 파일 출력
            if post.get('file_path') and os.path.exists(post['file_path']):
                st.write("**Filename**:", os.path.basename(post['file_path']))
                st.write(f"**File size**: {os.path.getsize(post['file_path'])} bytes")
                st.markdown(
                    f"[Download File]({post['file_path']})",
                    unsafe_allow_html=True
                )

        else:
            st.error("해당 게시물을 찾을 수 없습니다.")

    def get_post_by_id(self, post_id):
        # Query the Posting table using SQLAlchemy's ORM query
        post = session.query(Posting).filter_by(p_id=post_id).first()

        # If the post exists, convert it to a dictionary, else return None
        if post:
            return {
                "p_id": post.p_id,
                "p_title": post.p_title,
                "p_content": post.p_content,
                "p_image_path": post.p_image_path,
                "file_path": post.file_path,
                "p_location": post.p_location,
                "p_category": post.p_category,
                "like_num": post.like_num,
                "file": post.file,
                "upload_date": post.upload_date,
                "modify_date": post.modify_date
            }
        else:
            return None

    def display_posts_on_home(self):
        # 데이터베이스에서 포스팅 데이터를 가져옵니다.
        posts = self.get_all_posts()

        if not posts:
            st.write("현재 추천 포스팅이 없습니다.")
            return

        # 포스트를 두 개씩 나열
        for i in range(0, len(posts), 2):
            cols = st.columns(2)  # 두 개의 컬럼 생성
            for j, col in enumerate(cols):
                if i + j < len(posts):
                    post = posts[i + j]  # 현재 포스트 데이터
                    with col:
                        st.subheader(post.p_title)
                        self.fetch_location_data(post.p_id)

                        # 이미지 출력 (있는 경우)
                        if post.p_image_path:
                            self.create_location_name()
                            st.image(post.p_image_path, use_container_width=True)

                        with st.expander('더보기'):
                            self.display_post(post.p_id)


# ----------------------------------------------------카테고리 -----------------------------
class CategoryManager:
    def get_category_options(self):
        return session.query(FoodCategory).all()

    def get_category_names(self):
        categories = self.get_category_options()
        category_dict = {category.category: category.category_id for category in categories}
        return category_dict


# -------------------------------------------------테마----------------------------------------------


class ThemeManager:
    def __init__(self):
        self.th = st.session_state
        # Ensure the themes dictionary exists in the session state
        if "themes" not in self.th:
            self.th.themes = {
                "current_theme": self.get_saved_theme(),  # Load saved theme from DB or default to dark
                "light": {
                    "theme.base": "dark",
                    "theme.backgroundColor": "black",
                    "theme.textColor": "white",
                    "button_face": "어두운 모드 🌜"
                },
                "dark": {
                    "theme.base": "light",
                    "theme.backgroundColor": "white",
                    "theme.textColor": "#0a1464",
                    "button_face": "밝은 모드 🌞"
                }
            }

    def get_saved_theme(self):
        setting = session.query(Settings).filter(Settings.id == 1).first()
        session.close()

        return setting.current_theme if setting and setting.current_theme in ["light", "dark"] else 'dark'

    def save_theme(self, theme):
        setting = session.query(Settings).filter(Settings.id == 1).first()

        if setting:
            setting.current_theme = theme
        else:
            setting = Settings(id=1, current_theme="light")
            session.add(setting)

        session.commit()
        session.close()

    def change_theme(self):
        previous_theme = self.th.themes["current_theme"]
        new_theme = "light" if previous_theme == "dark" else "dark"

        # Ensure the new theme exists in the themes dictionary
        if new_theme not in self.th.themes:
            st.error(f"Theme '{new_theme}' not found in theme dictionary")
            return

        theme_dict = self.th.themes[new_theme]

        # Apply the new theme settings
        for key, value in theme_dict.items():
            if key.startswith("theme"):
                st._config.set_option(key, value)

        # Save the new theme in the database and update session state
        self.save_theme(new_theme)
        self.th.themes["current_theme"] = new_theme

    def render_button(self):
        """ Render the theme toggle button """
        # Ensure the current theme exists in the session state
        current_theme = self.th.themes.get("current_theme", "dark")  # Default to 'dark' if missing
        button_label = self.th.themes.get(current_theme, {}).get("button_face",
                                                                 "Unknown theme")  # Default label if missing

        # Render the button and handle the click event
        if st.button(button_label, use_container_width=True,key='change_theme'):
            self.change_theme()
            st.rerun()


# ---------------------------- 유저 프로필 ---------------------------------
class UserProfile:
    def __init__(self, upload_folder="profile_pictures"):
        self.upload_folder = upload_folder

        # Default profile picture URL
        self.default_profile_picture = (
            "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        )

        # Attempt to create the directory
        os.makedirs(self.upload_folder, exist_ok=True)

    def save_file(self, uploaded_file):
        if uploaded_file:
            file_path = os.path.join(self.upload_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        return None

    def get_user_profile(self, user_id):
        """사용자의 프로필 정보를 데이터베이스에서 조회"""
        return session.query(User).filter_by(user_id=user_id).first()

    def update_profile_picture(self, user_id, image_path):
        """사용자의 프로필 사진 경로를 업데이트"""
        user = self.get_user_profile(user_id)
        if user:
            user.profile_picture_path = image_path
            session.commit()

    def display_profile(self, user_id):
        """사용자 프로필 표시"""
        user = self.get_user_profile(user_id)
        if user:
            st.write(f"User Email: {user.user_email}")
            profile_picture = user.profile_picture_path

            # 프로필 사진 경로가 없거나 파일이 존재하지 않으면 기본 이미지 사용
            if not profile_picture or not os.path.exists(profile_picture):
                profile_picture = self.default_profile_picture

            st.image(profile_picture, caption=user_id, width=300)
        else:
            st.error("사용자 정보를 찾을 수 없습니다.")

    def upload_new_profile_picture(self, user_id):
        """새 프로필 사진 업로드 및 저장"""
        st.button("프로필 사진 변경", use_container_width=True,key='change_profile')
        uploaded_file = st.file_uploader("새 프로필 사진 업로드", type=["jpg", "png", "jpeg"])

        if st.button("업로드",key='upload'):
            if uploaded_file:
                image_path = self.save_file(uploaded_file)
                self.update_profile_picture(user_id, image_path)
                st.success("프로필 사진이 성공적으로 업데이트되었습니다.")
            else:
                st.error("파일을 업로드해주세요.")


class Account:
    def __init__(self,user_id):
        self.user_id=user_id
    def update_email(self, new_email: str):
        """Update the user's email in the database."""
        user = session.query(User).filter_by(user_id=self.user_id).first()
        if user:
            user.user_email = new_email
            session.commit()
        else:
            raise ValueError("User not found")


class SetView:
    def __init__(self, user_id, user_email):
        self.dao=Account
        self.user_id = user_id
        self.user_email = user_email
        self.user_profile = UserProfile()
        self.theme_manager = ThemeManager()
        self.like_button = LikeButton()

    def render_alarm_settings(self):

        alarm_enabled = st.button("알람 설정", use_container_width=True,key='alarm')
        if alarm_enabled:
            st.write("알람이 설정되었습니다.")
        else:
            st.write("알람이 해제되었습니다.")

    def render_user_profile(self):
        st.write(self.user_id)
        st.write(self.user_email)
        # Edit Profile Button (popup simulation)
        with st.expander("내 정보 수정하기"):
            # Change Email
            new_email = st.text_input("새 이메일 주소", value=self.user_email)
            if st.button("이메일 변경",key='change_email'):
                self.account.update_email(new_email)
                st.success("이메일이 변경되었습니다.")

            # Profile Picture Upload
            uploaded_file = st.file_uploader("새 프로필 사진 업로드", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image_path = self.user_profile.save_file(uploaded_file)
                self.user_profile.update_profile_picture(self.user_id, image_path)
                st.success("프로필 사진이 성공적으로 업데이트되었습니다.")
                st.rerun()

    def render_posts(self):
        with st.expander('관심목록', icon='💗'):
            self.like_button.display_liked_posts()


# -----------------------------------------------------좋아요 목록 --------------------------------------------------------------

class LikeButton:
    def __init__(self):
        if "posts" not in st.session_state:
            st.session_state.posts = []
            self.fetch_and_store_posts()

    def fetch_liked_posts(self):
        liked_posts = session.query(Posting.p_content, Posting.p_title).filter(Posting.like_num > 0).all()
        session.close()
        return [(post.p_title, post.p_content) for post in liked_posts]

    def display_liked_posts(self):
        liked_posts = self.fetch_liked_posts()
        # Display liked posts with the like button
        if liked_posts:
            for post in liked_posts:
                post_content, post_title = post
                st.write(f"Title: {post_title}, content : {post_content}")
        else:
            st.write("좋아요를 누른 포스팅이 없습니다.")



app = Page()
app.render_page()
