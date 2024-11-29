import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


# SQLite 데이터베이스 연결
def init_db():
    conn = sqlite3.connect('zip.db')
    cursor = conn.cursor()

    # 채팅 메시지를 저장할 테이블 생성
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_name TEXT,
                        username TEXT,
                        message TEXT,
                        timestamp DATETIME)''')
    conn.commit()
    conn.close()


# 메시지 저장 함수
def save_message(room_name, username, message):
    conn = sqlite3.connect('zip.db')
    cursor = conn.cursor()
    timestamp = datetime.now()
    cursor.execute("INSERT INTO messages (room_name, username, message, timestamp) VALUES (?, ?, ?, ?)",
                   (room_name, username, message, timestamp))
    conn.commit()
    conn.close()


# 채팅 메시지 불러오기 함수
def load_messages(room_name):
    conn = sqlite3.connect('zip.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, message, timestamp FROM messages WHERE room_name = ? ORDER BY timestamp",
                   (room_name,))
    messages = cursor.fetchall()
    conn.close()
    return messages


# Streamlit 앱 구성
def main():
    st.title('채팅 시스템')

    # 채팅 룸 이름 입력
    room_name = st.text_input("채팅 룸 이름", "General")

    if room_name:
        # 유저 이름 입력
        username = st.text_input("이름을 입력하세요", "사용자")

        # 메시지 입력
        message = st.text_input("메시지를 입력하세요")

        if st.button("보내기"):
            if message:
                save_message(room_name, username, message)
                st.success("메시지가 전송되었습니다.")
            else:
                st.warning("메시지를 입력해주세요.")

        # 채팅 메시지 불러오기
        messages = load_messages(room_name)

        # 메시지 표시
        for msg in messages:
            st.write(f"**{msg[0]}** ({msg[2]}): {msg[1]}")


if __name__ == "__main__":
    init_db()  # DB 초기화
    main()  # 앱 실행
