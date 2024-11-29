import sqlite3
import streamlit as st
import bcrypt

def init_db():
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
    cursor.execute("""
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

init_db()
#--------------------------페이지-----------------------------------------------

# 데이터베이스 연결 함수
def create_connection():
 conn = sqlite3.connect.connection('zip.db')
 return conn
    

# UserDAO 클래스 (데이터베이스 연동 클래스)
class UserDAO:
 
 # 아이디 존재 여부 체크
 def check_user_id_exists(self, user_id):
     conn = create_connection()
     try:
         # user 테이블에서 user_id에 해당하는 데이터 확인
         result = conn.query("SELECT * FROM user WHERE user_id = ?", params=(user_id,))
         return result if result else None  # 존재하면 해당 결과를 반환
     except Exception as e:
         st.error(f"DB 오류: {e}")
         return None

 # 사용자 등록
 def insert_user(self, user):
     conn = create_connection()

     # 비밀번호 해싱 (bcrypt 사용)
     hashed_password = bcrypt.hashpw(user.user_password.encode('utf-8'), bcrypt.gensalt())

     try:
         # user 테이블에 새 사용자 정보 추가
         query = """
             INSERT INTO user (user_id, user_password, user_email, user_is_online)
             VALUES (?, ?, ?, 0)
         """
         conn.execute(query, (user.user_id, hashed_password, user.user_email))
         conn.commit()
     except Exception as e:
         st.error(f"DB 오류: {e}")
         return
     st.success("회원가입이 완료되었습니다!")

 # 비밀번호 일치 확인
 def check_password(self, hashed_password, plain_password):
     return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

 # 사용자 온라인 상태 업데이트
 def update_user_online(self, user_id, is_online):
     conn = create_connection()
     try:
         # 사용자 온라인 상태를 업데이트
         query = "UPDATE user SET user_is_online = ? WHERE user_id = ?"
         conn.execute(query, (is_online, user_id))
         conn.commit()
     except Exception as e:
         st.error(f"DB 오류: {e}")

# 사용자 정보 VO 클래스
class UserVO:
 def __init__(self, user_id='', user_password='', user_email='', user_is_online=False):
     self.user_id = user_id
     self.user_password = user_password
     self.user_email = user_email
     self.user_is_online = user_is_online

# 회원가입 클래스
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

# 로그인 처리 클래스
class SignIn:
 def __init__(self, user_id, user_password):
     self.user_id = user_id
     self.user_password = user_password
     self.user_is_online = 0

 def sign_in_event(self):
     dao = UserDAO()

     # 사용자 정보를 가져옵니다.
     result = dao.check_user_id_exists(self.user_id)

     if result:
         # result는 튜플 형태 (user_id, user_password, user_email, user_is_online)
         stored_hashed_password = result['user_password']  # result['user_password']은 user_password에 해당
         if dao.check_password(stored_hashed_password, self.user_password):
             st.session_state["user_id"] = self.user_id  # 로그인 성공 시 세션에 user_id 저장
             self.user_is_online = 1
             st.success(f"{self.user_id}님, 로그인 성공!")
             dao.update_user_online(self.user_id, 1)  # 로그인 시 온라인 상태로 업데이트
             return True
         else:
             st.error("비밀번호가 틀렸습니다.")
     else:
         st.error("아이디가 존재하지 않습니다.")
     return False

# 페이지 이동 함수 등은 기존 코드대로 유지

# 로그인 페이지 예시
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
                 st.session_state['user_password'] = user_password  # 비밀번호도 저장
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
