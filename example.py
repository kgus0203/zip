import sqlite3
import streamlit as st
import bcrypt

def create_db():
   conn = sqlite3.connect('zip.db')
   cursor = conn.cursor()


   # user 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS user (
       user_id TEXT PRIMARY KEY,
       user_password TEXT NOT NULL,
       user_email TEXT NOT NULL,
       user_is_online INTEGER DEFAULT 0,
       user_mannerscore INTEGER DEFAULT 0,
       profile_picture_path TEXT
   )
   """)
   cursor.execute("""
      INSERT OR IGNORE INTO user (user_id, user_password, user_email, profile_picture_path)
      VALUES (?, ?, ?, ?)
      """, ('default_user', 'default_password', 'default@example.com',
            'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png'))


   # friend 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS friend (
       friend_id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id TEXT NOT NULL,
       friend_user_id TEXT NOT NULL,
       status TEXT NOT NULL,
       FOREIGN KEY (user_id) REFERENCES user(user_id),
       FOREIGN KEY (friend_user_id) REFERENCES user(user_id)
   )
   """)


   # groups 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS "group" (
       group_id INTEGER PRIMARY KEY AUTOINCREMENT,
       group_name TEXT UNIQUE NOT NULL,
       group_creator TEXT NOT NULL,
       category INTEGER,
       date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
       location INTEGER,
       meeting_date TEXT,
       meeting_time TEXT,
       status TEXT DEFAULT '진행 중',
       update_date TEXT NOT NULL,
       modify_date TEXT NOT NULL,
       FOREIGN KEY (group_creator) REFERENCES user(user_id),
       FOREIGN KEY (category) REFERENCES food_categories(category_id),
       FOREIGN KEY (location) REFERENCES locations(location_id)
   )
   """)


   # group_member 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS group_member (
       group_member_id INTEGER PRIMARY KEY AUTOINCREMENT,
       group_id TEXT NOT NULL,
       user_id TEXT NOT NULL,
       role TEXT DEFAULT 'member' CHECK (role IN ('admin', 'member')),
       joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (group_id) REFERENCES "group"(group_id),
       FOREIGN KEY (user_id) REFERENCES user(user_id)
   )
   """)


   # food_categories 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS food_categories (
       category_id INTEGER PRIMARY KEY AUTOINCREMENT,
       category TEXT UNIQUE NOT NULL
   )
   """)

   # Insert predefined food categories
   cursor.executemany("""
   INSERT OR IGNORE INTO food_categories (category) VALUES (?)
   """, [
      ("한식",),
      ("중식",),
      ("양식",),
      ("일식",),
      ("디저트",),
      ("패스트푸드",)
   ])



   # locations 테이블
   cursor.execute("""   CREATE TABLE IF NOT EXISTS locations (
       location_id INTEGER PRIMARY KEY AUTOINCREMENT,
       location_name TEXT NOT NULL,
       address_name TEXT NOT NULL,
       latitude REAL NOT NULL,
       longitude REAL NOT NULL
   )
   """)


   # messages 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS messages (
       message_id INTEGER PRIMARY KEY AUTOINCREMENT,
       group_id INTEGER NOT NULL,
       sender_id TEXT NOT NULL,
       message_text TEXT NOT NULL,
       sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (group_id) REFERENCES "group"(group_id),
       FOREIGN KEY (sender_id) REFERENCES user(user_id)
   )
   """)


   # posting 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS posting (
       p_id INTEGER PRIMARY KEY AUTOINCREMENT,
       p_title TEXT NOT NULL,
       p_content TEXT NOT NULL,
       p_image_path TEXT,
       file_path TEXT,
       p_location INTEGER,
       p_category INTEGER,
       like_num INTEGER DEFAULT 0,
       file BLOB,
       upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
       modify_date DATETIME DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (p_location) REFERENCES locations(location_id),
       FOREIGN KEY (p_category) REFERENCES food_categories(category_id)
   )
   """)
   cursor.execute('''
       CREATE TABLE IF NOT EXISTS settings (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           current_theme TEXT
       );
   ''')


   conn.commit()
   conn.close()


create_db()
#--------------------------페이지-----------------------------------------------

# 데이터베이스 연결 함수
def create_connection():
    conn = sqlite3.connect('zip.db')
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형식으로 반환
    return conn

# 시작은 홈화면
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

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
               
#-----------------------------------------로그인--------------------------------------------------------   
# UserDAO (데이터베이스 연동 클래스)
class UserDAO:

    def check_user_id_exists(self, user_id):
        connection = create_connection()
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM user WHERE user_id = ?"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result is not None
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()

    def insert_user(self, user):
        connection = create_connection()

        # 비밀번호 해싱 (bcrypt 사용)
        hashed_password = bcrypt.hashpw(user.user_password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor = connection.cursor()
            query = "INSERT INTO user (user_id, user_password, user_email, user_is_online) VALUES (?, ?, ?, 0)"
            cursor.execute(query, (user.user_id, hashed_password, user.user_email))
            connection.commit()
        except sqlite3.IntegrityError as e:  # UNIQUE 제약 조건으로 발생하는 오류 처리
            if "user_email" in str(e):
                st.error("이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요.")
            elif "user_id" in str(e):
                st.error("이미 사용 중인 아이디입니다. 다른 아이디를 사용해주세요.")
            else:
                st.error("회원가입 중 알 수 없는 오류가 발생했습니다.")
            return  # 예외 발생 시 함수 종료
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
            return  # 예외 발생 시 함수 종료
        finally:
            connection.close()

        # 회원가입 성공 메시지 (오류가 없을 경우에만 실행)
        st.success("회원가입이 완료되었습니다!")


    #해시알고리즘을 이용하여 비밀번호 일치 확인
    def check_password(self, hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
   
    def update_user_online(self,user_id,is_online):
        connection = create_connection()
        try:
            cursor = connection.cursor()
            query = "UPDATE user SET user_is_online = 1 WHERE user_is_online=? user_id = ?"
            cursor.execute(query, (user_id, is_online))
            connection.commit()
        except sqlite3.Error as e:
            st.error(f"DB 오류: {e}")
        finally:
            connection.close()


# UserVO (사용자 정보 클래스)
class UserVO:
    def __init__(self, user_id='', user_password='', user_email='', user_seq=None, user_is_online=False):
        self.user_id = user_id
        self.user_password = user_password
        self.user_email = user_email
        self.user_seq = user_seq
        self.user_is_online = user_is_online


class SignUp:
    def __init__(self, user_id, user_password, user_email):
        self.user = UserVO(user_id=user_id, user_password=user_password, user_email=user_email)
    def sign_up_event(self):
        dao = UserDAO()
        dao.insert_user(self.user)
    def check_length(self):
        if len(self.user.user_password) < 8:
            st.error("비밀번호는 최소 8자 이상이어야 합니다.")
            return False
        return True
    def check_user(self):
        dao = UserDAO()
        if dao.check_user_id_exists(self.user.user_id):
            st.error("이미 사용 중인 아이디입니다.")
            return False
        return True
    @st.cache_data
    def return_user(self):
       return self.user_id
       
# 로그인 처리 클래스
class SignIn:
    def __init__(self, user_id, user_password):
        self.user_id = user_id
        self.user_password = user_password
        self.user_is_online=0

    def sign_in_event(self):
        dao = UserDAO()
        result = dao.check_user_id_exists(self.user_id)

        if result:
            # 저장된 해시된 비밀번호 가져오기
            stored_hashed_password = result['user_password']  # result는 딕셔너리 형태
            if dao.check_password(stored_hashed_password, self.user_password):  # bcrypt로 비밀번호 비교
                st.session_state["user_id"] = self.user_id  # 로그인 성공 시 세션에 user_id 저장
                self.user_is_online = 1
                change_page('Home')
                return True
            else:
                st.error("비밀번호가 잘못되었습니다.")
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
            change_page('Home')

#-------------------------------------------------------------페이지 이동 -------------------------------------------------------------

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
              else:
                  st.error("로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해 주세요.")
  with col2:
      if st.button("뒤로가기", key="login_back_button"):
         go_back()  # 뒤로가기 로직 호출


# 페이지 함수 매핑
page_functions = {
    'Home': home_page,
    'Signup': signup_page,
    'Login': login_page,
}

# 현재 페이지 디버깅
st.write(f"Current Page: {st.session_state['current_page']}")  # 디버깅용 코드

# 현재 페이지 렌더링
if st.session_state["current_page"] in page_functions:
    page_functions[st.session_state["current_page"]]()  # 매핑된 함수 호출
else:
    st.error(f"페이지 {st.session_state['current_page']}를 찾을 수 없습니다.")
