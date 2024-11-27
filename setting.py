import streamlit as st
import sqlite3
from typing import Dict
import os

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

def create_connection():
    conn = sqlite3.connect('zip.db')
    conn.row_factory = sqlite3.Row  # results as dictionary-like
    return conn
class LikeButton:
   def __init__(self):
       self.lk = st.session_state
       if "like" not in self.lk:
           self.lk.like = {
               "current_like": "not_like",
               "refreshed": True,
               "not_like": {
                   "theme.base": "like",
                   "button_face": "좋아요 취소"
               },
               "like": {
                   "theme.base": "not_like",
                   "button_face": "좋아요"
               },
           }
       if "posts" not in st.session_state:
           st.session_state.posts = []
           self.fetch_and_store_posts()


   def create_connection(self):
       """ Create a SQLite database connection. """
       conn = sqlite3.connect('zip.db')
       conn.row_factory = sqlite3.Row  # Return results as dictionaries
       return conn


   def fetch_and_store_posts(self):
       """ Fetch all posts from the database and store them in session state. """
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT p_id, p_title FROM posting")
       posts = cursor.fetchall()
       conn.close()


       # Store the posts in session state
       st.session_state.posts = posts


   def fetch_liked_posts(self):
       """ Fetch only posts with likes (like_num > 0). """
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT p_id, p_title FROM posting WHERE like_num > 0")
       liked_posts = cursor.fetchall()
       conn.close()


       return liked_posts


   def toggle_like(self, post_id):
       """ Toggle like/unlike for a post based on its current like status. """
       conn = self.create_connection()
       cursor = conn.cursor()


       # Check current like status for the post
       cursor.execute("SELECT like_num FROM posting WHERE p_id = ?", (post_id,))
       result = cursor.fetchone()


       if result:
           if result[0] == 1:
               # Unlike the post
               cursor.execute("UPDATE posting SET like_num = like_num - 1 WHERE p_id = ?", (post_id,))
               st.warning("좋아요를 취소했습니다.")
           else:
               # Like the post again
               cursor.execute("UPDATE posting SET like_num = like_num + 1 WHERE p_id = ?", (post_id,))
               st.success("포스팅을 좋아요 했습니다!")
       else:
           # If the post doesn't exist or hasn't been liked yet
           cursor.execute("UPDATE posting SET like_num = 1 WHERE p_id = ?", (post_id,))
           st.success("포스팅을 좋아요 했습니다!")


       conn.commit()
       conn.close()


   def change_like(self):
       """ Toggle the 'like' theme between 'like' and 'not_like'. """
       previous_like = self.lk.like["current_like"]


       # Toggle between "like" and "not_like" themes
       like_key = "not_like" if self.lk.like["current_like"] == "not_like" else "like"
       like_dict = self.lk.like[like_key]


       # Update Streamlit theme options
       for vkey, vval in like_dict.items():
           if vkey.startswith("like"):
               st._config.set_option(vkey, vval)


       # Toggle current like state
       self.lk.like["refreshed"] = False
       self.lk.like["current_like"] = "like" if previous_like == "not_like" else "not_like"


   def render_button(self, post_id):
       """ Display the like/unlike button and handle its functionality. """
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT like_num FROM posting WHERE p_id = ?", (post_id,))
       result = cursor.fetchone()
       conn.close()


       if result:
           current_like_count = result[0]
           button_label = self.lk.like["like"]["button_face"] if current_like_count == 1 else self.lk.like["not_like"][
               "button_face"]
       else:
           button_label = self.lk.like["not_like"]["button_face"]


       # Display the button and trigger like/unlike on click
       st.button(button_label, on_click=self.toggle_like, args=(post_id,))


       # Refresh if necessary
       if self.lk.like["refreshed"] == False:
           self.lk.like["refreshed"] = True
           st.rerun()


   def display_posts(self):
       """ Display all posts and their corresponding like buttons. """
       posts = st.session_state.posts


       # Display posts with the like button
       for post in posts:
           post_id, post_title = post
           st.write(f"Post ID: {post_id}, Title: {post_title}")
           self.render_button(post_id)


   def display_liked_posts(self):
       """ Display only liked posts (like_num > 0). """
       liked_posts = self.fetch_liked_posts()


       # Display liked posts with the like button
       if liked_posts:
           for post in liked_posts:
               post_id, post_title = post
               st.write(f"Liked Post ID: {post_id}, Title: {post_title}")
       else:
           st.write("좋아요를 누른 포스팅이 없습니다.")




class Account:
    def __init__(self, user_id, user_email):
        self.user_id = user_id
        self.user_email = user_email

    def get_user_info(self) -> Dict:
        return {"user_id": self.user_id, "user_email": self.user_email}

    def update_email(self, new_email: str):
        # 실제 데이터베이스에서 이메일 업데이트
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET user_email = ? WHERE user_id = ?", (new_email, self.user_id))
        conn.commit()


class ThemeManager:
    def __init__(self):
        self.th = st.session_state
        if "themes" not in self.th:
            self.th.themes = {
                "current_theme": self.get_saved_theme(),  # Load saved theme from DB or default to light
                "light": {
                    "theme.base": "dark",
                    "theme.backgroundColor": "black",
                    "theme.primaryColor": "#c98bdb",
                    "theme.secondaryBackgroundColor": "#5591f5",
                    "theme.textColor": "white",
                    "button_face": "어두운 모드 🌜"
                },
                "dark": {
                    "theme.base": "light",
                    "theme.backgroundColor": "white",
                    "theme.primaryColor": "#5591f5",
                    "theme.secondaryBackgroundColor": "#82E1D7",
                    "theme.textColor": "#0a1464",
                    "button_face": "밝은 모드 🌞"
                }
            }

    def get_saved_theme(self):
        # 저장된 테마 가져오기
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT current_theme FROM settings WHERE id=1')
        theme = cursor.fetchone()
        conn.close()
        return theme[0] if theme else 'light'

    def save_theme(self, theme):
        # 현재 테마를 데이터베이스에 저장
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE settings SET current_theme=? WHERE id=1', (theme,))
        conn.commit()
        conn.close()

    def change_theme(self):
        # 테마 변경
        previous_theme = self.th.themes["current_theme"]
        new_theme = "light" if previous_theme == "dark" else "dark"

        # 테마 적용
        theme_dict = self.th.themes[new_theme]
        for key, value in theme_dict.items():
            if key.startswith("theme"):
                st._config.set_option(key, value)

        # 데이터베이스 저장 및 세션 상태 업데이트
        self.save_theme(new_theme)
        self.th.themes["current_theme"] = new_theme
        st.rerun()  # UI 새로고침

    def render_button(self):
        current_theme = self.th.themes["current_theme"]
        button_label = self.th.themes[current_theme]["button_face"]

        # 버튼 렌더링 및 클릭 이벤트 처리
        if st.button(button_label, use_container_width=True):
            self.change_theme()



class UserProfile:
    def __init__(self, upload_folder="profile_pictures"):
        self.db_name = 'zip.db'
        self.upload_folder = upload_folder
        self.default_profile_picture = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        os.makedirs(self.upload_folder, exist_ok=True)

    def create_connection(self):
        """SQLite 데이터베이스 연결 생성"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환
        return conn

    def save_file(self, uploaded_file):
        # 이미지 저장 후 경로 반환
        if uploaded_file is not None:
            file_path = os.path.join(self.upload_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        return None

    # 사용자 이미지 가져오기
    def get_user_profile(self, user_id):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        connection.close()
        return user

    # 프로필 업데이트
    def update_profile_picture(self, user_id, image_path):
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute("""
        UPDATE user
        SET profile_picture_path = ?
        WHERE user_id = ?
        """, (image_path, user_id))
        connection.commit()
        connection.close()

    def display_profile(self, user_id):
        user = self.get_user_profile(user_id)
        if user:
            st.write(f"User Email: {user['user_email']}")
            profile_picture = user['profile_picture_path']

            # 파일이 없거나 경로가 잘못된 경우 기본 이미지로 대체
            if not profile_picture or not os.path.exists(profile_picture):
                profile_picture = self.default_profile_picture

            st.image(profile_picture, caption=user_id, width=300)
        else:
            st.error("사용자 정보를 찾을 수 없습니다.")

    def upload_new_profile_picture(self, user_id):
        st.button("프로필 사진 변경", use_container_width=True)
        uploaded_file = st.file_uploader("새 프로필 사진 업로드", type=["jpg", "png", "jpeg"])

        if st.button("업로드"):
            if uploaded_file is not None:
                image_path = self.save_file(uploaded_file)
                self.update_profile_picture(user_id, image_path)
                st.success("프로필 사진이 성공적으로 업데이트되었습니다.")
                st.rerun()
            else:
                st.error("파일을 업로드해주세요.")


# SetView class to handle UI rendering
class SetView:
    def __init__(self):
        self.account = Account(user_id="default_user", user_email="default@example.com")
        self.user_profile = UserProfile()
        self.theme_manager = ThemeManager()
        self.like_button = LikeButton()

    def render_user_profile(self):
        user_info = self.account.get_user_info()
        # Display user profile
        self.user_profile.display_profile(user_info["user_id"])

        # Edit Profile Button (popup simulation)
        with st.expander("내 정보 수정하기"):
            # Change Email
            new_email = st.text_input("새 이메일 주소", value=user_info["user_email"])
            if st.button("이메일 변경"):
                self.account.update_email(new_email)
                st.success("이메일이 변경되었습니다.")

            # Profile Picture Upload
            uploaded_file = st.file_uploader("새 프로필 사진 업로드", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image_path = self.user_profile.save_file(uploaded_file)
                self.user_profile.update_profile_picture(user_info["user_id"], image_path)
                st.success("프로필 사진이 성공적으로 업데이트되었습니다.")
                st.rerun()

    def render_alarm_settings(self):

        alarm_enabled = st.button("알람 설정", use_container_width=True)
        if alarm_enabled:
            st.write("알람이 설정되었습니다.")
        else:
            st.write("알람이 해제되었습니다.")



    def render_posts(self):
        # Display liked posts toggle button

        with st.expander('관심목록',icon='💗'):
            self.like_button.display_liked_posts()


# Main function
def main():
    st.title("My Page")

    # Create the SetView object and render the views
    view = SetView()
    view.render_user_profile()
    view.render_alarm_settings()
    theme_manager = ThemeManager()
    theme_manager.render_button()

    view.render_posts()


if __name__ == "__main__":
    main()
