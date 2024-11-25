import streamlit as st
import sqlite3
from datetime import datetime
import os
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd






class LocationGet:
   def create_connection(self):
       conn = sqlite3.connect('zip.db')
       conn.row_factory = sqlite3.Row
       return conn
   #locations 테이블에 저장
   def save_location(self, location_name, address_name, latitude, longitude):
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("""
           INSERT INTO locations (location_name, address_name, latitude, longitude)
           VALUES (?, ?, ?, ?)
       """, (location_name, address_name, latitude, longitude))
       conn.commit()
       conn.close()
   #저장 장소들 가져오기
   def get_all_locations(self):
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT * FROM locations")
       locations = cursor.fetchall()
       conn.close()
       return locations


# 위치 검색 및 지도 표시 클래스
class LocationSearch:
   def __init__(self):
       self.db_manager = LocationGet()


   def search_location(self, query):
       url = f"https://dapi.kakao.com/v2/local/search/keyword.json"
       headers = {
           "Authorization": f"KakaoAK 6c1cbbc51f7ba2ed462ab5b62d3a3746"  # API 키를 헤더에 포함
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


           # 선택된 장소의 정보 찾기
           for place in locations:
               if place[0] == selected_place:
                   name, address, latitude, longitude = place


                   # folium 지도 생성
                   m = folium.Map(location=[latitude, longitude], zoom_start=17)
                   folium.Marker([latitude, longitude], tooltip=f"{name}\n{address}",
                                 icon=folium.Icon(color='blue', icon='star', icon_color='white')).add_to(m)


                   st_folium(m, width=800, height=400)  # Streamlit에서 folium 지도 표시
                   col3, col4 = st.columns([4, 1])
                   with col3:
                       st.write(f"장소 이름: {name}")
                       st.write(f"주소: {address}")
                       self.db_manager.save_location(name, address, latitude, longitude)




class PostManager:
   def __init__(self, upload_folder='uploaded_files'):
       self.upload_folder = upload_folder
       if not os.path.exists(upload_folder):
           os.makedirs(upload_folder)
       self.locations_df = None
       self.map=None
       if "posts" not in st.session_state:
           st.session_state.posts = []
           self.fetch_and_store_posts()


   # 디비 연결
   def create_connection(self):
       conn = sqlite3.connect('zip.db')
       conn.row_factory = sqlite3.Row  # Return results as dictionaries
       return conn
   #locations에 저장된 정보를 불러옴
   def fetch_location_data(self):
       conn = sqlite3.connect('zip.db')
       query = """
       SELECT l.location_name, l.address_name, l.latitude, l.longitude
       FROM posting p
       JOIN locations l ON p.p_location = l.location_id
       """
       self.locations_df = pd.read_sql(query, conn)
       conn.close()
   def create_map_with_markers(self):
       if self.locations_df is None:
           st.error("위치가 존재하지 않습니다")


       # 첫 번째 위치의 위도, 경도로 초기 위치 설정
       latitude = self.locations_df.iloc[0]['latitude']
       longitude = self.locations_df.iloc[0]['longitude']


       # Folium 맵 생성
       self.map = folium.Map(location=[latitude, longitude], zoom_start=17)


       # 각 위치에 마커 추가
       for index, row in self.locations_df.iterrows():
           lat = row['latitude']
           lon = row['longitude']
           name = row['location_name']
           address = row['address_name']


           folium.Marker([lat, lon],
                         tooltip=f"{name}\n{address}",
                         icon=folium.Icon(color='blue', icon='star', icon_color='white')).add_to(self.map)
   def display_map(self,key):
       if self.map is None:
           st.warning('위치 등록이 되어있지 않습니다')
       st_folium(self.map, width=800, height=400,key=key)
   # posting에 디비 저장 , 사진 업로드 한 개 밖에 못함
   def add_post(self, title, content, image_file, file_file, category):
       conn = self.create_connection()
       cursor = conn.cursor()


       # Save files if they exist
       image_path = self.save_file(image_file) if image_file else ''
       file_path = self.save_file(file_file) if file_file else ''


       # Insert query (p_location is omitted, it will be auto-incremented)
       query = """
       INSERT INTO posting (p_title, p_content, p_image_path, file_path, p_category, upload_date)
       VALUES (?, ?, ?, ?, ?, ?)
       """
       upload_date = modify_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


       # Execute query without the p_location field
       cursor.execute(query, (title, content, image_path, file_path, category, upload_date))
       conn.commit()
       conn.close()


   # 포스팅 업데이트
   def update_post(self, post_id, title, content, image_file, file_file, category):
       conn = self.create_connection()
       cursor = conn.cursor()


       # 이미지와 파일 저장 (이미지가 있는 경우만)
       image_path = self.save_file(image_file) if image_file else ''
       file_path = self.save_file(file_file) if file_file else ''


       query = """
          UPDATE posting
          SET p_title = ?, p_content = ?, p_image_path = ?, file_path = ?, p_category = ?, modify_date = ?
          WHERE p_id = ?
          """
       modify_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
       cursor.execute(query, (title, content, image_path, file_path, category, modify_date, post_id))
       conn.commit()
       conn.close()


   # Method to delete a post
   def delete_post(self, p_id):
       conn = self.create_connection()
       cursor = conn.cursor()
       query = "DELETE FROM posting WHERE p_id = ?"
       cursor.execute(query, (p_id,))
       conn.commit()
       conn.close()


   # Method to get all posts
   def get_all_posts(self):
       conn = self.create_connection()
       cursor = conn.cursor()
       query = "SELECT * FROM posting"
       cursor.execute(query)
       rows = cursor.fetchall()  # Fetch rows
       columns = [column[0] for column in cursor.description]  # Get column names
       conn.close()


       # Convert rows to dictionaries using column names
       return [dict(zip(columns, row)) for row in rows]


   # Method to save a file to the upload folder
   def save_file(self, file):
       if file:
           file_path = os.path.join(self.upload_folder, file.name)
           with open(file_path, 'wb') as f:
               f.write(file.getbuffer())
           return file_path
       return ''


   def fetch_and_store_posts(self):
       # Fetch all posts from the database and store them in session state
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT p_id, p_title FROM posting")
       posts = cursor.fetchall()
       conn.close()


       # Store the posts in session state
       st.session_state.posts = posts


   def toggle_like(self, post_id):
       conn = self.create_connection()
       cursor = conn.cursor()


       # Check current like status for the post
       cursor.execute("SELECT like_num FROM posting WHERE p_id = ?", (post_id,))
       result = cursor.fetchone()


       if result and result[0] == 1:
           # Unlike the post
           cursor.execute("UPDATE posting SET like_num = like_num - 1 WHERE p_id = ?", (post_id,))
           st.warning("좋아요를 취소했습니다.")


       else:
           # If the post doesn't exist or hasn't been liked yet
           cursor.execute("UPDATE posting SET like_num = 1 WHERE p_id = ?", (post_id,))
           st.success("포스팅을 좋아요 했습니다!")


       conn.commit()
       conn.close()


   def display_like_button(self, post_id):
       # Check if post is already liked
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT like_num FROM posting WHERE p_id = ?", (post_id,))
       result = cursor.fetchone()
       conn.close()


       if result and result[0] == 1:
           btn_label = "좋아요 취소"


       else:
           btn_label = "좋아요"


       if st.button(btn_label, key=post_id,use_container_width=True):
           self.toggle_like(post_id)


   def get_category_options(self):
       conn = self.create_connection()
       cursor = conn.cursor()
       query = "SELECT category_id, category FROM food_categories"
       cursor.execute(query)
       categories = cursor.fetchall()
       conn.close()
       return categories


   def edit_post(self, post_id):
       # 게시물 데이터 가져오기
       conn = self.create_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT * FROM posting WHERE p_id = ?", (post_id,))
       post = cursor.fetchone()
       conn.close()


       if post:
           # 수정할 게시물 정보로 폼을 채운다.
           title = st.text_input("게시물 제목", value=post['p_title'],key=f"post_title_{post['p_id']}")
           content = st.text_area("게시물 내용", value=post['p_content'],key=f"post_content_{post['p_id']}")
           image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'], key=f"image_upload_{post['p_id']}")
           file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'], key=f"file_upload_{post['p_id']}")


           selected_category_name=st.selectbox(
               "카테고리",
               self.get_category_names(),
               key=f"category_selectbox_{post['p_id']}"  # 고유한 key 추가
           )
           categories = self.get_category_options()
           category_dict = {category[1]: category[0] for category in categories}
           selected_category_id = category_dict[selected_category_name]
           if st.button("게시물 수정",key=f"button_{post['p_id']}",use_container_width=True):
               # 게시물 수정 메서드 호출
               self.update_post(post_id, title, content, image_file, file_file, selected_category_id)
               st.success("게시물이 수정되었습니다.")
       else:
           st.error("해당 게시물이 존재하지 않습니다.")


   def get_category_names(self):
       categories = self.get_category_options()
       return [category[1] for category in categories]  # 카테고리 이름만 리스트로 반환


   def display_posts(self):
       posts = self.get_all_posts()
       for post in posts:
           # 게시물 정보 출력
           st.write(f"Post ID: {post['p_id']}, Title: {post['p_title']}")
           st.write(f"Content: {post['p_content']}")


           # 좋아요 버튼
           self.display_like_button(post['p_id'])


           # 게시물 삭제 버튼
           if st.button(f"삭제", key=f"delete_{post['p_id']}",use_container_width=True):
               # 삭제 버튼 클릭 시
               self.delete_post(post['p_id'])
               st.success(f"게시물 '{post['p_title']}'가 삭제되었습니다.")
               # 삭제 후에는 목록을 갱신해서 다시 표시
               return self.display_posts()  # 재귀적으로 호출하여 목록을 갱신




           # 게시물 수정 버튼
           with st.expander("수정"):
               # 수정 버튼 클릭 시
               self.edit_post(post['p_id'])


           # 데이터 불러오기 (위치 정보)
           self.fetch_location_data()


           # 위치 데이터가 존재할 때만 지도 생성
           if self.locations_df is not None and not self.locations_df.empty:
               self.create_map_with_markers()
               st.title("Location Map")
               self.display_map(key=f"map_{post['p_id']}")


           # 게시물 추가 정보
           st.write(f"**등록 날짜**: {post['upload_date']}, **수정 날짜**: {post['modify_date']}")
           st.write("---")




# Streamlit page setup
st.title("게시물 관리 시스템")


# Initialize PostManager
post_manager = PostManager()


# Sidebar navigation
page = st.sidebar.selectbox("페이지 선택", ["게시물 등록", "게시물 열람"])




# 게시물 등록 페이지
if page == "게시물 등록":
   st.header("게시물 등록")


   title = st.text_input("게시물 제목")
   content = st.text_area("게시물 내용")
   image_file = st.file_uploader("이미지 파일", type=['jpg', 'png', 'jpeg'])
   file_file = st.file_uploader("일반 파일", type=['pdf', 'docx', 'txt', 'png', 'jpg'])


   # 카테고리 선택을 위한 Selectbox
   post_manager = PostManager('zip.db')  # DB 경로 설정
   category_names = post_manager.get_category_names()  # 카테고리 이름만 가져옴


   # Selectbox에서 카테고리 선택
   selected_category_name = st.selectbox("카테고리", category_names)


   # 선택한 카테고리 이름에 해당하는 category_id 구하기
   categories = post_manager.get_category_options()
   category_dict = {category[1]: category[0] for category in categories}
   selected_category_id = category_dict[selected_category_name]


   location_search = LocationSearch()
   location_search.display_location_on_map()


   if st.button("게시물 등록"):
       if title and content:
           post_manager.add_post(title, content, image_file, file_file,selected_category_id)
           st.success("게시물이 등록되었습니다.")
       else:
           st.error("제목과 내용을 입력해 주세요.")










# 게시물 열람 페이지
elif page == "게시물 열람":
   st.header("게시물 목록")
   post_manager.display_posts()





