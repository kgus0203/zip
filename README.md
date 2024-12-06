# 소프트웨어 공학 Testing 과제
[Team 맛ZIP]
제출 파일 : app.txt(전체 코드) ,zip.db , ReadMe.txt + SRS_맛집.XLSX, SDS_맛집.PDF

팀원: 이아현 남지인 김영준 이상원 이기준

## 👨‍🏫프로젝트 소개
맛집 소개 포스팅을 할 수 있고 식사하러 갈 사람을 모집할 수 있는 사이트입니다.

## 📌주요기능
- 로그인 
- 맛집 포스팅 작성 및 좋아요
- 친구 관련 기능
- 그룹 생성 및 채팅 참여

## 🧑‍💻개발환경
- Streamlit 1.39.0 ver 
- Python 3.12.7 ver
- PyCharm 2024.2.4
- Visual Studio Code 1.95.3

- Python 언어와 Streamlit 웹프레임워크, SQLite DBMS를 활용하였습니다.


## 🪛필수라이브러리 설치
```
pip install streamlit sqlalchemy pandas bcrypt requests python-dotenv
```
## 방법 1.🖥️Streamlit 앱 실행 (로컬서버)
1. 첨부파일의 app (txt)파일, zip.db 파일을 다운로드
2. app.txt 파일 속 코드를 그대로 IDE의 파이썬 언어로 입력 후 저장 (app.py로 저장을 권장합니다)
3. app.py 파일과 zip.db를 같은 디렉토리에 배치 
4. IDE의 터미널에서 streamlit run app.py 명령어 입력 (streamlit run 저장한 파일명.py)

(app.txt 파일 속에 소스코드 전체가 들어가있습니다.)

## 방법 2.🌐서버 접속
[맛zip]
https://y9kxago8mpnyrpltbnrmwn.streamlit.app/
에 접속하면 연결이 되도록 서버와 연동을 시켰습니다.
