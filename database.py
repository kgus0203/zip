import sqlite3
#들여쓰기 맞춰두었습니다

def create_db():
   conn = sqlite3.connect('zip.db')
   cursor = conn.cursor()


   # user 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS user (
       user_seq INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id TEXT NOT NULL,
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


    # friend 테이블 (친구 목록)
   cursor.execute("""
    CREATE TABLE IF NOT EXISTS friend (
        friend_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        friend_user_id TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        FOREIGN KEY (friend_user_id) REFERENCES user(user_id)
    )
    """)
   cursor.execute("""
               CREATE TABLE IF NOT EXISTS password_recovery (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_email TEXT NOT NULL,
                   token TEXT NOT NULL,
                   created_at TEXT NOT NULL
               )
           """)

   cursor.execute("""
                  CREATE TABLE IF NOT EXISTS like (
                      like_id INTEGER PRIMARY KEY ,
                      user_id TEXT NOT NULL,
                      post_id INTEGER NOT NULL,
                      FOREIGN KEY (user_id) REFERENCES user(user_id),
                      FOREIGN KEY (post_id) REFERENCES posting(p_id)
                      
                  )
              """)
    # block 테이블 (차단 목록)
   cursor.execute("""
    CREATE TABLE IF NOT EXISTS block (
        block_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        blocked_user_id TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        FOREIGN KEY (blocked_user_id) REFERENCES user(user_id)
    )
    """)

    # myFriendrequest 테이블 (내가 보낸 친구 신청 목록)
   cursor.execute("""
    CREATE TABLE IF NOT EXISTS myFriendrequest (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        requested_user_id TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        FOREIGN KEY (requested_user_id) REFERENCES user(user_id)
    )
    """)

    # otherRequest 테이블 (다른 사람이 보낸 친구 신청 목록)
   cursor.execute("""
    CREATE TABLE IF NOT EXISTS otherRequest (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        requester_user_id TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(user_id),
        FOREIGN KEY (requester_user_id) REFERENCES user(user_id)
    )
    """)



   # groups 테이블
   cursor.execute("""
   CREATE TABLE IF NOT EXISTS "group" (
       group_id INTEGER PRIMARY KEY AUTOINCREMENT,
       group_name TEXT UNIQUE NOT NULL,
       group_creator TEXT NOT NULL,
       category INTEGER,
       date DATETIME DEFAULT CURRENT_TIMESTAMP,
       location INTEGER,
       meeting_date DATE DEFAULT CURRENT_DATE,
       meeting_time TIME DEFAULT CURRENT_TIME,
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
       joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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
       p_user TEXT NOT NULL, 
       p_title TEXT NOT NULL,
       p_content TEXT NOT NULL,
       p_image_path TEXT,
       file_path TEXT,
       p_location INTEGER,
       p_category INTEGER,
       like_num INTEGER DEFAULT 0,
       total_like_num INTEGER DEFAULT 0,
       file BLOB,
       upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
       modify_date DATETIME DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (p_location) REFERENCES locations(location_id),
       FOREIGN KEY (p_category) REFERENCES food_categories(category_id),
       FOREIGN KEY (p_user) REFERENCES user(user_id)
   )
   """)
   cursor.execute('''
       CREATE TABLE IF NOT EXISTS settings (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user TEXT NOT NULL,
           current_theme TEXT,
           FOREIGN KEY (user) REFERENCES user(user_id)
       );
   ''')


   conn.commit()
   conn.close()


create_db()
