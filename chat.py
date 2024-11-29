import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# SQLAlchemy ORM 설정
Base = declarative_base()

# 메시지 테이블 정의
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

# 데이터베이스 연결 설정 (chat_db.db 파일로 연결)
DATABASE_URL = "sqlite:///chat_db.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 초기화 함수 (테이블 생성)
def init_db():
    if not os.path.exists('chat_db.db'):
        # DB 파일이 존재하지 않으면 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("Database and tables created.")
    else:
        print("Database already exists.")

# 메시지 저장 함수
def save_message(room_name, username, message):
    session = Session()
    timestamp = datetime.now()
    new_message = Message(room_name=room_name, username=username, message=message, timestamp=timestamp)
    session.add(new_message)
    session.commit()
    session.close()

# 채팅 메시지 불러오기 함수
def load_messages(room_name):
    session = Session()
    messages = session.query(Message.username, Message.message, Message.timestamp).filter(Message.room_name == room_name).order_by(Message.timestamp).all()
    session.close()
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
