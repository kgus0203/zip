import streamlit as st
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, func, CheckConstraint, Date,
    Time,
)
from sqlalchemy.orm import sessionmaker, relationship
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
from datetime import timedelta

# SQLAlchemy Base 선언
Base = declarative_base()

# 데이터베이스 URL 설정
DATABASE_URL = "sqlite:///zip.db"

# 데이터베이스 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Localization:
    def __init__(self, lang='ko'):

        self.lang = lang
        self.translations = self.load_translations()

    def load_translations(self):

        return {
            "ko": {
                "check":"확인",
                "id_pw_change_title": "ID/PW 변경",
                "no_user_info_error": "사용자 정보가 없습니다. 다시 로그인해주세요.",
                "select_change_action": "변경할 항목을 선택하세요",
                "change_id": "ID 변경",
                "change_pw": "비밀번호 변경",
                "next_button": "다음",
                "enter_new_value": "새로 사용할 {action}를 입력하세요",
                "save_button": "저장",
                "id_change_success": "ID가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.",
                "pw_change_success": "비밀번호가 성공적으로 변경되었습니다. 로그아웃 후 첫 페이지로 이동합니다.",
                "login_page_title": "로그인 페이지",
                "user_id_input": "아이디",
                "password_input": "비밀번호",
                "login_button": "로그인",
                "login_error_empty": "아이디와 비밀번호를 입력해 주세요.",
                "login_error_failed": "로그인에 실패했습니다. 아이디 또는 비밀번호를 확인해 주세요.",
                "user_info_load_error": "사용자 정보를 불러오는데 실패했습니다.",
                "back_button": "뒤로가기 ↩️",
                "signup_page_title": "회원가입 페이지",
                "email_input": "이메일",
                "signup_button": "회원가입",
                "signup_error_empty": "모든 필드를 입력해 주세요.",
                "signup_success": "회원가입이 완료되었습니다!",
                "signup_error_failed": "회원가입에 실패하였습니다.",
                "home_title": "맛ZIP",
                "logout_button": "로그아웃",
                "logout_success": "로그아웃 성공",
                "profile_button": "프로필",
                "view_post_button": "게시물 보기",
                "group_button": "그룹 페이지",
                "recommended_posts": "추천 맛집 게시물",
                "find_id_pw_button": "ID/PW 찾기",
                "page_not_found": "페이지 '{page}'을 찾을 수 없습니다.",
                "no_previous_page": "이전 페이지가 없습니다.",
                "upload_post_header": "게시물 등록",
                "post_title_input": "게시물 제목",
                "post_content_input": "게시물 내용",
                "image_file_upload": "이미지 파일",
                "general_file_upload": "일반 파일",
                "category_select": "카테고리",
                "post_register_button": "게시물 등록",
                "post_register_success": "게시물이 등록되었습니다.",
                "user_info_not_found": "사용자 정보를 찾을 수 없습니다.",
                "my_page_header": "내 페이지",
                "friend_management": "친구 관리",
                "my_friend_list_button": "내 친구 리스트",
                "friend_requests_button": "친구 대기",
                "user_manager_page_title": "사용자 관리 페이지",
                "email_input_prompt": "이메일을 입력하세요: ",
                "confirm_button": "확인",
                "password_recovery_email_sent": "비밀번호 복구 메일을 전송했습니다",
                "email_not_registered_warning": "등록되지 않은 이메일입니다.",
                "view_post_header": "게시물 목록",
                "upload_post_button": "글 작성",
                "my_made_groups_expander": "내가 만든 그룹 목록",
                "no_joined_groups": "생성한 그룹이 없습니다.",
                "group_name": "그룹 이름",
                "category": "카테고리",
                "status": "상태",
                "meeting_date": "약속 날짜",
                "meeting_time": "약속 시간",
                "edit_button": "수정",
                "delete_button": "삭제",
                "group_deleted_success": "그룹이 삭제되었습니다.",
                "friend_requests_management": "친구 요청 관리",
                "sent_friend_requests": "내가 보낸 친구 요청",
                "no_sent_requests": "보낸 친구 요청이 없습니다.",
                "received_friend_requests": "다른 사람이 보낸 친구 요청",
                "accept": "수락",
                "reject": "거절",
                "no_received_requests": "받은 친구 요청이 없습니다.",
                "group_page_title": "그룹페이지",
                "create_group_button": "그룹 생성",
                "blocked_list_button": "차단 목록",
                "search_group_button": "그룹 검색",
                "category": "카테고리",
                "status": "상태",
                "meeting_date": "약속 날짜",
                "meeting_time": "약속 시간",
                "members_count": "인원수",
                "not_set": "설정되지 않음",
                "detail_button": "세부 정보",
                "detail_group_page": "그룹 세부 정보",
                "group_block_list_title": "그룹 차단 목록",
                "login_required_error": "로그인이 필요합니다.",
                "no_blocked_groups": "차단된 그룹이 없습니다.",
                "blocked_group_id": "차단된 그룹 ID",
                "unblock_button": "차단 해제",
                "unblock_success": "차단 해제 완료:",
                "unblock_error": "차단 해제 중 오류 발생",
                "group_request_list_title": "그룹 대기 목록",
                "no_requests": "대기 중인 요청이 없습니다.",
                "requester_id": "요청자 ID",
                "approve_request": "승인",
                "request_approved": "요청이 승인되었습니다.",
                "reject_request": "거절",
                "request_rejected": "요청이 거절되었습니다.",
                "group_detail_title": "그룹 세부 정보",
                "no_group_error": "그룹 정보가 없습니다.",
                "group_info_not_found": "그룹 정보를 찾을 수 없습니다.",
                "current_members": "현재 인원수",
                "last_modified": "마지막 수정일",
                "meeting_date": "약속 날짜",
                "meeting_time": "약속 시간",
                "not_set": "설정되지 않음",
                "group_members": "그룹원",
                "no_members_in_group": "이 그룹에 소속된 멤버가 없습니다.",
                "block_group": "그룹 차단",
                "unblock_group": "차단 해제",
                "group_blocked_success": "그룹이 차단되었습니다.",
                "group_blocked_error": "차단 중 오류가 발생했습니다.",
                "group_unblocked_success": "차단이 해제되었습니다.",
                "group_unblocked_error": "해제 중 오류가 발생했습니다.",
                "invite_to_group": "그룹 초대",
                "enter_invitee_id": "초대할 사용자 ID를 입력하세요",
                "group_id_not_found_error":"그룹 ID를 찾을 수 없습니다.",
                "send_invite": "초대 요청 보내기",
                "invite_sent_success": "님에게 초대 요청을 보냈습니다.",
                "group_invite_confirmed": "그룹 초대가 되었습니다.",
                "invite_failed": "초대 요청을 보내는 데 실패했습니다.",
                "enter_valid_invitee_id": "초대할 사용자 ID를 입력하세요.",
                "group_block_list_title": "그룹 차단 목록",
                "login_required": "로그인이 필요합니다.",
                "no_blocked_groups": "차단된 그룹이 없습니다.",
                "blocked_group_id": "차단된 그룹 ID",
                "unblock": "차단 해제",
                "group_unblocked_success": "차단 해제 성공",
                "group_unblock_error": "차단 해제 실패",
                "create_group_dialog_title": "그룹 생성",
                "create_group_header": "그룹 생성",
                "group_name_label": "그룹 이름",
                "group_name_placeholder": "그룹 이름을 입력하세요",
                "max_members_label": "최대 인원 수",
                "select_meeting_date_label": "약속 날짜 선택",
                "select_meeting_time_label": "약속 시간 선택",
                "create_group_button": "그룹 생성",
                "update_group_dialog_title": "그룹 수정",
                "update_group_header": "그룹을 수정합니다.",
                "meeting_date_label": "약속 날짜",
                "meeting_time_label": "약속 시간",
                "group_status_label": "그룹 상태",
                "status_in_progress": "진행 중",
                "status_completed": "완료",
                "status_canceled": "취소",
                "update_group_button": "그룹 수정",
                "search_group_dialog_title": "그룹 검색",
                "search_group_header": "그룹 검색 및 참여",
                "search_criteria_label": "검색 기준을 선택하세요",
                "search_by_name": "이름",
                "search_by_date": "날짜",
                "search_by_category": "카테고리",
                "group_name_prompt": "그룹 이름을 입력하세요",
                "meeting_date_prompt": "약속 날짜를 선택하세요",
                "search_button_label": "검색",
                "no_search_results": "검색 결과가 없습니다.",
                "group_name": "그룹 이름",
                "group_leader": "그룹장",
                "current_members": "현재 인원수",
                "meeting_date": "약속 날짜",
                "meeting_time": "약속 시간",
                "category": "카테고리",
                "location": "장소",
                "join_group": "그룹 참여",
                "friend_request_input_label": "친구 요청을 보낼 ID를 입력하세요:",
                "friend_request_button": "친구 요청",
                "friend_request_warning": "친구 요청할 ID를 입력해주세요.",
                "unblock_friend_dialog_title": "친구 차단 해제 창",
                "unblock_friend_input_label": "차단 해제할 친구의 ID를 입력하세요:",
                "unblock_friend_button": "차단 해제",
                "unblock_friend_warning": "친구 차단 해제할 ID를 입력해주세요.",
                "blocked_list_title": "차단된 친구 목록",
                "blocked_users_subheader": "현재 차단된 사용자:",
                "no_blocked_users": "차단된 사용자가 없습니다.",
                "no_friend_id_error": "친구 ID가 없습니다.",
                "friend_posts_title": "{friend_id}님의 포스팅",
                "no_image_message": "이미지가 없습니다.",
                "no_posts_warning": "작성한 포스팅이 없습니다.",
                "db_error": "데이터베이스 오류: {error}",
                "delete_friend_dialog_title": "친구 삭제 창",
                "delete_friend_input_label": "삭제할 친구의 ID를 입력하세요:",
                "delete_friend_button": "친구 삭제",
                "delete_friend_warning": "삭제할 친구의 ID를 입력해주세요.",
                "block_friend_dialog_title": "친구 차단 창",
                "block_friend_input_label": "차단할 친구의 ID를 입력하세요:",
                "block_friend_button": "친구 차단",
                "block_friend_warning": "친구 차단할 ID를 입력해주세요.",
                "friend_requests_dialog_title": "친구 대기 창",
                "friend_list_title": "내 친구 리스트",
                "send_friend_request_button": "친구 요청",
                "password_length_error": "비밀번호는 최소 8자 이상이어야 합니다.",
                "password_change_success": "비밀번호가 변경되었습니다.",
                "password_minimum_length": "비밀번호는 8자리 이상이어야 합니다.",
                "user_id_exists_error": "이미 사용 중인 아이디입니다.",
                "login_success": "{user_id}님, 로그인 성공!",
                "password_incorrect_error": "비밀번호가 틀렸습니다.",
                "user_id_not_found_error": "아이디가 존재하지 않습니다.",
                "no_search_results": "검색 결과가 없습니다.",
                "api_request_error": "API 요청 오류: {status_code}",
                "search_location_input": "검색할 장소를 입력하세요:",
                "search_button": "검색",
                "select_search_result": "검색 결과를 선택하세요:",
                "place_name": "장소 이름",
                "address": "주소",
                "password_recovery_subject": "비밀번호 복구 토큰",
                "password_recovery_body": "안녕하세요,\n\n비밀번호 복구 요청이 접수되었습니다. 아래의 복구 토큰을 사용하세요:\n\n{token}\n\n이 요청을 본인이 하지 않은 경우, 이 이메일을 무시해 주세요.",
                "email_sent_success": "복구 이메일이 {email}으로 성공적으로 전송되었습니다.",
                "email_failed_smtp": "SMTP 오류로 인해 이메일 전송 실패: {error}",
                "email_failed_generic": "예기치 않은 오류로 인해 이메일 전송 실패: {error}",
                "invalid_token": "유효하지 않은 토큰입니다.",
                "password_reset_success": "비밀번호가 성공적으로 복구되었습니다.",
                "user_not_found": "사용자 ID '{user_id}'를 찾을 수 없습니다.",
                "missing_required_fields": "모든 필수 입력 항목을 입력해주세요.",
                "status_in_progress": "진행 중",
                "group_creation_success": "'{group_name}' 그룹이 성공적으로 생성되었습니다!",
                "no_posts_found": "사용자 ID '{user_id}'로 작성된 게시물이 없습니다.",
                "post_retrieval_error": "게시물 조회 중 오류가 발생했습니다: {error}",
                "like_removed": "좋아요를 취소했습니다.",
                "like_added": "좋아요를 추가했습니다!",
                "total_likes": "총 좋아요 수: {total_likes}",
                "unlike_button": "좋아요 취소",
                "like_button": "좋아요",
                "no_locations_found": "위치가 존재하지 않습니다",
                "location_name": "장소 이름: {name}",
                "location_address": "주소: {address}",
                "no_location_data": "위치 데이터가 없습니다.",
                "edit_post_title_label": "게시물 제목",
                "edit_post_content_label": "게시물 내용",
                "edit_post_image_upload": "이미지 파일",
                "edit_post_file_upload": "일반 파일",
                "edit_post_category_label": "카테고리",
                "edit_post_submit_button": "게시물 수정",
                "edit_post_success_message": "게시물이 수정되었습니다.",
                "edit_post_not_found_error": "해당 게시물이 존재하지 않습니다.",
                "post_id_and_title": "게시물 ID: {post_id}, 제목: {title}",
                "post_content": "내용: {content}",
                "delete_post_button": "삭제",
                "delete_post_success_message": "게시물 '{title}'가 삭제되었습니다.",
                "edit_post_expander": "수정",
                "location_map_title": "위치 지도",
                "post_dates": "**등록 날짜**: {upload_date}, **수정 날짜**: {modify_date}",
                "sort_posts_label": "정렬 방식",
                "sort_by_latest": "최신순",
                "sort_by_popularity": "인기순",
                "no_recommended_posts_message": "현재 추천 포스팅이 없습니다.",
                "view_more_expander": "더보기",
                "select_category_label": "카테고리 선택",
                "no_registered_categories_error": "등록된 카테고리가 없습니다. 관리자에게 문의하세요.",
                "dark_mode_button_label": "어두운 모드 🌜",
                "light_mode_button_label": "밝은 모드 🌞",
                "user_email": "사용자 이메일: {email}",
                "user_info_not_found": "사용자 정보를 찾을 수 없습니다.",
                "change_profile_picture": "프로필 사진 변경",
                "upload_new_profile_picture": "새 프로필 사진 업로드",
                "upload_button": "업로드",
                "profile_picture_updated": "프로필 사진이 성공적으로 업데이트되었습니다.",
                "file_save_failed": "파일 저장에 실패했습니다.",
                "field_updated": "{field}이(가) 성공적으로 업데이트되었습니다.",
                "user_info_fetch_failed": "업데이트 후 사용자 정보를 가져오는 데 실패했습니다.",
                "field_update_failed": "사용자 정보를 업데이트하는 데 실패했습니다.",
                "alarm_settings": "알람 설정",
                "alarm_enabled": "알람이 설정되었습니다.",
                "alarm_disabled": "알람이 해제되었습니다.",
                "edit_my_info": "내 정보 수정하기",
                "new_email": "새 이메일 주소",
                "change_email_button": "이메일 변경",
                "new_password": "새 비밀번호",
                "change_password_button": "비밀번호 변경",
                "profile_picture_changed": "프로필 사진이 변경되었습니다.",
                "favorites": "관심목록",
                "friend_requests_title": "친구 대기 창",
                "message_saved": "{sender}님의 메세지가 저장되었습니다.",
                "group_not_found": "그룹이 존재하지 않습니다.",
                "chat_title": "채팅: {group}",
                "login_required": "로그인이 필요합니다.",
                "chat_history": "### 채팅 기록",
                "message_input": "메시지 입력",
                "send_button": "보내기",
                "message_required": "메시지를 입력해주세요.",
                "group_member_added_success": "그룹 멤버가 성공적으로 추가되었습니다!",
                "group_member_add_error": "멤버 추가 중 오류 발생: {error}",
                "group_details": "그룹: {group_name}",
                "group_not_found": "그룹을 찾을 수 없습니다.",
                "group_deleted_success": "그룹이 성공적으로 삭제되었습니다!",
                "group_delete_error": "그룹 삭제 중 오류 발생: {error}",
                "group_updated_success": "'{group_name}' 그룹이 성공적으로 수정되었습니다!",
                "db_error": "DB 오류: {error}",
                "already_member": "이미 해당 그룹의 멤버입니다.",
                "group_joined_success": "'{group_name}' 그룹에 성공적으로 참여하였습니다.",
                "group_blocked_success": "그룹이 성공적으로 차단되었습니다!",
                "group_block_error": "그룹 차단 중 오류 발생: {error}",
                "group_unblocked_success": "그룹 차단이 성공적으로 해제되었습니다!",
                "group_not_blocked": "차단된 그룹이 존재하지 않습니다.",
                "group_unblock_error": "그룹 차단 해제 중 오류 발생: {error}",
                "blocked_groups_error": "차단된 그룹 조회 중 오류 발생: {error}",
                "is_group_blocked_error": "그룹 차단 여부 확인 중 오류 발생: {error}",
                "search_by_name": "이름으로 검색",
                "search_by_date": "날짜로 검색",
                "search_by_category": "카테고리로 검색",
                "friend_list_title": "내 친구 리스트",
                "no_friends": "친구가 없습니다.",
                "blocked_list_title": "차단 목록",
                "no_blocked_users": "차단된 사용자가 없습니다.",
                "block_self_error": "자신을 차단할 수 없습니다.",
                "user_not_found": "없는 ID입니다.",
                "already_blocked": "이미 차단된 사용자입니다.",
                "block_success": "{friend_id}님을 차단하였습니다.",
                "not_blocked_user": "차단된 사용자가 아닙니다.",
                "unblock_success": "{friend_id}님을 차단 해제하였습니다.",
                "delete_self_error": "자신을 삭제할 수 없습니다.",
                "not_in_friend_list": "해당 유저는 내 친구 리스트에 없는 유저입니다.",
                "delete_friend_success": "{friend_id}님을 친구 목록에서 삭제하였습니다.",
                "add_self_as_friend_error": "자신을 친구로 추가할 수 없습니다.",
                "unblock_before_request_error": "먼저 차단을 해제해주세요.",
                "user_id_not_found_error": "없는 ID입니다.",
                "already_friends_error": "이미 친구입니다.",
                "already_requested_error": "이미 친구 요청을 보냈습니다.",
                "debug_my_friend_requests": "내가 보낸 친구 요청:",
                "friend_request_sent_success": "{friend_id}님에게 친구 요청을 보냈습니다. 상대방이 수락할 때까지 기다려주세요.",
                "friend_request_accepted_success": "{requester_id}님과 친구가 되었습니다.",
                "friend_request_rejected_success": "{requester_id}님의 친구 요청을 거절했습니다.",
                "not_in_group": "이 그룹에 소속되어 있지 않습니다.",
                "leave_group_success": "'{group_id}' 그룹에서 성공적으로 탈퇴했습니다.",
                "leave_group_error": "그룹 탈퇴 중 오류 발생: {error}",
                "enter_recovery_token": "복구 토큰",
                "token_placeholder": "이메일로 받은 토큰을 입력하세요",
                "new_password_label": "새 비밀번호",
                "new_password_placeholder": "새 비밀번호를 입력하세요",
                "recover_password_button": "비밀번호 복구",
                "all_fields_required": "모든 필드를 입력하세요.",
                "password_reset_success": "비밀번호가 성공적으로 변경되었습니다!",
                "invalid_or_expired_token": "유효하지 않은 토큰이거나 토큰이 만료되었습니다.",
                "my_groups_expander": "내가 속한 그룹 목록",
                "no_joined_groups": "가입한 그룹이 없습니다.",
                "group_name": "그룹 이름",
                "category": "카테고리",
                "status": "상태",
                "meeting_date": "약속 날짜",
                "meeting_time": "약속 시간",
                "edit_button": "수정",
                "delete_button": "삭제",
                "kick_member_button": "그룹원 내쫓기",
                "kick_member_dialog": "그룹원 내쫓기",
                "group_members_in": "그룹 멤버",
                "no_members": "이 그룹에 멤버가 없습니다.",
                "admin_role": "관리자",
                "member_role": "멤버",
                "kick_button": "내쫓기",
                "kick_success": "{member_id}님을 그룹에서 내쫓았습니다.",
                "kick_error": "{member_id}님을 내쫓는 중 오류가 발생했습니다.",
                "exit_group_dialog": "그룹 나가기",
                "exit_group_confirmation": "정말로 '{group_name}' 그룹을 나가시겠습니까?",
                "yes_button": "예",
                "no_button": "아니요",
                "exit_group_success": "그룹 '{group_name}'을 성공적으로 나갔습니다.",
                "exit_group_cancelled": "그룹 나가기가 취소되었습니다.",
                "delete_group_dialog": "그룹 삭제",
                "delete_group_confirmation": "정말로 '{group_name}' 그룹을 삭제하시겠습니까?",
                "group_deleted": "'{group_name}' 그룹이 삭제되었습니다.",
                "not_group_creator": "그룹 생성자만 삭제할 수 있습니다.",
                "delete_group_cancelled": "그룹 삭제가 취소되었습니다.",
                "my_groups_expander": "내가 속한 그룹 목록",
                "no_joined_groups": "가입한 그룹이 없습니다.",
                "no_maded_groups": "생성된 그룹이 없습니다.",
                "group_name": "그룹 이름",
                "category": "카테고리",
                "status": "상태",
                "meeting_date": "약속 날짜",
                "meeting_time": "약속 시간",
                "chat": "그룹 채팅",
                "enter_chat_button": "채팅 입장하기",
                "leave_group_button": "그룹 탈퇴",
                "choose_language": "언어를 선택해주세요",
                "select_language": "언어 선택"

            },
            "en": {
                "check":"check",
                "id_pw_change_title": "ID/PW Change",
                "no_user_info_error": "User information not found. Please log in again.",
                "select_change_action": "Select an item to change",
                "change_id": "Change ID",
                "change_pw": "Change Password",
                "next_button": "Next",
                "enter_new_value": "Enter a new {action}",
                "save_button": "Save",
                "id_change_success": "ID has been successfully changed. Logging out and returning to the home page.",
                "pw_change_success": "Password has been successfully changed. Logging out and returning to the home page.",
                "login_page_title": "Login Page",
                "user_id_input": "User ID",
                "password_input": "Password",
                "login_error_empty": "Please enter your user ID and password.",
                "login_error_failed": "Login failed. Please check your user ID and password.",
                "user_info_load_error": "Failed to load user information.",
                "signup_page_title": "Signup Page",
                "email_input": "Email Address",
                "signup_button": "Sign Up",
                "signup_error_empty": "Please fill in all fields.",
                "signup_success": "Sign up completed successfully!",
                "signup_error_failed": "Sign up failed.",
                "logout_button": "Logout",
                "group_id_not_found_error": "Group ID not found.",
                "logout_success": "Logout successful.",
                "profile_button": "Profile",
                "view_post_button": "View Posts",
                "group_button": "Group Page",
                "recommended_posts": "Recommended Posts",
                "home_title": "MatZIP",
                "login_button": "Login",
                "find_id_pw_button": "Find ID/PW",
                "page_not_found": "Page '{page}' not found.",
                "no_previous_page": "No previous page available.",
                "upload_post_header": "Upload Post",
                "post_title_input": "Post Title",
                "post_content_input": "Post Content",
                "image_file_upload": "Image File",
                "general_file_upload": "General File",
                "category_select": "Category",
                "post_register_button": "Register Post",
                "post_register_success": "Post has been registered.",
                "back_button": "Back ↩️",
                "user_info_not_found": "User information could not be found.",
                "my_page_header": "My Page",
                "friend_management": "Friend Management",
                "my_friend_list_button": "My Friend List",
                "friend_requests_button": "Friend Requests",
                "user_manager_page_title": "User Management Page",
                "email_input_prompt": "Enter your email: ",
                "confirm_button": "Confirm",
                "password_recovery_email_sent": "Password recovery email has been sent.",
                "email_not_registered_warning": "The email is not registered.",
                "friend_management": "Friend Management",
                "my_friend_list_button": "My Friend List",
                "friend_requests_button": "Friend Requests",
                "friend_requests_title": "Friend Request Management",
                "user_manager_page_title": "User Management Page",
                "email_input_prompt": "Enter your email",
                "confirm_button": "Confirm",
                "password_recovery_email_sent": "Password recovery email has been sent.",
                "email_not_registered_warning": "The email is not registered.",
                "view_post_header": "Post List",
                "upload_post_button": "Create Post",
                "my_made_groups_expander": "Groups I Created",
                "no_maded_groups": "No groups created",
                "group_name": "Group Name",
                "category": "Category",
                "status": "Status",
                "meeting_date": "Meeting Date",
                "meeting_time": "Meeting Time",
                "edit_button": "Edit",
                "delete_button": "Delete",
                "group_deleted_success": "Group has been deleted.",
                "friend_requests_management": "Friend Request Management",
                "sent_friend_requests": "Friend Requests Sent",
                "no_sent_requests": "No sent friend requests.",
                "received_friend_requests": "Friend Requests Received",
                "accept": "Accept",
                "reject": "Reject",
                "no_received_requests": "No received friend requests.",
                "group_page_title": "Group Page",
                "create_group_button": "Create Group",
                "blocked_list_button": "Blocked List",
                "search_group_button": "Search Groups",
                "friend_requests_title": "Friend Pending Requests",
                "category": "Category",
                "status": "Status",
                "meeting_date": "Meeting Date",
                "meeting_time": "Meeting Time",
                "members_count": "Members Count",
                "not_set": "Not set",
                "detail_button": "Details",
                "detail_group_page": "Group Details",
                "group_block_list_title": "Blocked Groups List",
                "login_required_error": "Login is required.",
                "no_blocked_groups": "No blocked groups found.",
                "blocked_group_id": "Blocked Group ID",
                "unblock_button": "Unblock",
                "unblock_success": "Unblock successful:",
                "unblock_error": "Error occurred while unblocking.",
                "group_request_list_title": "Group Requests",
                "no_requests": "No pending requests.",
                "requester_id": "Requester ID",
                "approve_request": "Approve",
                "request_approved": "Request approved.",
                "reject_request": "Reject",
                "request_rejected": "Request rejected.",
                "group_detail_title": "Group Details",
                "no_group_error": "Group information is not available.",
                "group_info_not_found": "Group information could not be found.",
                "current_members": "Current Members",
                "last_modified": "Last Modified",
                "meeting_date": "Meeting Date",
                "meeting_time": "Meeting Time",
                "not_set": "Not set",
                "group_members": "Group Members",
                "no_members_in_group": "No members in this group.",
                "block_group": "Block Group",
                "unblock_group": "Unblock Group",
                "group_blocked_success": "Group has been blocked.",
                "group_blocked_error": "Error occurred while blocking the group.",
                "group_unblocked_success": "Group has been unblocked.",
                "group_unblocked_error": "Error occurred while unblocking the group.",
                "invite_to_group": "Invite to Group",
                "enter_invitee_id": "Enter the ID of the user to invite",
                "send_invite": "Send Invite Request",
                "invite_sent_success": "has been invited.",
                "group_invite_confirmed": "Group invitation confirmed.",
                "invite_failed": "Failed to send invitation request.",
                "enter_valid_invitee_id": "Please enter a valid ID to invite.",
                "group_block_list_title": "Blocked Groups List",
                "login_required": "Login is required.",
                "no_blocked_groups": "No blocked groups.",
                "blocked_group_id": "Blocked Group ID",
                "unblock": "Unblock",
                "group_unblocked_success": "Unblock successful",
                "group_unblock_error": "Unblock failed",
                "create_group_dialog_title": "Create Group",
                "create_group_header": "Create Group",
                "group_name_label": "Group Name",
                "group_name_placeholder": "Enter group name",
                "max_members_label": "Maximum Members",
                "select_meeting_date_label": "Select Meeting Date",
                "select_meeting_time_label": "Select Meeting Time",
                "create_group_button": "Create Group",
                "update_group_dialog_title": "Update Group",
                "update_group_header": "Update Group",
                "meeting_date_label": "Meeting Date",
                "meeting_time_label": "Meeting Time",
                "group_status_label": "Group Status",
                "status_in_progress": "In Progress",
                "status_completed": "Completed",
                "status_canceled": "Canceled",
                "update_group_button": "Update Group",
                "search_group_dialog_title": "Search Groups",
                "search_group_header": "Search and Join Groups",
                "search_criteria_label": "Select Search Criteria",
                "search_by_name": "Name",
                "search_by_date": "Date",
                "search_by_category": "Category",
                "group_name_prompt": "Enter group name",
                "meeting_date_prompt": "Select meeting date",
                "search_button_label": "Search",
                "no_search_results": "No search results found.",
                "group_name": "Group Name",
                "select_category_label": "Select Category",
                "no_registered_categories_error": "No registered categories found. Please contact the administrator.",
                "group_leader": "Group Leader",
                "current_members": "Current Members",
                "meeting_date": "Meeting Date",
                "meeting_time": "Meeting Time",
                "category": "Category",
                "location": "Location",
                "join_group": "Join Group",
                "friend_request_input_label": "Enter the ID to send a friend request:",
                "friend_request_button": "Send Friend Request",
                "friend_request_warning": "Please enter the ID to send a friend request.",
                "unblock_friend_dialog_title": "Unblock Friend Dialog",
                "unblock_friend_input_label": "Enter the ID to unblock a friend:",
                "unblock_friend_button": "Unblock Friend",
                "unblock_friend_warning": "Please enter the ID to unblock a friend.",
                "blocked_list_title": "Blocked Friends List",
                "blocked_users_subheader": "Currently Blocked Users:",
                "no_blocked_users": "No blocked users found.",
                "no_friend_id_error": "No friend ID found.",
                "friend_posts_title": "{friend_id}'s Posts",
                "no_image_message": "No image available.",
                "no_posts_warning": "No posts available.",
                "db_error": "Database error: {error}",
                "delete_friend_dialog_title": "Delete Friend Dialog",
                "delete_friend_input_label": "Enter the ID to delete a friend:",
                "delete_friend_button": "Delete Friend",
                "delete_friend_warning": "Please enter the ID to delete a friend.",
                "block_friend_dialog_title": "Block Friend Dialog",
                "block_friend_input_label": "Enter the ID to block a friend:",
                "block_friend_button": "Block Friend",
                "block_friend_warning": "Please enter the ID to block a friend.",
                "friend_requests_dialog_title": "Friend Requests Dialog",
                "friend_list_title": "My Friend List",
                "send_friend_request_button": "Send Friend Request",
                "password_length_error": "Password must be at least 8 characters.",
                "user_id_exists_error": "The user ID is already in use.",
                "login_success": "Login successful, welcome {user_id}!",
                "password_incorrect_error": "The password is incorrect.",
                "user_id_not_found_error": "The user ID does not exist.",
                "no_search_results": "No search results found.",
                "api_request_error": "API request error: {status_code}",
                "search_location_input": "Enter a location to search:",
                "search_button": "Search",
                "select_search_result": "Select a search result:",
                "place_name": "Place Name",
                "address": "Address",
                "password_recovery_subject": "Password Recovery Token",
                "password_recovery_body": "Hello,\n\nA password recovery request has been received. Please use the recovery token below:\n\n{token}\n\nIf you did not request this, please ignore this email.",
                "email_sent_success": "Recovery email successfully sent to {email}.",
                "email_failed_smtp": "Failed to send email due to SMTP error: {error}",
                "email_failed_generic": "Failed to send email due to unexpected error: {error}",
                "invalid_token": "Invalid token.",
                "password_reset_success": "Password has been successfully reset.",
                "user_not_found": "User ID '{user_id}' not found.",
                "missing_required_fields": "Please fill in all required fields.",
                "status_in_progress": "In progress",
                "group_creation_success": "Group '{group_name}' has been successfully created!",
                "no_posts_found": "No posts found for user ID '{user_id}'.",
                "post_retrieval_error": "Error occurred while retrieving posts: {error}",
                "like_removed": "Like has been removed.",
                "like_added": "Like has been added!",
                "total_likes": "Total likes: {total_likes}",
                "unlike_button": "Unlike",
                "like_button": "Like",
                "no_locations_found": "No locations found.",
                "location_name": "Location Name: {name}",
                "location_address": "Address: {address}",
                "no_location_data": "No location data available.",
                "edit_post_title_label": "Post Title",
                "edit_post_content_label": "Post Content",
                "edit_post_image_upload": "Image File",
                "edit_post_file_upload": "General File",
                "edit_post_category_label": "Category",
                "edit_post_submit_button": "Edit Post",
                "edit_post_success_message": "Post has been updated.",
                "edit_post_not_found_error": "The post does not exist.",
                "post_id_and_title": "Post ID: {post_id}, Title: {title}",
                "post_content": "Content: {content}",
                "delete_post_button": "Delete",
                "delete_post_success_message": "The post '{title}' has been deleted.",
                "edit_post_expander": "Edit",
                "location_map_title": "Location Map",
                "post_dates": "**Upload Date**: {upload_date}, **Modify Date**: {modify_date}",
                "sort_posts_label": "Sort By",
                "sort_by_latest": "Latest",
                "sort_by_popularity": "Most Popular",
                "no_recommended_posts_message": "There are no recommended posts currently.",
                "view_more_expander": "View More",
                "dark_mode_button_label": "Dark Mode 🌜",
                "light_mode_button_label": "Light Mode 🌞",
                "user_email": "User Email: {email}",
                "user_info_not_found": "User information not found.",
                "change_profile_picture": "Change Profile Picture",
                "upload_new_profile_picture": "Upload New Profile Picture",
                "upload_button": "Upload",
                "profile_picture_updated": "Profile picture successfully updated.",
                "file_save_failed": "Failed to save file.",
                "field_updated": "{field} successfully updated.",
                "user_info_fetch_failed": "Failed to fetch user information after update.",
                "field_update_failed": "Failed to update user information.",
                "alarm_settings": "Alarm Settings",
                "alarm_enabled": "Alarm has been enabled.",
                "alarm_disabled": "Alarm has been disabled.",
                "edit_my_info": "Edit My Info",
                "new_email": "New Email Address",
                "change_email_button": "Change Email",
                "new_password": "New Password",
                "change_password_button": "Change Password",
                "profile_picture_changed": "Profile picture has been changed.",
                "favorites": "Favorites",
                "message_saved": "Message from {sender} has been saved.",
                "password_change_success": "Password has been successfully changed.",
                "password_minimum_length": "Password must be at least 8 characters long.",
                "group_not_found": "Group does not exist.",
                "chat_title": "Chat: {group}",
                "login_required": "Login is required.",
                "chat_history": "### Chat History",
                "message_input": "Enter your message",
                "send_button": "Send",
                "message_required": "Please enter a message.",
                "group_member_added_success": "Group member added successfully!",
                "group_member_add_error": "Error occurred while adding member: {error}",
                "group_details": "Group: {group_name}",
                "group_not_found": "Group not found.",
                "group_deleted_success": "Group deleted successfully!",
                "group_delete_error": "Error occurred while deleting group: {error}",
                "group_updated_success": "Group '{group_name}' updated successfully!",
                "db_error": "Database error: {error}",
                "already_member": "You are already a member of this group.",
                "group_joined_success": "Successfully joined the group '{group_name}'.",
                "group_blocked_success": "The group has been successfully blocked!",
                "group_block_error": "Error occurred while blocking the group: {error}",
                "group_unblocked_success": "The group block has been successfully lifted!",
                "group_not_blocked": "The group is not blocked.",
                "group_unblock_error": "Error occurred while unblocking the group: {error}",
                "blocked_groups_error": "Error occurred while retrieving blocked groups: {error}",
                "is_group_blocked_error": "Error occurred while checking if the group is blocked: {error}",
                "search_by_name": "Search by Name",
                "search_by_date": "Search by Date",
                "search_by_category": "Search by Category",
                "friend_list_title": "My Friend List",
                "no_friends": "No friends found.",
                "blocked_list_title": "Blocked List",
                "no_blocked_users": "No blocked users.",
                "block_self_error": "You cannot block yourself.",
                "user_not_found": "User ID not found.",
                "already_blocked": "This user is already blocked.",
                "block_success": "You have blocked {friend_id}.",
                "not_blocked_user": "This user is not blocked.",
                "unblock_success": "You have unblocked {friend_id}.",
                "delete_self_error": "You cannot delete yourself.",
                "not_in_friend_list": "This user is not in your friend list.",
                "delete_friend_success": "You have removed {friend_id} from your friend list.",
                "add_self_as_friend_error": "You cannot add yourself as a friend.",
                "unblock_before_request_error": "Please unblock the user before sending a request.",
                "user_id_not_found_error": "User ID not found.",
                "already_friends_error": "You are already friends.",
                "already_requested_error": "You have already sent a friend request.",
                "debug_my_friend_requests": "My Friend Requests:",
                "friend_request_sent_success": "You have sent a friend request to {friend_id}. Please wait for their acceptance.",
                "friend_request_accepted_success": "You are now friends with {requester_id}.",
                "friend_request_rejected_success": "You have rejected the friend request from {requester_id}.",
                "not_in_group": "You are not a member of this group.",
                "leave_group_success": "Successfully left the group '{group_id}'.",
                "leave_group_error": "Error occurred while leaving the group: {error}",
                "enter_recovery_token": "Recovery Token",
                "token_placeholder": "Enter the token received via email",
                "new_password_label": "New Password",
                "new_password_placeholder": "Enter your new password",
                "recover_password_button": "Recover Password",
                "all_fields_required": "Please fill in all fields.",
                "password_reset_success": "Your password has been successfully changed!",
                "invalid_or_expired_token": "Invalid or expired token.",
                "my_groups_expander": "My Groups",
                "no_joined_groups": "You have not joined any groups.",
                "group_name": "Group Name",
                "category": "Category",
                "status": "Status",
                "meeting_date": "Meeting Date",
                "meeting_time": "Meeting Time",
                "edit_button": "Edit",
                "delete_button": "Delete",
                "kick_member_button": "Kick Member",
                "kick_member_dialog": "Kick Member",
                "group_members_in": "Group Members in",
                "no_members": "No members in this group.",
                "admin_role": "Admin",
                "member_role": "Member",
                "kick_button": "Kick",
                "kick_success": "Successfully kicked {member_id} from the group.",
                "kick_error": "Error kicking {member_id} from the group.",
                "exit_group_dialog": "Exit Group",
                "exit_group_confirmation": "Do you really want to leave the group '{group_name}'?",
                "yes_button": "Yes",
                "no_button": "No",
                "exit_group_success": "Successfully left the group '{group_name}'.",
                "exit_group_cancelled": "Group exit cancelled.",
                "delete_group_dialog": "Delete Group",
                "delete_group_confirmation": "Do you really want to delete the group '{group_name}'?",
                "group_deleted": "Successfully deleted the group '{group_name}'.",
                "not_group_creator": "Only the group creator can delete this group.",
                "delete_group_cancelled": "Group deletion cancelled.",
                "my_groups_expander": "My Groups",
                "no_joined_groups": "You have not joined any groups.",
                "group_name": "Group Name",
                "category": "Category",
                "status": "Status",
                "chat": "group chat",
                "meeting_date": "Meeting Date",
                "meeting_time": "Meeting Time",
                "enter_chat_button": "Enter Chat",
                "leave_group_button": "Leave Group",
                "choose_language": "please choose language",
                "select_language": "selcet language"

            },
            "jp": {
                "check":"確認",
                "id_pw_change_title": "ID/PW変更",
                "no_user_info_error": "ユーザー情報がありません。もう一度ログインしてください。",
                "select_change_action": "変更する項目を選択してください",
                "change_id": "ID変更",
                "change_pw": "パスワード変更",
                "next_button": "次へ",
                "enter_new_value": "新しい{action}を入力してください",
                "save_button": "保存",
                "id_change_success": "IDが正常に変更されました。ログアウトしてホームページに戻ります。",
                "pw_change_success": "パスワードが正常に変更されました。ログアウトしてホームページに戻ります。",
                "login_page_title": "ログインページ",
                "user_id_input": "ユーザーID",
                "password_input": "パスワード",
                "login_button": "ログイン",
                "login_error_empty": "ユーザーIDとパスワードを入力してください。",
                "login_error_failed": "ログインに失敗しました。ユーザーIDまたはパスワードを確認してください。",
                "user_info_load_error": "ユーザー情報を読み込めませんでした。",
                "back_button": "戻る ↩️",
                "signup_page_title": "サインアップページ",
                "email_input": "メールアドレス",
                "signup_button": "会員登録",
                "signup_error_empty": "すべてのフィールドに入力してください。",
                "signup_success": "サインアップが完了しました！",
                "signup_error_failed": "サインアップに失敗しました。",
                "logout_button": "ログアウト",
                "logout_success": "ログアウトが完了しました。",
                "profile_button": "プロフィール",
                "view_post_button": "投稿を見る",
                "group_button": "グループページ",
                "recommended_posts": "おすすめの投稿",
                "home_title": "味ZIP",
                "find_id_pw_button": "ID/PW 検索",
                "page_not_found": "ページ '{page}' は見つかりません。",
                "no_previous_page": "前のページがありません。",
                "upload_post_header": "投稿の登録",
                "post_title_input": "投稿タイトル",
                "post_content_input": "投稿内容",
                "image_file_upload": "画像ファイル",
                "general_file_upload": "一般ファイル",
                "category_select": "カテゴリー",
                "group_id_not_found_error": "グループIDが見つかりません。",
                "post_register_button":"投稿登録",
                "post_register_success": "投稿が登録されました。",
                "user_info_not_found": "ユーザー情報が見つかりません。",
                "my_page_header": "マイページ",
                "friend_management": "友達管理",
                "my_friend_list_button": "マイフレンドリスト",
                "friend_requests_button": "友達リクエスト",

                "user_manager_page_title": "ユーザー管理ページ",
                "email_input_prompt": "メールアドレスを入力してください: ",
                "confirm_button": "確認",
                "select_category_label": "カテゴリー選択",
                "no_registered_categories_error": "登録されたカテゴリーがありません。管理者にお問い合わせください。",
                "password_recovery_email_sent": "パスワード復旧メールが送信されました",
                "friend_management": "友達管理",
                "my_friend_list_button": "友達リスト",
                "friend_requests_button": "友達リクエスト",
                "friend_requests_title": "友達リクエスト管理",
                "user_manager_page_title": "ユーザー管理ページ",
                "email_input_prompt": "メールアドレスを入力してください",
                "confirm_button": "確認",
                "password_recovery_email_sent": "パスワード復旧メールを送信しました。",
                "email_not_registered_warning": "登録されていないメールアドレスです。",
                "view_post_header": "投稿リスト",
                "upload_post_button": "投稿作成",
                "my_made_groups_expander": "作成したグループ",
                "no_maded_groups": "作成したグループがありません。",
                "group_name": "グループ名",
                "category": "カテゴリー",
                "status": "状態",
                "meeting_date": "予定日",
                "meeting_time": "予定時間",
                "edit_button": "編集",
                "delete_button": "削除",
                "group_deleted_success": "グループが削除されました。",
                "friend_requests_management": "友達リクエスト管理",
                "sent_friend_requests": "送信した友達リクエスト",
                "no_sent_requests": "送信した友達リクエストがありません。",
                "received_friend_requests": "受信した友達リクエスト",
                "accept": "承認",
                "reject": "拒否",
                "no_received_requests": "受信した友達リクエストがありません。",
                "group_page_title": "グループページ",
                "create_group_button": "グループ作成",
                "blocked_list_button": "ブロックリスト",
                "search_group_button": "グループ検索",
                "category": "カテゴリー",
                "status": "状態",
                "meeting_date": "約束日",
                "meeting_time": "約束時間",
                "members_count": "メンバー数",
                "not_set": "設定されていません",
                "detail_button": "詳細",
                "detail_group_page": "グループ詳細",
                "group_block_list_title": "ブロックされたグループリスト",
                "login_required_error": "ログインが必要です。",
                "no_blocked_groups": "ブロックされたグループが見つかりません。",
                "blocked_group_id": "ブロックされたグループ ID",
                "unblock_button": "ブロック解除",
                "unblock_success": "ブロック解除成功:",
                "unblock_error": "ブロック解除中にエラーが発生しました。",
                "group_request_list_title": "グループリクエストリスト",
                "no_requests": "保留中のリクエストはありません。",
                "requester_id": "リクエスター ID",
                "approve_request": "承認",
                "request_approved": "リクエストが承認されました。",
                "reject_request": "拒否",
                "request_rejected": "リクエストが拒否されました。",
                "group_detail_title": "グループ詳細",
                "no_group_error": "グループ情報がありません。",
                "group_info_not_found": "グループ情報が見つかりません。",
                "current_members": "現在のメンバー数",
                "last_modified": "最終更新日",
                "meeting_date": "会議日",
                "meeting_time": "会議時間",
                "friend_requests_title": "友達リクエスト保留",
                "not_set": "設定されていません",
                "group_members": "グループメンバー",
                "no_members_in_group": "このグループにはメンバーがいません。",
                "block_group": "グループをブロック",
                "unblock_group": "ブロックを解除",
                "group_blocked_success": "グループがブロックされました。",
                "group_blocked_error": "グループのブロック中にエラーが発生しました。",
                "group_unblocked_success": "グループのブロックが解除されました。",
                "group_unblocked_error": "ブロック解除中にエラーが発生しました。",
                "invite_to_group": "グループに招待",
                "enter_invitee_id": "招待するユーザーのIDを入力してください",
                "send_invite": "招待リクエストを送信",
                "invite_sent_success": "が招待されました。",
                "group_invite_confirmed": "グループ招待が確認されました。",
                "invite_failed": "招待リクエストの送信に失敗しました。",
                "enter_valid_invitee_id": "招待するユーザーのIDを入力してください",
                "group_block_list_title": "ブロックされたグループ一覧",
                "login_required": "ログインが必要です。",
                "no_blocked_groups": "ブロックされたグループはありません。",
                "blocked_group_id": "ブロックされたグループID",
                "unblock": "ブロック解除",
                "group_unblocked_success": "ブロック解除成功",
                "group_unblock_error": "ブロック解除失敗",
                "create_group_dialog_title": "グループ作成",
                "create_group_header": "グループ作成",
                "group_name_label": "グループ名",
                "group_name_placeholder": "グループ名を入力してください",
                "max_members_label": "最大メンバー数",
                "select_meeting_date_label": "会議の日付を選択",
                "select_meeting_time_label": "会議の時間を選択",
                "create_group_button": "グループ作成",
                "update_group_dialog_title": "グループ編集",
                "update_group_header": "グループ編集",
                "meeting_date_label": "会議の日付",
                "meeting_time_label": "会議の時間",
                "group_status_label": "グループステータス",
                "status_in_progress": "進行中",
                "status_completed": "完了",
                "status_canceled": "キャンセル",
                "update_group_button": "グループ編集",
                "search_group_dialog_title": "グループ検索",
                "search_group_header": "グループを検索して参加",
                "search_criteria_label": "検索基準を選択",
                "password_change_success": "パスワードが変更されました。",
                "password_minimum_length": "パスワードは8文字以上である必要があります。",
                "search_by_name": "名前",
                "search_by_date": "日付",
                "search_by_category": "カテゴリー",
                "group_name_prompt": "グループ名を入力してください",
                "meeting_date_prompt": "会議の日付を選択してください",
                "search_button_label": "検索",
                "no_search_results": "検索結果が見つかりませんでした。",
                "group_name": "グループ名",
                "group_leader": "グループリーダー",
                "current_members": "現在のメンバー数",
                "meeting_date": "会議の日付",
                "meeting_time": "会議の時間",
                "category": "カテゴリー",
                "location": "場所",
                "join_group": "グループ参加",
                "friend_request_input_label": "友達リクエストを送るIDを入力してください:",
                "friend_request_button": "友達リクエストを送る",
                "friend_request_warning": "友達リクエストを送るIDを入力してください。",
                "unblock_friend_dialog_title": "友達のブロック解除ダイアログ",
                "unblock_friend_input_label": "友達のブロック解除するIDを入力してください:",
                "unblock_friend_button": "友達のブロックを解除",
                "unblock_friend_warning": "友達のブロック解除するIDを入力してください。",
                "blocked_list_title": "ブロックされた友達一覧",
                "blocked_users_subheader": "現在ブロックされているユーザー:",
                "no_blocked_users": "ブロックされているユーザーはいません。",
                "no_friend_id_error": "友達IDが見つかりません。",
                "friend_posts_title": "{friend_id}さんの投稿",
                "no_image_message": "画像がありません。",
                "no_posts_warning": "投稿はありません。",
                "db_error": "データベースエラー: {error}",
                "delete_friend_dialog_title": "友達削除ダイアログ",
                "delete_friend_input_label": "友達を削除するIDを入力してください:",
                "delete_friend_button": "友達を削除",
                "delete_friend_warning": "友達を削除するIDを入力してください。",
                "block_friend_dialog_title": "友達をブロックするダイアログ",
                "block_friend_input_label": "友達をブロックするIDを入力してください:",
                "block_friend_button": "友達をブロック",
                "block_friend_warning": "友達をブロックするIDを入力してください。",
                "friend_requests_dialog_title": "友達リクエスト待機ダイアログ",
                "friend_list_title": "私の友達リスト",
                "send_friend_request_button": "友達リクエストを送る",
                "password_length_error": "パスワードは8文字以上である必要があります。",
                "user_id_exists_error": "このユーザーIDは既に使用されています。",
                "login_success": "{user_id}さん、ログイン成功！",
                "password_incorrect_error": "パスワードが間違っています。",
                "user_id_not_found_error": "ユーザーIDが存在しません。",
                "no_search_results": "検索結果がありません。",
                "api_request_error": "APIリクエストエラー: {status_code}",
                "search_location_input": "検索したい場所を入力してください:",
                "search_button": "検索",
                "select_search_result": "検索結果を選択してください:",
                "place_name": "場所名",
                "address": "住所",
                "password_recovery_subject": "パスワード復旧トークン",
                "password_recovery_body": "こんにちは、\n\nパスワードの復旧リクエストを受け付けました。以下の復旧トークンを使用してください：\n\n{token}\n\nこのリクエストを自分で行っていない場合、このメールを無視してください。",
                "email_sent_success": "{email} に復旧メールが正常に送信されました。",
                "email_failed_smtp": "SMTPエラーによりメール送信に失敗しました：{error}",
                "email_failed_generic": "予期しないエラーによりメール送信に失敗しました：{error}",
                "invalid_token": "無効なトークンです。",
                "password_reset_success": "パスワードが正常に復旧されました。",
                "user_not_found": "ユーザーID '{user_id}' が見つかりません。",
                "missing_required_fields": "すべての必須項目を入力してください。",
                "status_in_progress": "進行中",
                "group_creation_success": "「{group_name}」グループが正常に作成されました！",
                "no_posts_found": "ユーザーID「{user_id}」で作成された投稿がありません。",
                "post_retrieval_error": "投稿の取得中にエラーが発生しました: {error}",
                "like_removed": "いいねを取り消しました。",
                "like_added": "いいねを追加しました！",
                "total_likes": "合計いいね数: {total_likes}",
                "unlike_button": "いいね取り消し",
                "like_button": "いいね",
                "no_locations_found": "場所が存在しません。",
                "location_name": "場所の名前: {name}",
                "location_address": "住所: {address}",
                "no_location_data": "位置データがありません。",
                "edit_post_title_label": "投稿のタイトル",
                "edit_post_content_label": "投稿の内容",
                "edit_post_image_upload": "画像ファイル",
                "edit_post_file_upload": "通常ファイル",
                "edit_post_category_label": "カテゴリー",
                "edit_post_submit_button": "投稿を修正する",
                "edit_post_success_message": "投稿が修正されました。",
                "edit_post_not_found_error": "該当する投稿が存在しません。",
                "post_id_and_title": "投稿ID: {post_id}, タイトル: {title}",
                "post_content": "内容: {content}",
                "delete_post_button": "削除",
                "delete_post_success_message": "投稿『{title}』が削除されました。",
                "edit_post_expander": "修正",
                "location_map_title": "位置地図",
                "post_dates": "**登録日**: {upload_date}, **修正日**: {modify_date}",
                "sort_posts_label": "並べ替え方式",
                "sort_by_latest": "最新順",
                "sort_by_popularity": "人気順",
                "no_recommended_posts_message": "現在おすすめの投稿はありません。",
                "view_more_expander": "もっと見る",
                "dark_mode_button_label": "ダークモード 🌜",
                "light_mode_button_label": "ライトモード 🌞",
                "user_email": "ユーザーのメール: {email}",
                "user_info_not_found": "ユーザー情報が見つかりません。",
                "change_profile_picture": "プロフィール写真の変更",
                "upload_new_profile_picture": "新しいプロフィール写真をアップロード",
                "upload_button": "アップロード",
                "profile_picture_updated": "プロフィール写真が正常に更新されました。",
                "file_save_failed": "ファイルの保存に失敗しました。",
                "field_updated": "{field}が正常に更新されました。",
                "user_info_fetch_failed": "更新後のユーザー情報の取得に失敗しました。",
                "field_update_failed": "ユーザー情報の更新に失敗しました。",
                "alarm_settings": "アラーム設定",
                "alarm_enabled": "アラームが設定されました。",
                "alarm_disabled": "アラームが解除されました。",
                "edit_my_info": "自分の情報を編集",
                "new_email": "新しいメールアドレス",
                "change_email_button": "メールアドレスを変更",
                "new_password": "新しいパスワード",
                "change_password_button": "パスワードを変更",
                "profile_picture_changed": "プロフィール写真が変更されました。",
                "favorites": "お気に入り",
                "message_saved": "{sender}さんのメッセージが保存されました。",
                "group_not_found": "グループが存在しません。",
                "chat_title": "チャット: {group}",
                "login_required": "ログインが必要です。",
                "chat_history": "### チャット履歴",
                "message_input": "メッセージを入力してください",
                "send_button": "送信",
                "message_required": "メッセージを入力してください。",
                "group_member_added_success": "グループメンバーが正常に追加されました！",
                "group_member_add_error": "メンバー追加中にエラーが発生しました: {error}",
                "group_details": "グループ: {group_name}",
                "group_not_found": "グループが見つかりません。",
                "group_deleted_success": "グループが正常に削除されました！",
                "group_delete_error": "グループ削除中にエラーが発生しました: {error}",
                "group_updated_success": "'{group_name}' グループが正常に更新されました！",
                "db_error": "データベースエラー: {error}",
                "already_member": "既にこのグループのメンバーです。",
                "group_joined_success": "'{group_name}' グループに正常に参加しました。",
                "group_blocked_success": "グループが正常にブロックされました！",
                "group_block_error": "グループをブロック中にエラーが発生しました: {error}",
                "group_unblocked_success": "グループのブロックが正常に解除されました！",
                "group_not_blocked": "ブロックされたグループは存在しません。",
                "group_unblock_error": "グループのブロック解除中にエラーが発生しました: {error}",
                "blocked_groups_error": "ブロックされたグループの取得中にエラーが発生しました: {error}",
                "is_group_blocked_error": "グループがブロックされているか確認中にエラーが発生しました: {error}",
                "search_by_name": "名前で検索",
                "search_by_date": "日付で検索",
                "search_by_category": "カテゴリーで検索",
                "friend_list_title": "私の友達リスト",
                "no_friends": "友達がいません。",
                "blocked_list_title": "ブロックリスト",
                "no_blocked_users": "ブロックされたユーザーはいません。",
                "block_self_error": "自分自身をブロックすることはできません。",
                "user_not_found": "ユーザーIDが見つかりません。",
                "already_blocked": "このユーザーは既にブロックされています。",
                "block_success": "{friend_id}をブロックしました。",
                "not_blocked_user": "このユーザーはブロックされていません。",
                "unblock_success": "{friend_id}のブロックを解除しました。",
                "delete_self_error": "自分自身を削除することはできません。",
                "not_in_friend_list": "このユーザーは友達リストにいません。",
                "delete_friend_success": "{friend_id}を友達リストから削除しました。",
                "add_self_as_friend_error": "自分を友達に追加することはできません。",
                "unblock_before_request_error": "リクエストを送信する前にブロックを解除してください。",
                "user_id_not_found_error": "ユーザーIDが見つかりません。",
                "already_friends_error": "既に友達です。",
                "already_requested_error": "既に友達リクエストを送信しました。",
                "debug_my_friend_requests": "送信した友達リクエスト：",
                "friend_request_sent_success": "{friend_id}に友達リクエストを送りました。承認をお待ちください。",
                "friend_request_accepted_success": "{requester_id}と友達になりました。",
                "friend_request_rejected_success": "{requester_id}からの友達リクエストを拒否しました。",
                "enter_recovery_token": "復旧トークン",
                "token_placeholder": "メールで受け取ったトークンを入力してください",
                "new_password_label": "新しいパスワード",
                "new_password_placeholder": "新しいパスワードを入力してください",
                "recover_password_button": "パスワードを復旧する",
                "all_fields_required": "すべてのフィールドを入力してください。",
                "password_reset_success": "パスワードが正常に変更されました！",
                "invalid_or_expired_token": "無効または期限切れのトークンです。",
                "not_in_group": "このグループに所属していません。",
                "leave_group_success": "'{group_id}' グループを正常に脱退しました。",
                "leave_group_error": "グループ脱退中にエラーが発生しました: {error}",
                "my_groups_expander": "参加中のグループリスト",
                "no_joined_groups": "参加中のグループはありません。",
                "group_name": "グループ名",
                "category": "カテゴリー",
                "status": "状態",
                "meeting_date": "約束日",
                "meeting_time": "約束時間",
                "enter_chat_button": "チャットに参加",
                "leave_group_button": "グループを脱退",
                "my_groups_expander": "参加中のグループリスト",
                "no_joined_groups": "参加中のグループはありません。",
                "group_name": "グループ名",
                "category": "カテゴリー",
                "status": "状態",
                "meeting_date": "約束日",
                "meeting_time": "約束時間",
                "edit_button": "編集",
                "delete_button": "削除",
                "kick_member_button": "メンバーを追放",
                "kick_member_dialog": "メンバーを追放",
                "group_members_in": "グループのメンバー",
                "no_members": "このグループにはメンバーがいません。",
                "admin_role": "管理者",
                "member_role": "メンバー",
                "kick_button": "追放",
                "kick_success": "{member_id}さんをグループから追放しました。",
                "kick_error": "{member_id}さんを追放中にエラーが発生しました。",
                "exit_group_dialog": "グループを退出",
                "exit_group_confirmation": "本当にグループ「{group_name}」を退出しますか？",
                "yes_button": "はい",
                "no_button": "いいえ",
                "chat": "グループチェチング",
                "exit_group_success": "グループ「{group_name}」を正常に退出しました。",
                "exit_group_cancelled": "グループ退出がキャンセルされました。",
                "delete_group_dialog": "グループを削除",
                "delete_group_confirmation": "本当にグループ「{group_name}」を削除しますか？",
                "group_deleted": "グループ「{group_name}」を正常に削除しました。",
                "not_group_creator": "グループ作成者のみがこのグループを削除できます。",
                "delete_group_cancelled": "グループ削除がキャンセルされました。",
                "choose_language": "言語を選んでください。",
                "select_language": "言語選択"

            }

        }

    def get_text(self, key):

        try:
            return self.translations[self.lang][key]
        except KeyError:
            st.warning(f"'{key}' not found in language '{self.lang}'.")
            return key

    def switch_language(self, new_lang):

        if new_lang in self.translations:
            self.lang = new_lang
        else:
            st.error(f"Language '{new_lang}' is not supported.")

    def show_translations(self):

        st.json(self.translations.get(self.lang, {}))


session = SessionLocal()

# Streamlit 상태 초기화
if 'localization' not in st.session_state:
    st.session_state.localization = Localization(lang='ko')  # 기본값으로 한국어 설정
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'ko'  # 현재 언어 상태 관리

# Localization 객체 가져오기
localization = st.session_state.localization


# -----------------------------------------------페이지 전환 ----------------------------------------------------------


class Page:

    def __init__(self):
        # 세션 상태 초기화
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'Home'  # Default to Home if not set
        if 'history' not in st.session_state:
            st.session_state['history'] = []
        # TurnPages 클래스 인스턴스 생성
        self.turn_pages = TurnPages(self)
        self.group_page = GroupPage(self)
        self.friend_page = FriendPage(self)

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
            'ID PW 변경': self.turn_pages.change_password_page,
            'Upload Post': self.turn_pages.upload_post,
            'Group page': self.group_page.groups_page,
            'Detail group': self.group_page.detail_group,
            'GroupBlockList': self.group_page.group_block_list_page,
            'Group Update Page': self.group_page.group_update_page,  # 그룹 수정 페이지 등록
            'Friend List Page': self.friend_page.FriendList_page,
            "FriendRequests": self.turn_pages.show_friend_requests_page

        }

        # 현재 페이지 렌더링
        if st.session_state.current_page in page_functions:
            page_functions[st.session_state.current_page]()  # 매핑된 함수 호출
        else:
            st.warning(localization.get_text("page_not_found"))  # 잘못된 페이지 처리

    # 페이지 전환 함수
    def change_page(self, page_name: str):
        # 방문 기록을 세션에 저장
        if st.session_state["current_page"] != page_name:
            st.session_state["history"].append(st.session_state["current_page"])
            st.session_state["current_page"] = page_name
            st.rerun()

    # 뒤로가기 함수
    def go_back(self):
        # 세션에 기록된 이전 페이지로 돌아가기
        if 'history' in st.session_state and st.session_state.history:
            st.session_state.current_page = st.session_state.history.pop()  # 이전 페이지로 이동
            st.rerun()  # 재귀 문제를 피할 수 있는 안정적인 rerun 방식
        else:
            st.warning(localization.get_text("no_previous_page"))  # 방문 기록이 없을 경우 처리
            st.rerun()  # 재귀 문제를 피할 수 있는 안정적인 rerun 방식

        # 홈 페이지 함수 (로그인 전)

    def home_page(self):
        col1, col2 = st.columns(2)  # 동일한 너비의 세 개 열 생성
        with col1:
            st.title(localization.get_text("home_title"))

        with col2:
            col3, col4, col5 = st.columns(3)
            with col3:
                if st.button(localization.get_text("login_button"), key="home_login_button", use_container_width=True):
                    self.turn_pages.login_page()
            with col4:
                if st.button(localization.get_text("signup_button"), key="home_signup_button",
                             use_container_width=True):
                    self.turn_pages.signup_page()  # 수정된 부분: self.turn_pages.signup_page()
            with col5:
                if st.button(localization.get_text("find_id_pw_button"), key="home_forgot_button",
                             use_container_width=True):
                    self.turn_pages.usermanager_page()

        post_manager = PostManager()  # 인스턴스 생성
        post_manager.display_posts_on_home(None)  # display_posts_on_home 메서드 호출


class TurnPages:
    def __init__(self, page: Page):

        self.page = page
        self.friend_page = FriendPage

    def change_password_page(self):
        st.title(localization.get_text("change_password_title"))

        # 현재 로그인된 사용자 ID 가져오기
        user_id = st.session_state.get('logged_in_user')
        if not user_id:
            st.error(localization.get_text("no_user_info_error"))
            self.page.change_page('Login')  # 로그인 페이지로 이동
            return

        # 새 비밀번호 입력
        new_password = st.text_input(localization.get_text("enter_new_password"), type="password")
        if st.button(localization.get_text("save_button"), use_container_width=True):
            if new_password:
                try:
                    # 비밀번호 변경 로직
                    user = session.query(User).filter(User.user_id == user_id).first()
                    if user:
                        # 비밀번호를 해싱하여 저장
                        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                        user.password = hashed_password
                        session.commit()
                        st.success(localization.get_text("password_change_success"))
                        st.session_state.clear()  # 세션 초기화로 로그아웃 처리
                        self.page.change_page('Login')  # 로그인 페이지로 이동
                    else:
                        st.error(localization.get_text("user_not_found"))
                except Exception as e:
                    session.rollback()
                    st.error(localization.get_text("password_change_error").format(error=str(e)))
                finally:
                    session.close()
            else:
                st.warning(localization.get_text("password_empty_warning"))

    @st.dialog(localization.get_text("login_page_title"))
    def login_page(self):
        user_id = st.text_input(localization.get_text("user_id_input"), key="login_user_id_input")
        user_password = st.text_input(localization.get_text("password_input"), type='password',
                                      key="login_password_input")

        if st.button(localization.get_text("login_button"), key="login_submit_button", use_container_width=True):
            if not user_id or not user_password:
                st.error(localization.get_text("login_error_empty"))
            else:
                # UserVO 객체 생성 (일단 최소 정보로 생성)
                user_vo = UserVO(user_id=user_id, user_password=user_password, user_email="")

                # SignIn 객체 생성
                sign_in = SignIn(user_vo)

                if sign_in.sign_in_event():  # 로그인 성공 시
                    dao = UserDAO()
                    user_vo = dao.get_user_vo(user_id)  # UserVO 객체를 반환

                    if user_vo:
                        # user_vo가 정상적으로 반환되면 처리
                        st.session_state['user_data'] = {
                            "user_id": user_vo.user_id,
                            "user_name": user_vo.user_id,  # 여기서는 user_id로 대체 (이름 컬럼 추가 시 수정 필요)
                            "profile_picture": user_vo.user_profile_picture if user_vo.user_profile_picture else "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
                            "user_email": user_vo.user_email,  # 추가 정보 포함
                        }
                    else:
                        st.error(localization.get_text("user_info_load_error"))
                        self.page.change_page('Login')

                    # 이후 user_data 사용하여 UI 처리
                    user_data = st.session_state.get('user_data')
                    # 이메일을 포함한 추가 정보를 UserVO에 업데이트
                    user_vo.user_email = user_data['user_email']
                    user_vo.profile_picture_path = user_data['profile_picture']

                    # 로그인 후 홈화면으로 이동
                    self.page.change_page('after_login')
                else:
                    st.error(localization.get_text("login_error_failed"))

    @st.dialog(localization.get_text("signup_page_title"))
    def signup_page(self):
        # 사용자 입력 받기
        user_id = st.text_input(localization.get_text("user_id_input"))
        user_password = st.text_input(localization.get_text("password_input"), type='password')
        email = st.text_input(localization.get_text("email_input"))

        if st.button(localization.get_text("signup_button"), key="signup_submit_button", use_container_width=True):
            if not user_id or not user_password or not email:
                st.error(localization.get_text("signup_error_empty"))
            else:
                # UserVO 객체 생성
                user_vo = UserVO(user_id=user_id, user_password=user_password, user_email=email)

                # SignUp 객체 생성
                signup = SignUp(user_vo)

                # 회원가입 이벤트 처리
                if signup.sign_up_event():
                    st.success(localization.get_text("signup_success"))
                    self.page.change_page('Home')
                else:
                    st.error(localization.get_text("signup_error_failed"))

    def after_login(self):
        # 타이틀을 중앙에 크게 배치
        st.markdown(f"<h1 style='text-align: center;'>{localization.get_text('home_title')}</h1>",
                    unsafe_allow_html=True)
        # 사용자 정보
        user_id = st.session_state.get("user_id")
        # 로그인 정보 없을 시 처리
        if not user_id:
            st.error(localization.get_text("login_required_error"))
            self.page.change_page('Login')

        dao = UserDAO()
        user_vo = dao.get_user_vo(user_id)  # UserVO 객체를 반환

        if user_vo:
            # user_vo가 정상적으로 반환되면 처리
            st.session_state['user_data'] = {
                "user_id": user_vo.user_id,
                "user_name": user_vo.user_id,  # 여기서는 user_id로 대체 (이름 컬럼 추가 시 수정 필요)
                "profile_picture": user_vo.user_profile_picture if user_vo.user_profile_picture else "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
                "user_email": user_vo.user_email,  # 추가 정보 포함
            }
        else:
            st.error(localization.get_text("user_info_load_error"))
            self.page.change_page('Login')

        # 이후 user_data 사용하여 UI 처리
        user_data = st.session_state.get('user_data')

        # 사용자 ID 표시 및 로그아웃 버튼
        col1, col2, col3, col4 = st.columns([1, 4, 2, 1])
        if user_data:
            user_name = user_data['user_name']
            with col1:
                profile_picture = user_data['profile_picture']
                st.image(profile_picture)
            with col2:
                st.write(f"**{user_name}**")
            with col3:
                if st.button(localization.get_text("logout_button"), key="logout_button", use_container_width=True):
                    st.session_state.clear()
                    st.warning(localization.get_text("logout_success"))
                    st.rerun()
            with col4:
                if st.button(localization.get_text("profile_button"), key="profile_button", use_container_width=True):
                    self.page.change_page("Setting")
        else:
            st.error(localization.get_text("no_user_info_error"))

        # 중앙 포스팅 리스트
        st.title(localization.get_text("recommended_posts"))
        # PostManager 클래스의 인스턴스 생성 후 display_posts_on_home 호출
        post_manager = PostManager()  # 인스턴스 생성
        post_manager.display_posts_on_home(user_id)  # display_posts_on_home 메서드 호출
        self.sidebar()

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

    def upload_post(self):
        user_id = st.session_state.get("user_id")
        st.header(localization.get_text("upload_post_header"))
        title = st.text_input(localization.get_text("post_title_input"))
        content = st.text_area(localization.get_text("post_content_input"))
        image_file = st.file_uploader(localization.get_text("image_file_upload"), type=['jpg', 'png', 'jpeg'])
        file_file = st.file_uploader(localization.get_text("general_file_upload"),
                                     type=['pdf', 'docx', 'txt', 'png', 'jpg'])

        # 카테고리 선택을 위한 Selectbox
        post_manager = PostManager('uploads')  # DB 경로 설정
        category_manager = CategoryManager()
        category_names = category_manager.get_category_names()  # 카테고리 이름만 가져옴

        # Selectbox에서 카테고리 선택
        selected_category_name = st.selectbox(localization.get_text("category_select"), category_names)

        # 선택한 카테고리 이름에 해당하는 category_id 구하기
        categories = category_manager.get_category_options()
        category_dict = {category.category: category.category_id for category in categories}
        selected_category_id = category_dict[selected_category_name]

        location_search = LocationSearch()
        location_search.display_location_on_map()
        col1, col2 = st.columns([6, 2])
        with col1:
            if st.button(localization.get_text("post_register_button"), use_container_width=True):
                location_search.add_post(user_id, title, content, image_file, file_file, selected_category_id)
                st.success(localization.get_text("post_register_success"))
        with col2:
            if st.button(localization.get_text("back_button"), use_container_width=True):
                self.page.go_back()  # 뒤로가기 로직 호출

    def setting_page(self):
        # 로그인 정보 가져오기
        user_id = st.session_state.get("user_id")

        if not user_id:
            st.error(localization.get_text("no_user_info_error"))
            self.page.change_page('Login')
            return

        # 세션 상태에서 캐시된 사용자 정보 확인
        user_vo = st.session_state.get("user_vo")

        if not user_vo or user_vo.user_id != user_id:
            # 캐시된 사용자 정보가 없거나 로그인한 사용자와 일치하지 않으면
            # DB에서 새로 가져오기
            dao = UserDAO()
            user_vo = dao.get_user_vo(user_id)

            if not user_vo:
                st.error(localization.get_text("user_info_not_found"))
                return

            # 세션에 사용자 정보를 캐시
            st.session_state["user_vo"] = user_vo

        # 페이지 UI 구성
        col1, col2 = st.columns([8, 2])
        with col1:
            st.title(localization.get_text("my_page_header"))
        with col2:
            if st.button(localization.get_text("back_button"), use_container_width=True):
                self.page.go_back()

                # 사용자 프로필, 알림 설정 및 테마 버튼을 렌더링하는 뷰 클래스
        view = SetView(user_vo)  # UserVO 객체 전달
        view.render_user_profile()

        # 테마 관리 버튼
        theme_manager = ThemeManager(user_id)
        theme_manager.render_button(user_id)
        theme_manager.select_language(user_id)
        # 사용자의 게시물 렌더링
        view.render_posts()
        self.view_my_group()
        self.view_my_groups()

        # 친구 및 그룹 관리 사이드바

    def sidebar(self):

        st.sidebar.title(localization.get_text("home_title"))

        # 친구 리스트
        if st.sidebar.button(localization.get_text("my_friend_list_button"), use_container_width=True):
            self.page.change_page("Friend List Page")

        if st.sidebar.button(localization.get_text("view_post_button"), key='view_post_button',
                             use_container_width=True):
            self.page.change_page('View Post')

        if st.sidebar.button(localization.get_text("group_button"), key='group_button', use_container_width=True):
            self.page.change_page("Group page")

        if "action" in st.session_state:
            st.write(st.session_state["action"])
            del st.session_state["action"]

    @st.dialog(localization.get_text("user_manager_page_title"))
    def usermanager_page(self):

        email = st.text_input(localization.get_text("email_input_prompt"))
        # SMTP 이메일과 비밀번호를 초기화
        smtp_email = "kgus0203001@gmail.com"  # 발신 이메일 주소
        smtp_password = "pwhj fwkw yqzg ujha"  # 발신 이메일 비밀번호
        if st.button(localization.get_text("confirm_button"), key="forgot_confirm_button", use_container_width=True):

            user_manager = UserManager(smtp_email, smtp_password)

            # 이메일 등록 여부 확인
            user_info = user_manager.is_email_registered(email)
            if user_info:
                st.success(localization.get_text("password_recovery_email_sent"))
                user_manager.save_recovery_token(email)
                user_manager.send_recovery_email(email)

            else:
                st.warning(localization.get_text("email_not_registered_warning"))
                return
        # 복구 토큰 입력 받기
        token = st.text_input(localization.get_text("enter_recovery_token"),
                              placeholder=localization.get_text("token_placeholder"))

        # 새 비밀번호 입력
        new_password = st.text_input(localization.get_text("new_password_label"),
                                     placeholder=localization.get_text("new_password_placeholder"), type="password")

        # 비밀번호 복구 버튼 클릭
        if st.button(localization.get_text("recover_password_button"), use_container_width=True):
            if not email or not token or not new_password:
                st.error(localization.get_text("all_fields_required"))
                return

            # 비밀번호 복구를 위한 UserManager 인스턴스 생성
            user_manager = UserManager(smtp_email, smtp_password)

            # 토큰 검증 후 비밀번호 재설정
            if user_manager.verify_token(email, token):
                if len(new_password)>=8:
                    st.success(localization.get_text("password_reset_success"))
                else:
                    st.warning('비밀번호는 8자리 이상입니다')
            else:
                st.error(localization.get_text("invalid_or_expired_token"))

            # 뒤로가기 버튼
            if st.button(localization.get_text("back_button"), use_container_width=True):
                self.page.go_back()

    # 게시글 목록

    def view_post(self):
        user_id = st.session_state.get("user_id")
        col1, col2, col3 = st.columns([6, 2, 2])  # 비율 6 : 2 : 2
        with col1:
            st.title(localization.get_text("view_post_header"))  # 제목을 왼쪽에 배치
        with col2:
            if st.button(localization.get_text("back_button"), use_container_width=True):
                self.page.go_back()  # 뒤로가기 로직 호출
        with col3:
            if st.button(localization.get_text("upload_post_button"), use_container_width=True):
                self.page.change_page('Upload Post')
        # PostManager 인스턴스를 생성
        post_manager = PostManager()
        # display_posts 메서드를 호출
        post_manager.display_posts(user_id)

        # 내그룹 보기

    def view_my_group(self):
        user_id = st.session_state.get("user_id")
        with st.expander(localization.get_text("my_made_groups_expander"), icon='🍙'):
            group_manager = GroupManager(user_id)
            groups = group_manager.get_my_groups()
            if not groups:
                st.info(localization.get_text("no_joined_groups"))
                return

            for group in groups:
                st.markdown(f"**{localization.get_text('group_name')}:** {group['group_name']}")
                st.markdown(f"**{localization.get_text('category')}:** {group['category']}")
                st.markdown(f"**{localization.get_text('status')}:** {group['status']}")
                st.markdown(f"**{localization.get_text('meeting_date')}:** {group['meeting_date']}")
                st.markdown(f"**{localization.get_text('meeting_time')}:** {group['meeting_time']}")

                # 수정 버튼
                if st.button(localization.get_text("edit_button"), key=f"edit_{group['group_id']}",
                             use_container_width=True):
                    st.session_state["group_id"] = group['group_id']
                    self.page.change_page('Group Update Page')

                # 삭제 버튼
                if st.button(localization.get_text("delete_button"), key=f"delete_{group['group_id']}",
                             use_container_width=True):
                    st.session_state["delete_group_id"] = group["group_id"]
                    st.session_state["delete_group_name"] = group["group_name"]
                    if group_manager.is_group_creator(group['group_id']):
                        group_manager.delete_group(group['group_id'])
                        if group_manager.is_group_creator(group['group_id']):
                            self.show_delete_confirmation_dialog()
                # 그룹원 내쫓기 버튼
                if st.button(localization.get_text("kick_member_button"), key=f"kick_{group['group_id']}",
                             use_container_width=True):
                    self.kick_member(group['group_id'], group['group_name'])

    @st.dialog(localization.get_text("kick_member_dialog"))
    def kick_member(self, group_id, group_name):
        st.markdown(f"### {localization.get_text('group_members_in')} '{group_name}'")

        user_id = st.session_state.get("user_id")
        group_manager = GroupManager(user_id)

        group_members = group_manager.get_group_members(group_id)

        if not group_members:
            st.warning(localization.get_text("no_members"))
            return

        for member in group_members:
            member_id, role = member[0], member[1]
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(
                    f"- {member_id} ({localization.get_text('admin_role') if role == 'admin' else localization.get_text('member_role')})")
            with col2:
                if member_id != user_id:  # 본인은 내쫓을 수 없음
                    if st.button(localization.get_text("kick_button"), key=f"kick_member_{group_id}_{member_id}"):
                        if group_manager.kick_member(group_id, member_id):
                            st.success(localization.get_text("kick_success").format(member_id=member_id))
                            st.session_state["page_refresh"] = True
                            st.rerun()
                        else:
                            st.error(localization.get_text("kick_error").format(member_id=member_id))

    @st.dialog(localization.get_text("check"))
    def exit_group(self, group_id, group_name):
        st.write(localization.get_text("exit_group_confirmation").format(group_name=group_name))
        col_yes, col_no = st.columns(2)
        user_id = st.session_state.get("user_id")
        group_manager = GroupManager(user_id)

        with col_yes:
            if st.button(localization.get_text("yes_button"), key="confirm_yes_button", use_container_width=True,
                         type='primary'):
                success = group_manager.leave_group(group_id)
                if success:
                    st.success(localization.get_text("exit_group_success").format(group_name=group_name))
                    st.rerun()

        with col_no:
            if st.button(localization.get_text("no_button"), key="confirm_no_button", use_container_width=True,
                         type='primary'):
                st.info(localization.get_text("exit_group_cancelled"))

    @st.dialog(localization.get_text("delete_group_dialog"))
    def show_delete_confirmation_dialog(self):
        user_id = st.session_state.get("user_id")
        group_manager = GroupManager(user_id)

        if "delete_group_id" in st.session_state:
            with st.container():
                st.markdown(localization.get_text("delete_group_confirmation").format(
                    group_name=st.session_state['delete_group_name']))

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(localization.get_text("yes_button"),
                                 key=f"confirm_delete_{st.session_state['delete_group_id']}",
                                 use_container_width=True, type="primary"):
                        group_id = st.session_state["delete_group_id"]
                        if group_manager.is_group_creator(group_id):
                            group_manager.delete_group(group_id)
                            st.success(localization.get_text("group_deleted").format(
                                group_name=st.session_state['delete_group_name']))
                        else:
                            st.error(localization.get_text("not_group_creator"))

                        del st.session_state["delete_group_id"]
                        del st.session_state["delete_group_name"]
                        st.rerun()

                with col2:
                    if st.button(localization.get_text("no_button"),
                                 key=f"cancel_delete_{st.session_state['delete_group_id']}",
                                 use_container_width=True, type="primary"):
                        st.info(localization.get_text("delete_group_cancelled"))
                        del st.session_state["delete_group_id"]
                        del st.session_state["delete_group_name"]
                        st.rerun()

    def view_my_groups(self):
        # 내가 속한 그룹 목록 조회
        user_id = st.session_state.get("user_id")
        group_manager = GroupManager(user_id)

        # 유저가 속한 그룹인지 확인한다.

        with st.expander(localization.get_text("my_groups_expander"), icon='🍙'):
            groups = group_manager.get_user_groups()

            if not groups:
                st.info(localization.get_text("no_joined_groups"))
                return

            for group in groups:
                st.markdown(f"**{localization.get_text('group_name')}:** {group.group_name}")
                st.markdown(f"**{localization.get_text('category')}:** {group.category}")
                st.markdown(f"**{localization.get_text('status')}:** {group.status}")
                st.markdown(f"**{localization.get_text('meeting_date')}:** {group.meeting_date}")
                st.markdown(f"**{localization.get_text('meeting_time')}:** {group.meeting_time}")

                # 그룹원 표시
                if st.button(localization.get_text("enter_chat_button"), key=f'enter_chat_{group.group_id}', use_container_width=True):
                    chatting = Chatting(group.group_id)  # session 객체 필요
                    chatting.display_chat_interface()

                if st.button(localization.get_text("leave_group_button"), key=f'out_group_{group.group_id}', use_container_width=True):
                    self.exit_group(group.group_id, group.group_name)

    # 대기 중인 친구 요청을 표시하는 함수
    def show_friend_requests_page(self):
        user_id = st.session_state.get("user_id")
        friend_request = FriendRequest(user_id)
        received_requests = friend_request.get_received_requests()
        st.title(localization.get_text("friend_requests_management"))

        # 내가 보낸 요청 목록
        st.subheader(localization.get_text("sent_friend_requests"))
        sent_requests = friend_request.get_my_sent_requests()
        if sent_requests:
            for req in sent_requests:
                st.write(f"- {req['requested_user_id']}")
        else:
            st.write(localization.get_text("no_sent_requests"))

        # 내가 받은 요청 목록
        st.subheader(localization.get_text("received_friend_requests"))

        if received_requests:
            for req in received_requests:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"- {req['requester_user_id']}")
                with col2:
                    if st.button(f"{localization.get_text('accept')} ({req['requester_user_id']})",
                                 key=f"accept_{req['requester_user_id']}", use_container_width=True):
                        friend_request.accept_friend_request(req['requester_user_id'])
                    if st.button(f"{localization.get_text('reject')} ({req['requester_user_id']})",
                                 key=f"reject_{req['requester_user_id']}", use_container_width=True):
                        friend_request.reject_friend_request(req['requester_user_id'])
        else:
            st.write(localization.get_text("no_received_requests"))

        # 뒤로 가기 버튼 추가
        if st.button(localization.get_text("back_button")):
            st.session_state["current_page"] = "after_login"  # 이전 페이지로 설정
            st.session_state["refresh"] = True  # 새로고침 플래그 설정
            st.rerun()


# -----------------------------------------------------그룹 페이지--------------------------------------------

class GroupPage():
    def __init__(self, page: Page):
        self.user_id = st.session_state.get("user_id")
        self.page = page
        self.category_manager = CategoryManager()
        self.group_manager = GroupManager(self.user_id)
        self.location_manager = LocationSearch

    # 내 그룹 페이지
    def groups_page(self):
        # 상단 제목 설정 (좌측 정렬)
        col1, col2 = st.columns([3, 5])  # 버튼을 위한 공간 추가
        with col1:
            st.markdown(
                f"<h1 class='centered-title'>{localization.get_text('group_page_title')}</h1>",
                unsafe_allow_html=True,
            )
        with col2:
            button_col1, button_col2, button_col3, button_col4 = st.columns(4)
            # 그룹생성 버튼
            with button_col1:
                if st.button(localization.get_text("create_group_button"), use_container_width=True):
                    self.group_creation_page()
            # 그룹차단 버튼
            with button_col2:
                if st.button(localization.get_text("blocked_list_button"), use_container_width=True):  # 여기에 추가
                    st.session_state["current_page"] = "GroupBlockList"
                    st.rerun()
            # 뒤로가기 버튼
            with button_col3:
                if st.button(localization.get_text("back_button"), use_container_width=True):
                    self.page.go_back()
            # 그룹검색 버튼
            with button_col4:
                if st.button(localization.get_text("search_group_button"), use_container_width=True):
                    self.search_groups_page()

        # 유저의 그룹을 가져온다
        group_manager = GroupManager(self.user_id)
        groups = group_manager.get_all_groups()

        # 그룹이 없을때
        if not groups:
            st.error(localization.get_text("no_maded_groups"))

        st.markdown(
            """
            <style>
            /* 그룹 박스 중앙 배치 */
            .group-box {
                border: 2px solid #555555;  /* 어두운 회색 테두리 */
                padding: 20px;
                border-radius: 10px;
                background-color: #333333;  /* 어두운 회색 배경 */
                margin: 15px auto;  /* 중앙 정렬을 위한 auto 설정 */
                color: white;  /* 텍스트를 하얀색으로 설정 */
                width: 80%;  /* 박스 크기 설정 */
                text-align: center; /* 텍스트를 중앙 정렬 */
            }
            .group-box h2 {
                margin-bottom: 10px;
            }
            .group-box p {
                margin: 5px 0;
            }

            /* "열기" 버튼 스타일 */
            .open-button {
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                cursor: pointer;
                width: 100%; /* 버튼을 가로로 길게 만들기 */
            }

            .open-button:hover {
                background-color: #45a049;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        for group in groups:
            members = group_manager.get_group_member_count(group.group_id)
            category_name = self.category_manager.category_id_to_name(group.category)
            st.markdown(
                f"""
                        <div class="group-box">
                            <h2>{group.group_name}</h2>
                            <p><strong>{localization.get_text("category")}:</strong> {category_name if category_name else localization.get_text("not_set")}</p>
                            <p><strong>{localization.get_text("status")}:</strong> {group.status}</p>
                            <p><strong>{localization.get_text("meeting_date")}:</strong> {group.meeting_date if group.meeting_date else localization.get_text("not_set")}</p>
                            <p><strong>{localization.get_text("meeting_time")}:</strong> {group.meeting_time if group.meeting_time else localization.get_text("not_set")}</p>
                            <p><strong>{localization.get_text("members_count")}:</strong> {members if members else localization.get_text("no_members")}</p>
                        </div>
                        """,
                unsafe_allow_html=True
            )

            st.markdown("---")
            # 그룹을 클릭하면 그룹id를 세션에 저장한다
            if st.button(localization.get_text("detail_button"), key=f"open_group_{group.group_id}",
                         use_container_width=True):
                st.session_state["group_id"] = group.group_id  # 그룹 ID를 세션에 저장
                self.page.change_page('Detail group')  # 세부 정보 페이지 호출

            # 그룹들 사이에 구분선
            st.markdown("---")

    def group_block_list_page(self):
        st.title(localization.get_text("group_block_list_title"))

        # 로그인 확인
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error(localization.get_text("login_required_error"))
            return

        block_dao = GroupBlockDAO(user_id)  # GroupBlockDAO 인스턴스 생성
        blocked_groups = block_dao.get_blocked_groups()  # 차단된 그룹 ID 목록 가져오기
        # 차단된 그룹이 있으면 정보를 반환함
        if not blocked_groups:
            st.warning(localization.get_text("no_blocked_groups"))
        else:
            for group_id in blocked_groups:
                st.markdown(f"**{localization.get_text('blocked_group_id')}:** {group_id}")
                if st.button(f"{localization.get_text('unblock_button')} (ID: {group_id})",
                             key=f"unblock_group_{group_id}", use_container_width=True):
                    if block_dao.unblock_group(group_id):
                        st.success(f"{localization.get_text('unblock_success')} {group_id}")
                    else:
                        st.error(localization.get_text("unblock_error"))
        if st.button(localization.get_text("back_button"), use_container_width=True):
            self.page.go_back()

    # 멤버 박스 출력 함수 (그룹장은 왕관 아이콘만 표시하고, 다른 멤버는 번호만 표시)
    def display_member_box(self, member_name, is_admin, member_number):
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        # 그룹장일 경우 왕관 아이콘만 표시하고, 일반 멤버는 번호만 표시
        member_display = f"{'👑 ' if is_admin else ''}{member_name}"
        member_icon = number_emojis[member_number - 1] if not is_admin else ""  # 그룹장에게는 번호 표시 안함

        st.markdown(
            f"""
            <div class="member-box">
                <span><span class="member-icon">{member_icon}</span><strong>{member_display}</strong></span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 그룹 세부 정보 페이지
    def detail_group(self):
        col1, col2 = st.columns([6, 2])  # 비율 6 : 2
        with col1:
            st.title(localization.get_text("group_detail_title"))  # 제목을 왼쪽에 배치
        with col2:
            if st.button(localization.get_text("back_button"), use_container_width=True):
                self.page.go_back()  # 뒤로가기 로직 호출

        # 그룹 ID 가져오기 (열기 버튼 클릭 시 해당 그룹 ID가 넘어옴)
        group_id = st.session_state.get("group_id")
        if not group_id:
            st.error(localization.get_text("no_group_error"))
            return

        group_info = self.group_manager.get_group_info(group_id)
        members = self.group_manager.get_group_member_count(group_id)
        user_id = st.session_state.get("user_id")
        if not group_info:
            st.error(localization.get_text("group_info_not_found"))
            return

        group_name, modify_date, meeting_date, meeting_time = group_info[1], group_info[3], group_info[4], group_info[5]

        # Display group information
        st.markdown(f"### {group_name}")
        st.markdown(f"**{localization.get_text('current_members')}:** {members} / 10")
        st.markdown(f"**{localization.get_text('last_modified')}:** {modify_date}")
        st.markdown(
            f"**{localization.get_text('meeting_date')}:** {meeting_date if meeting_date else localization.get_text('not_set')}")
        st.markdown(
            f"**{localization.get_text('meeting_time')}:** {meeting_time if meeting_time else localization.get_text('not_set')}")

        members = self.group_manager.get_group_members(group_id)

        # 그룹원 표시
        if members:
            st.write(f"**{localization.get_text('group_members')}:**")
            for idx, (member_name, role) in enumerate(members, start=1):
                is_admin = role == 'admin'  # 그룹장이면 True
                self.display_member_box(member_name, is_admin, idx)
        else:
            st.warning(localization.get_text("no_members_in_group"))

        # GroupBlockDAO 초기화
        if "block_dao" not in st.session_state:
            st.session_state["block_dao"] = GroupBlockDAO(user_id)  # zip.db를 기본값으로 사용
        block_dao = st.session_state["block_dao"]

        # 그룹 차단/해제 기능
        if st.button(localization.get_text("block_group"), key=f"block_group_{group_id}", use_container_width=True):
            success = block_dao.block_group(group_id)
            if success:
                st.success(localization.get_text("group_blocked_success"))
            else:
                st.error(localization.get_text("group_blocked_error"))

        if st.button(localization.get_text("unblock_group"), key=f"unblock_group_{group_id}", use_container_width=True):
            success = block_dao.unblock_group(st.session_state.get("user_id"), group_id)
            if success:
                st.success(localization.get_text("group_unblocked_success"))
            else:
                st.error(localization.get_text("group_unblocked_error"))

        if st.button(localization.get_text("invite_to_group"), key=f"invite_group_{group_id}",
                     use_container_width=True):
            self.group_manager.join_group(group_name)
            # 입력 필드 상태를 세션 상태에 저장해서 유지
            if 'invitee_id' not in st.session_state:
                st.session_state['invitee_id'] = ''  # 초기 값 설정

            with st.form(key=f"invite_form_{group_id}"):
                invitee_id = st.text_input("초대할 사용자 ID를 입력하세요",
                                           key=f"invitee_id_{group_id}")  # value는 자동으로 session_state 사용
                submit_button = st.form_submit_button("초대 보내기")
                if submit_button:
                    if invitee_id:  # st.session_state를 직접 수정하지 않음, 위젯 자체에 저장된 값 사용
                        result = self.group_manager.invite_user_to_group(group_id, invitee_id)
                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
                    else:
                        st.warning("사용자 ID를 입력하세요.")

    def group_block_list_page(self):
        st.title(localization.get_text("group_block_list_title"))

        # 로그인 확인
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.error(localization.get_text("login_required"))
            return

        block_dao = GroupBlockDAO(user_id)  # GroupBlockDAO 인스턴스 생성
        blocked_groups = block_dao.get_blocked_groups()  # 차단된 그룹 ID 목록 가져오기

        if not blocked_groups:
            st.warning(localization.get_text("no_blocked_groups"))
        else:
            for group_id in blocked_groups:
                st.markdown(f"**{localization.get_text('blocked_group_id')}:** {group_id}")
                if st.button(f"{localization.get_text('unblock')} ({group_id})", key=f"unblock_group_{group_id}",
                             use_container_width=True):
                    if block_dao.unblock_group(group_id):
                        st.success(f"{localization.get_text('group_unblocked_success')} ({group_id})")
                    else:
                        st.error(localization.get_text("group_unblock_error"))
        if st.button(localization.get_text("back_button"), use_container_width=True):
            self.page.go_back()

    @st.dialog(localization.get_text("create_group_dialog_title"))
    def group_creation_page(self):

        # 이제 인스턴스를 통해 group_creation_page 메서드를 호출합니다.
        st.header(localization.get_text("create_group_header"))

        # 그룹 이름 입력
        group_name = st.text_input(localization.get_text("group_name_label"),
                                   placeholder=localization.get_text("group_name_placeholder"), key="group_name_input")
        max_members = st.number_input(localization.get_text("max_members_label"), min_value=2, max_value=10, step=1,
                                      value=10, key="max_members_input")

        meeting_date = st.date_input(localization.get_text("select_meeting_date_label"), key="meeting_date_input")
        meeting_time = st.time_input(localization.get_text("select_meeting_time_label"), key="meeting_time_input")

        # 카테고리 선택

        categories = self.category_manager.category_selector()

        # 장소 검색 필드와 지도
        location_search = LocationSearch()
        location_search.display_location_on_map()

        group_manager = GroupManager(self.user_id)
        # 그룹 생성 버튼
        if st.button(localization.get_text("create_group_button"), key="create_group_button"):
            group_id = location_search.add_group(group_name, self.user_id, categories, meeting_date, meeting_time)
            if group_id:
                group_manager.add_group_member(group_id)
                st.rerun()

    @st.dialog(localization.get_text("update_group_dialog_title"))
    def group_update_page(self):
        # 그룹 ID 가져오기 (세션에 저장된 그룹 ID)
        group_id = st.session_state.get("group_id")
        if not group_id:
            st.error(localization.get_text("group_id_not_found_error"))
            return

        group_info = self.group_manager.get_group_info(group_id)
        # 그룹 수정 폼 바로 표시
        st.markdown(f"**'{group_info[1]}' {localization.get_text('update_group_header')}**")

        group_name = st.text_input(localization.get_text("group_name_label"), value=group_info[1])
        # 카테고리 선택
        category_manager = CategoryManager()
        categories = category_manager.category_selector()

        # 약속 날짜와 시간 추가
        if group_info[4] is not None:
            meeting_date = st.date_input(localization.get_text("meeting_date_label"), value=group_info[4])
        else:
            meeting_date = st.date_input(localization.get_text("meeting_date_label"),
                                         value=datetime.today().date())  # 기본값: 오늘 날짜

        if group_info[5] is not None:
            meeting_time = st.time_input(localization.get_text("meeting_time_label"), value=group_info[5])
        else:
            meeting_time = st.time_input(localization.get_text("meeting_time_label"),
                                         value=datetime.now().time())  # 기본값: 현재 시간

        status_choices = [
            localization.get_text("status_in_progress"),
            localization.get_text("status_completed"),
            localization.get_text("status_canceled")
        ]
        group_status = group_info[2]

        # group_status 값이 유효하지 않을 경우 기본값 설정
        if group_status not in status_choices:
            group_status = localization.get_text("status_in_progress")  # 기본값

        # selectbox로 상태 선택
        selected_status = st.selectbox(localization.get_text("group_status_label"), options=status_choices,
                                       index=status_choices.index(group_status))
        # 그룹 수정 버튼
        if st.button(localization.get_text("update_group_button"), use_container_width=True):
            self.group_manager.update_group(group_id, group_name, categories, selected_status, meeting_date,
                                            meeting_time)

        if st.button(localization.get_text("back_button"), use_container_width=True):
            self.page.go_back()

    @st.dialog(localization.get_text("search_group_dialog_title"))
    def search_groups_page(self):
        st.header(localization.get_text("search_group_header"))
        search_group = GroupSearch()
        # 검색 기준 선택
        search_criteria = st.selectbox(
            localization.get_text("search_criteria_label"),
            [
                localization.get_text("search_by_name"),
                localization.get_text("search_by_date"),
                localization.get_text("search_by_category")
            ],
            index=0
        )
        user_input = None
        groups = []

        # 그룹 검색 처리
        if search_criteria == localization.get_text("search_by_name"):
            user_input = st.text_input(localization.get_text("group_name_prompt"))
        elif search_criteria == localization.get_text("search_by_date"):
            user_input = st.date_input(localization.get_text("meeting_date_prompt"))
        elif search_criteria == localization.get_text("search_by_category"):
            user_input = self.category_manager.category_selector()

        # 검색 버튼
        with st.expander(localization.get_text("search_button_label")):
            # 검색 실행
            if user_input:
                groups = search_group.search_groups(user_input, search_criteria)

            # 결과 표시
            if not groups:
                st.warning(localization.get_text("no_search_results"))
            else:
                for group_name, group_creator, meeting_date, meeting_time, category, location_name, current_members in groups:
                    st.markdown(f"**{localization.get_text('group_name')}:** {group_name}")
                    st.markdown(f"**{localization.get_text('group_leader')}:** {group_creator}")
                    st.markdown(f"**{localization.get_text('current_members')}:** {current_members}")
                    st.markdown(f"**{localization.get_text('meeting_date')}:** {meeting_date}")
                    st.markdown(f"**{localization.get_text('meeting_time')}:** {meeting_time}")
                    st.markdown(f"**{localization.get_text('category')}:** {category}")
                    st.markdown(f"**{localization.get_text('location')}:** {location_name}")
                    if st.button(f"{localization.get_text('join_group')} ({group_name})", key=f"join_{group_name}",
                                 use_container_width=True):
                        self.group_manager.join_group(group_name)
                st.markdown("---")  # 구분선


class FriendPage:
    def __init__(self, page: Page):
        self.user_id = st.session_state.get("user_id")
        self.page = page
        self.friend_manager = FriendManager(self.user_id)
        self.friend_request = FriendRequest(self.user_id)  



    def show_friend_list(self):
        session = SessionLocal()
        try:
            friends = session.query(Friend).filter(Friend.user_id == self.user_id).all()
            if friends:
                for friend in friends:
                    profile_picture = (
                        session.query(User.profile_picture_path)
                        .filter(User.user_id == friend.friend_user_id)
                        .scalar()
                    )
                    if not profile_picture or not os.path.exists(profile_picture):
                        profile_picture = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
                        col1, col2, col3 = st.columns([1, 6, 2])  # 사진 1칸, 텍스트 6칸, 버튼 2칸
                    with col1:
                        st.image(profile_picture, width=50)  # 작은 크기로 사진 표시
                    with col2:
                        st.write(f"{friend.friend_user_id}")  # 친구 ID 표시
                    with col3:
                    # '포스팅 보기' 버튼
                        if st.button(f"포스팅 보기 ({friend.friend_user_id})", key=f"view_posts_{friend.friend_user_id}"):
                        # 상대방 포스팅 보기 페이지로 이동
                            st.session_state['current_friend_id'] = friend.friend_user_id
                            st.session_state['current_page'] = 'FriendPosts'
                            st.rerun()
            else:
                st.write("친구가 없습니다.")
        finally:
            session.close()
    
    def friend_posts_page(self):
    # 현재 사용자의 친구 포스팅 가져오기
        posts = self.get_friend_posts()

        if posts:
            st.title("친구들의 포스팅")
            for post in posts:
            # 포스팅 제목과 내용 출력
                st.subheader(post.p_title)
                st.write(post.p_content)

            # 이미지가 있는 경우 출력
                if post.p_image_path and os.path.exists(post.p_image_path):
                    st.image(post.p_image_path, width=200)
                else:
                    st.write("이미지가 없습니다.")
        else:
            st.warning("친구들의 포스팅이 없습니다.")

    
    def get_friend_posts(self):
        session = SessionLocal()
        try:
        # 친구들의 포스팅 가져오기
            friend_posts = (
                session.query(Posting)
                .join(Friend, Friend.friend_user_id == Posting.p_user)
                .filter(Friend.user_id == self.user_id)
                .all()
            )
            return friend_posts
        except Exception as e:
            st.error(f"오류 발생: {e}")
            return []
        finally:
            session.close()

    
    

    def show_friend_requests_page(self):
        st.title("친구 요청 관리")
        st.subheader("내가 보낸 친구 요청")
        sent_requests = self.friend_request.get_my_sent_requests()
        for req in sent_requests:
            st.write(f"- {req}")

        st.subheader("다른 사람이 보낸 친구 요청")
        received_requests = self.friend_request.get_received_requests()
        for req in received_requests:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"- {req}")
            with col2:
                if st.button(f"수락 ({req})"):
                    self.friend_request.accept_friend_request(req)
                if st.button(f"거절 ({req})"):
                    self.friend_request.reject_friend_request(req)

        if st.button("뒤로 가기"):
            st.session_state["current_page"] = "after_login"
            st.rerun()
    
    
    
    def friend_posts_page(self):
    # 현재 사용자의 친구 포스팅 가져오기
        posts = self.get_friend_posts()

        if posts:
            st.title("친구들의 포스팅")
            for post in posts:
            # 포스팅 제목과 내용 출력
                st.subheader(post.p_title)
                st.write(post.p_content)

            # 이미지가 있는 경우 출력
                if post.p_image_path and os.path.exists(post.p_image_path):
                    st.image(post.p_image_path, width=200)
                else:
                    st.write("이미지가 없습니다.")
        else:
            st.warning("친구들의 포스팅이 없습니다.")

    @st.dialog("친구 추가 창")
    def add_friend_page(self):

        # 상호작용할 ID 입력창
        target_id = st.text_input(localization.get_text("friend_request_input_label"), key="friend_action_input")

        if st.button(localization.get_text("friend_request_button"), use_container_width=True):
            if target_id:
                # 친구 추가 함수 호출 (user_id와 target_id)
                self.friend_request.add_friend(target_id)
            else:
                st.warning(localization.get_text("friend_request_warning"))

    @st.dialog(localization.get_text("unblock_friend_dialog_title"))
    def unblock_friend_page(self):
        # 상호작용할 ID 입력창
        target_id = st.text_input(localization.get_text("unblock_friend_input_label"), key="friend_action_input")

        if st.button(localization.get_text("unblock_friend_button"), use_container_width=True):
            if target_id:
                # 친구 차단 해제 함수 호출 (user_id와 target_id)
                self.friend_manager.unblock_friend(target_id)
            else:
                st.warning(localization.get_text("unblock_friend_warning"))

        st.title(localization.get_text("blocked_list_title"))
        self.show_blocked_list_page()

    def show_blocked_list_page(self):
        blocked_users = self.friend_manager.show_blocked_list()  # 차단된 유저 목록 가져오기
        if blocked_users:
            st.subheader(localization.get_text("blocked_users_subheader"))
            for user in blocked_users:
                st.write(f"- {user['blocked_user_id']}")
        else:
            st.write(localization.get_text("no_blocked_users"))

    def friend_posts_page(self):
        # 현재 선택된 친구 ID
        friend_id = st.session_state.get('current_friend_id')
        if not friend_id:
            st.error(localization.get_text("no_friend_id_error"))
            return

        # 세션 시작
        session = SessionLocal()
        try:
            # 친구의 포스팅 가져오기
            posts = session.query(Posting).filter(Posting.p_user == friend_id).all()

            if posts:
                st.title(localization.get_text("friend_posts_title").format(friend_id=friend_id))
                for post in posts:
                    st.subheader(post.p_title)
                    st.write(post.p_content)

                    # 이미지 경로가 존재하고 실제로 파일이 있으면 이미지를 표시
                    if post.p_image_path and os.path.exists(post.p_image_path):
                        st.image(post.p_image_path, width=200)
                    else:
                        st.write(localization.get_text("no_image_message"))
            else:
                st.warning(localization.get_text("no_posts_warning"))
        except Exception as e:
            st.error(localization.get_text("db_error").format(error=e))
        finally:
            session.close()  # 세션 종료

    @st.dialog(localization.get_text("delete_friend_dialog_title"))
    def delete_friend(self):
        # 상호작용할 ID 입력창
        target_id = st.text_input(localization.get_text("delete_friend_input_label"), key="friend_action_input")

        if st.button(localization.get_text("delete_friend_button"), use_container_width=True):
            if target_id:
                # 친구 삭제 함수 호출 (user_id와 target_id)
                self.friend_manager.delete_friend(target_id)
            else:
                st.warning(localization.get_text("delete_friend_warning"))

    # 친구 상태 표시 함수
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

    @st.dialog(localization.get_text("block_friend_dialog_title"))
    def block_friend_page(self):
        # 상호작용할 ID 입력창
        target_id = st.text_input(localization.get_text("block_friend_input_label"), key="friend_action_input")

        if st.button(localization.get_text("block_friend_button"), use_container_width=True):
            if target_id:
                # 친구 차단 함수 호출 (user_id와 target_id)
                self.friend_manager.block_friend(target_id)
            else:
                st.warning(localization.get_text("block_friend_warning"))

    def FriendList_page(self):
        col1, col2 = st.columns([4, 2])
        with col1:
            st.title(localization.get_text("friend_list_title"))  # 제목을 왼쪽에 배치
        with col2:
            if st.button(localization.get_text("back_button"), use_container_width=True, key='friendlist_key'):
                self.page.go_back()
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
        with col1:
            if st.button(localization.get_text("send_friend_request_button"), key="add_friend_button",
                         use_container_width=True):
                self.add_friend_page()
        with col2:
            if st.button(localization.get_text("block_friend_button"), key="block_friend_button",
                         use_container_width=True):
                self.block_friend_page()
        with col3:
            if st.button(localization.get_text("unblock_friend_button"), key="unblock_friend_button",
                         use_container_width=True):
                self.unblock_friend_page()
        with col4:
            if st.button(localization.get_text("delete_friend_button"), key="delete_friend_button",
                         use_container_width=True):
                self.delete_friend()
        with col5:
            if st.button(localization.get_text("friend_requests_button"), key="friend_requests_button",
                         use_container_width=True):
                self.request_friends_page()
    # 친구 리스트 출력
        
        self.show_friend_list()  # 친구 목록 출력 함수 호출

    @st.dialog(localization.get_text("friend_requests_title"))
    def request_friends_page(self):
        st.title(localization.get_text("friend_requests_title"))
        self.show_friend_requests_page()
        

# -------------------------------------디비-----------------------------------------------------------------------------

class User(Base):
    __tablename__ = 'user'
    user_seq = Column(Integer, primary_key=True, autoincrement=True)  # 고유 시퀀스
    user_id = Column(String, unique=True, nullable=False)  # 사용자 ID
    user_password = Column(String, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    user_is_online = Column(Boolean, default=False)
    profile_picture_path = Column(String, nullable=True)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_password': self.user_password,
            'user_email': self.user_email,
            'user_seq': self.user_seq,
            'user_is_online': self.user_is_online,
            'profile_picture_path': self.profile_picture_path
        }


class Friend(Base):
    __tablename__ = 'friend'
    friend_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    friend_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)


class Group(Base):
    __tablename__ = 'group'
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String, unique=True, nullable=False)
    group_creator = Column(String, ForeignKey('user.user_id'), nullable=False)
    category = Column(Integer, nullable=True)
    date = Column(DateTime, default=func.now())
    location = Column(Integer, nullable=True)
    meeting_date = Column(Date, server_default=func.current_date())  # Default: CURRENT_DATE
    meeting_time = Column(Time, server_default=func.current_time())  # Default: CURRENT_TIME
    status = Column(String, default='진행 중')
    update_date = Column(DateTime, default=func.now(), onupdate=func.now())
    modify_date = Column(DateTime, default=func.now(), onupdate=func.now())


class Block(Base):
    __tablename__ = 'block'
    block_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    blocked_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)


# myFriendrequest 테이블 (내가 보낸 친구 신청 목록)
class MyFriendRequest(Base):
    __tablename__ = 'myFriendrequest'
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    requested_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)


# otherRequest 테이블 (다른 사람이 보낸 친구 신청 목록)
class OtherRequest(Base):
    __tablename__ = 'otherRequest'
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    requester_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)


class GroupBlock(Base):
    __tablename__ = 'group_block'

    block_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    blocked_group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)


class Like(Base):
    __tablename__ = 'like'

    like_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posting.p_id'), nullable=False)


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
    joined_at = Column(DateTime, default=func.now())


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
    p_user = Column(String, ForeignKey('user.user_id'), nullable=False)
    p_title = Column(String, nullable=False)
    p_content = Column(Text, nullable=False)
    p_image_path = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    p_location = Column(Integer, ForeignKey('locations.location_id'), nullable=True)
    p_category = Column(Integer, ForeignKey('food_categories.category_id'), nullable=True)
    total_like_num = Column(Integer, default=0)
    file = Column(Text, nullable=True)  # Adjust as needed
    upload_date = Column(DateTime, default=func.now())
    modify_date = Column(DateTime, default=func.now(), onupdate=func.now())


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    user = Column(String, ForeignKey('user.user_id'), nullable=False)
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
        default_categories = ["한식", "중식", "양식", "일식", "디저트", "분식", "패스트푸드"]
        for category in default_categories:
            if not session.query(FoodCategory).filter_by(category=category).first():
                session.add(FoodCategory(category=category))

        session.commit()

    except Exception as e:
        session.rollback()  # 예외 발생 시 롤백
        print(f"Error initializing database: {e}")

    finally:
        session.close()  # 세션 닫기


# ---------------------------------------------------------------로그인 ----------------------------
class UserVO:
    def __init__(self, user_id: str, user_password: str, user_email: str, user_seq: int = None,
                 user_is_online: bool = False,
                 user_profile_picture: str = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"):
        self.user_id = user_id
        self.user_password = user_password
        self.user_email = user_email
        self.user_seq = user_seq
        self.user_is_online = user_is_online
        self.user_profile_picture = user_profile_picture

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get('user_id', ''),
            user_password=data.get('user_password', ''),
            user_email=data.get('user_email', ''),
            user_seq=data.get('user_seq', None),
            user_is_online=data.get('user_is_online', False),
            user_profile_picture=data.get('user_profile_picture',
                                          "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png")
        )


class UserManager:
    def __init__(self, smtp_email, smtp_password):
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password

    def is_email_registered(self, email):
        # 이메일이 등록되어 있는지 확인하고 user_id 반환
        user = session.query(User).filter_by(user_email=email).first()
        if user:
            return user.user_id  # user_id를 반환
        return None

    def generate_token(self, length=16):
        # 랜덤 토큰 생성
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    def send_recovery_email(self, email):
        token = self.generate_token()
        subject = localization.get_text("password_recovery_subject")
        body = (
            localization.get_text("password_recovery_body").format(token=token)
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
            print(localization.get_text("email_sent_success").format(email=email))
            # 보낸 토큰을 session_state에 저장
            st.session_state['recovery_token'] = token
            st.session_state['token_sent_time'] = datetime.utcnow()
        except smtplib.SMTPException as e:
            print(localization.get_text("email_failed_smtp").format(error=e))
        except Exception as e:
            print(localization.get_text("email_failed_generic").format(error=e))

    def save_recovery_token(self, email):
        # 복구 토큰을 데이터베이스에 저장
        token = self.generate_token()
        recovery = PasswordRecovery(user_email=email, token=token, created_at=datetime.utcnow())
        session.add(recovery)
        session.commit()

    def verify_token(self, email, token):
        # 세션에서 저장된 토큰과 비교, 토큰의 유효성 확인
        stored_token = st.session_state.get('recovery_token')
        sent_time = st.session_state.get('token_sent_time')

        # Check if the token exists and if it is not expired (valid for 1 hour)
        if stored_token == token and sent_time and (datetime.utcnow() - sent_time) < timedelta(hours=1):
            return True
        return False

    def reset_password(self, email, new_password):
        # 비밀번호 길이 제약 (8자 이상)
        if len(new_password) < 8:
            st.error(localization.get_text("password_length_error"))  # 길이가 8자 미만일 때 출력할 에러 메시지
            return

        # 비밀번호 해싱
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        # 사용자 찾기
        user = session.query(User).filter_by(user_email=email).first()

        if user:
            # 비밀번호 업데이트
            user.user_password = hashed_password
            session.commit()
            st.success(localization.get_text("password_reset_success"))  # 성공 메시지
        else:
            st.warning(localization.get_text("email_not_found"))  # 이메일이 존재하지 않으면 경고 메시지

        session.close()

    def recover_password(self, email, new_password, token):

        if not self.verify_token(email, token):
            print(localization.get_text("invalid_token"))
            return
        self.reset_password(email, new_password)
        print(localization.get_text("password_reset_success"))


# DAO 클래스
class UserDAO:

    def check_user_id_exists(self, user_id):
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            return UserVO.from_dict(user.to_dict()) if user else None
        except Exception as e:
            st.error(localization.get_text("db_error").format(error=e))
            return None

    def insert_user(self, user_vo: UserVO):

        # UserVO를 상속받아 정보를 저장함
        hashed_password = bcrypt.hashpw(user_vo.user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(
            user_id=user_vo.user_id,
            user_password=hashed_password,
            user_email=user_vo.user_email
        )
        try:
            session.add(new_user)
            session.commit()

        except Exception as e:
            session.rollback()
            st.error(localization.get_text("db_error").format(error=e))

    def check_password(self, hashed_password, plain_password):
        # hashed_password가 문자열이라면 bytes로 변환
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

    def get_user_vo(self, user_id):
        user = session.query(User).filter(User.user_id == user_id).first()
        session.close()

        if user:
            return UserVO(
                user_id=user.user_id,
                user_password=user.user_password,
                user_email=user.user_email,
                user_seq=user.user_seq,
                user_is_online=user.user_is_online,
                user_profile_picture=user.profile_picture_path
            )
        return None

    def update_user_field(self, user_id, field_name, field_value):

        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            setattr(user, field_name, field_value)
            session.commit()
            return True

    def update_user_password(self, user_id, new_password):
        try:
            # 새로운 비밀번호를 해시 처리
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # 사용자 조회
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                # 비밀번호 업데이트
                user.user_password = hashed_password
                session.commit()
                return True
            else:
                st.warning(localization.get_text("user_not_found").format(user_id=user_id))
                return False
        except Exception as e:
            session.rollback()
            st.error(localization.get_text("db_error").format(error=e))
            return False


# 회원가입 클래스
class SignUp:
    def __init__(self, user_vo: UserVO):
        self.user_vo = user_vo

    def sign_up_event(self):
        dao = UserDAO()  # UserDAO 인스턴스 생성
        if not self.check_length():
            return False
        if not self.check_user():
            return False
        dao.insert_user(self.user_vo)  # UserVO를 DAO에 전달
        return True

    def check_length(self):
        if len(self.user_vo.user_password) < 8:
            st.error(localization.get_text("password_length_error"))
            return False
        return True

    def check_user(self):
        dao = UserDAO()
        if dao.check_user_id_exists(self.user_vo.user_id):
            st.error(localization.get_text("user_id_exists_error"))
            return False
        return True


# 로그인 처리 클래스
class SignIn:
    def __init__(self, user_vo: UserVO):
        self.user_vo = user_vo
        self.page = Page()

    def sign_in_event(self):
        dao = UserDAO()
        user = dao.check_user_id_exists(self.user_vo.user_id)  # UserVO 반환
        if user:
            if dao.check_password(user.user_password, self.user_vo.user_password):
                st.session_state["user_id"] = self.user_vo.user_id
                dao.update_user_field(self.user_vo.user_id, "user_is_online", True)

                st.success(localization.get_text("login_success").format(user_id=self.user_vo.user_id))
                return True
            else:
                st.error(localization.get_text("password_incorrect_error"))
        else:
            st.error(localization.get_text("user_id_not_found_error"))
        return False


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

    def get_location_names(self):
        locations = session.query(Location).all()
        location_dict = {location.location_name: location.location_id for location in locations}
        return location_dict


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
                st.error(localization.get_text("no_search_results"))
                return None
        else:
            st.error(localization.get_text("api_request_error").format(status_code=response.status_code))
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
        col1, col2 = st.columns([8, 2])
        with col1:
            query = st.text_input(localization.get_text("search_location_input"), "영남대역", key='place')  # 기본값: 영남대역
        with col2:
            st.button(localization.get_text("search_button"), use_container_width=True)

        if query:
            # 카카오 API로 장소 검색
            results = self.search_location(query)

        if results:
            # 지역 정보 추출
            locations = [(place["place_name"], place["address_name"], float(place["y"]), float(place["x"]))
                         for place in results]

            # 지역 이름 선택
            selected_place = st.selectbox(localization.get_text("select_search_result"),
                                          [name for name, _, _, _ in locations])
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
                        st.write(f"{localization.get_text('place_name')}: {name}")
                        st.write(f"{localization.get_text('address')}: {address}")
                        # 여기서 데이터베이스에 저장
                        self.selected_location_id = self.save_or_get_location(
                            name, address, latitude, longitude)
            if location_data:
                df = pd.DataFrame(location_data)
                st.map(df[['latitude', 'longitude']])

    def get_selected_location_id(self):
        return self.selected_location_id

    def add_post(self, user_id, title, content, image_file, file_file, category):
        location_id = self.get_selected_location_id()  # Get the selected location_id
        post_manager = PostManager()
        image_path = post_manager.save_file(image_file) if image_file else ''
        file_path = post_manager.save_file(file_file) if file_file else ''
        upload_date = modify_date = datetime.now()

        # Create a new post object
        new_post = Posting(
            p_user=user_id,
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

    def add_group(self, group_name, user_id, category, meeting_date, meeting_time):
        location_id = self.get_selected_location_id()
        current_date = modify_date = datetime.now()

        if not group_name or not location_id or not meeting_date or not meeting_time:
            st.error(localization.get_text("missing_required_fields"))
            return

        # 그룹 이름 중복 확인
        existing_group = session.query(Group).filter(Group.group_name == group_name).first()
        if existing_group:
            st.error('그룹 이름이 이미 존재합니다')
            return

        # 그룹 모델 인스턴스 생성
        new_group = Group(
            group_name=group_name,
            group_creator=user_id,
            category=category,
            location=location_id,
            meeting_date=meeting_date,
            meeting_time=meeting_time,
            update_date=current_date,
            modify_date=current_date,
            status=localization.get_text("status_in_progress")
        )

        # 세션에 그룹 추가
        session.add(new_group)
        session.commit()
        session.refresh(new_group)  # 새로운 그룹 객체에 자동 생성된 group_id가 반영됨

        # 성공 메시지
        st.success(localization.get_text("group_creation_success").format(group_name=group_name))

        # 생성된 그룹 ID 반환
        return new_group.group_id  # 생성된 그룹의 ID를 반환


class PostManager:
    def __init__(self, upload_folder='uploaded_files'):
        self.upload_folder = upload_folder
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        self.locations_df = None
        if "posts" not in st.session_state:
            st.session_state.posts = []
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

    def get_my_posts(self, user_id):
        try:
            # 데이터베이스에서 user_id에 해당하는 사용자의 게시물 조회
            posts = session.query(Posting).filter(Posting.p_user == user_id).all()

            # 사용자가 작성한 게시물이 없을 경우 처리
            if not posts:
                st.warning(localization.get_text("no_posts_found").format(user_id=user_id))
                return []

            # 게시물 데이터를 리스트로 변환하여 반환
            post_list = []
            for post in posts:
                post_data = {
                    "post_id": post.post_id,
                    "title": post.p_title,
                    "content": post.p_content,
                    "image_path": post.p_image_path,
                    "file_path": post.file_path,
                    "category_id": post.p_category,
                    "location_id": post.p_location,
                    "upload_date": post.upload_date,
                    "modify_date": post.modify_date,
                }
                post_list.append(post_data)

            return post_list

        except Exception as e:
            st.error(localization.get_text("post_retrieval_error").format(error=e))
            return []
        finally:
            session.close()  # 세션 닫기

    def toggle_like(self, post_id, user_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()
        if post is None:
            st.error("Post not found.")
            return

        like = session.query(Like).filter_by(post_id=post_id, user_id=user_id).first()
        try:
            if like:
                # 이미 좋아요를 눌렀다면 취소
                session.delete(like)
                post.total_like_num -= 1
                st.warning(localization.get_text("like_removed"))
            else:
                # 좋아요 추가
                new_like = Like(post_id=post_id, user_id=user_id)
                session.add(new_like)
                post.total_like_num += 1
                st.success(localization.get_text("like_added"))
            session.commit()
        except Exception as e:
            session.rollback()
            st.error(f"An error occurred: {str(e)}")
        finally:
            st.rerun()

    def display_like_button(self, post_id, user_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()
        if post is None:
            st.error("Post not found.")
            return

        like = session.query(Like).filter_by(post_id=post_id, user_id=user_id).first()
        total_likes = post.total_like_num
        st.write(localization.get_text("total_likes").format(total_likes=total_likes))

        btn_label = localization.get_text("unlike_button") if like else localization.get_text("like_button")
        if st.button(btn_label, key=post_id, use_container_width=True, type='primary'):
            self.toggle_like(post_id, user_id)

    def create_location_name(self):
        # Check if the DataFrame is empty
        if self.locations_df is None or self.locations_df.empty:
            st.error(localization.get_text("no_locations_found"))
            return

        # Display place details
        for index, row in self.locations_df.iterrows():
            name = row['location_name']
            address = row['address_name']
            st.write(localization.get_text("location_name").format(name=name))
            st.write(localization.get_text("location_address").format(address=address))

    def display_map(self):
        if self.locations_df is None or self.locations_df.empty:
            st.error(localization.get_text("no_location_data"))
            return

        # Use the latitude and longitude columns to display the map
        st.map(self.locations_df[['latitude', 'longitude']], use_container_width=True)

    def edit_post(self, post_id):
        post = session.query(Posting).filter_by(p_id=post_id).first()

        if post:
            title = st.text_input(localization.get_text("edit_post_title_label"), value=post.p_title,
                                  key=f"post_title_{post.p_id}")
            content = st.text_area(localization.get_text("edit_post_content_label"), value=post.p_content,
                                   key=f"post_content_{post.p_id}")
            image_file = st.file_uploader(localization.get_text("edit_post_image_upload"), type=['jpg', 'png', 'jpeg'],
                                          key=f"image_upload_{post.p_id}")
            file_file = st.file_uploader(localization.get_text("edit_post_file_upload"),
                                         type=['pdf', 'docx', 'txt', 'png', 'jpg'], key=f"file_upload_{post.p_id}")

            selected_category_name = st.selectbox(
                localization.get_text("edit_post_category_label"),
                [category.category for category in self.category_manager.get_category_options()],
                key=f"category_selectbox_{post.p_id}"
            )
            categories = self.category_manager.get_category_options()
            category_dict = {category.category: category.category_id for category in categories}
            selected_category_id = category_dict[selected_category_name]

            if st.button(localization.get_text("edit_post_submit_button"), key=f"button_{post.p_id}",
                         use_container_width=True):
                self.update_post(post_id, title, content, image_file, file_file, selected_category_id)
                st.success(localization.get_text("edit_post_success_message"))
                st.run()

        else:
            st.error(localization.get_text("edit_post_not_found_error"))

    def fetch_location_data(self, post_id):
        location_data = session.query(
            Location.location_name,
            Location.address_name,
            Location.latitude,
            Location.longitude
        ).join(Posting, Posting.p_location == Location.location_id).filter(Posting.p_id == post_id).all()

        if location_data:
            self.locations_df = pd.DataFrame(location_data,
                                             columns=['location_name', 'address_name', 'latitude', 'longitude'])
        else:
            self.locations_df = pd.DataFrame(columns=['location_name', 'address_name', 'latitude', 'longitude'])

        return self.locations_df

    def display_posts(self, user_id):
        posts = session.query(Posting).filter_by(p_user=user_id).all()

        for post in posts:
            st.write(localization.get_text("post_id_and_title").format(post_id=post.p_id, title=post.p_title))
            st.write(localization.get_text("post_content").format(content=post.p_content))
            if post.p_image_path and os.path.exists(post.p_image_path):
                st.image(post.p_image_path, width=200)

            if st.button(f"삭제", key=f"delete_{post.p_id}", use_container_width=True):
                # 세션 상태에 게시물 정보 저장
                st.session_state["delete_post_id"] = post.p_id
                st.session_state["delete_post_title"] = post.p_title

                # 삭제 확인 대화 상자 표시
                self.show_delete_confirmation_dialog()
            # 게시물 수정 버튼
            with st.expander(localization.get_text("edit_post_expander")):
                self.edit_post(post.p_id)

            self.fetch_location_data(post.p_id)

            if self.locations_df is not None and not self.locations_df.empty:
                self.create_location_name()
                st.title(localization.get_text("location_map_title"))
                self.display_map()

            st.write(
                localization.get_text("post_dates").format(upload_date=post.upload_date, modify_date=post.modify_date))
            st.write("---")

    def display_post(self, post_id):
        # 특정 게시물 가져오기
        post = self.get_post_by_id(post_id)

        if post:
            # 게시물 정보 출력
            st.write(f"**creator ID**: {post['p_user']}")
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

    @st.dialog("게시물 삭제")
    def show_delete_confirmation_dialog(self):
        if "delete_post_id" in st.session_state:
            with st.container():
                st.markdown(f"정말로 게시물 '{st.session_state['delete_post_title']}'을 삭제하시겠습니까?")

                col1, col2 = st.columns(2)
                with col1:
                    # '예' 버튼
                    if st.button("예", key=f"confirm_delete_post_{st.session_state['delete_post_id']}",
                                 use_container_width=True, type="primary"):
                        post_id = st.session_state["delete_post_id"]

                        # 게시물 삭제 로직 실행
                        self.delete_post(post_id)
                        st.success(f"게시물 '{st.session_state['delete_post_title']}'가 삭제되었습니다.")

                        # 세션 상태 초기화
                        del st.session_state["delete_post_id"]
                        del st.session_state["delete_post_title"]

                        # 게시물 목록 새로고침
                        st.rerun()

                with col2:
                    # '아니오' 버튼
                    if st.button("아니오", key=f"cancel_delete_post_{st.session_state['delete_post_id']}",
                                 use_container_width=True, type="primary"):
                        st.info("게시물 삭제가 취소되었습니다.")

                        # 세션 상태 초기화
                        del st.session_state["delete_post_id"]
                        del st.session_state["delete_post_title"]

    def get_post_by_id(self, post_id):
        # Query the Posting table using SQLAlchemy's ORM query
        post = session.query(Posting).filter_by(p_id=post_id).first()

        # If the post exists, convert it to a dictionary, else return None
        if post:
            return {
                "p_id": post.p_id,
                "p_user": post.p_user,
                "p_title": post.p_title,
                "p_content": post.p_content,
                "p_image_path": post.p_image_path,
                "file_path": post.file_path,
                "p_location": post.p_location,
                "p_category": post.p_category,
                "file": post.file,
                "upload_date": post.upload_date,
                "modify_date": post.modify_date
            }
        else:
            return None

    def display_posts_on_home(self, user_id):
        # 정렬 방식 선택
        sort_by = st.selectbox(localization.get_text("sort_posts_label"),
                               [localization.get_text("sort_by_latest"), localization.get_text("sort_by_popularity")])
        # 정렬 기준 설정
        if sort_by == localization.get_text("sort_by_popularity"):
            posts = session.query(Posting).order_by(Posting.total_like_num.desc()).all()
        else:
            posts = session.query(Posting).order_by(Posting.upload_date.desc()).all()

        if not posts:
            st.write(localization.get_text("no_recommended_posts_message"))
            return

        # 포스트를 두 개씩 나열
        for i in range(0, len(posts), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(posts):
                    post = posts[i + j]  # 현재 포스트 데이터
                    with col:
                        st.subheader(post.p_title)

                        if user_id:
                            self.display_like_button(post.p_id, user_id)
                        self.fetch_location_data(post.p_id)

                        if post.p_image_path:
                            self.create_location_name()
                            st.image(post.p_image_path)

                        with st.expander(localization.get_text("view_more_expander")):
                            self.display_post(post.p_id)


# ----------------------------------------------------카테고리 -----------------------------
class CategoryManager:
    def get_category_options(self):
        return session.query(FoodCategory).all()

    def get_category_names(self):
        categories = self.get_category_options()
        category_dict = {category.category: category.category_id for category in categories}
        return category_dict

    def category_selector(self):
        categories = self.get_category_names()
        if categories:
            category = st.selectbox(
                localization.get_text("select_category_label"),
                options=list(categories.keys()),  # category names as options
                format_func=lambda x: x,  # Display the category name (the key of the dictionary)
                key="category_selectbox"
            )
            return categories[category]  # Return the category ID corresponding to the selected category
        else:
            st.error(localization.get_text("no_registered_categories_error"))

    def category_id_to_name(self, category_id):
        categories = self.get_category_options()
        for category in categories:
            if category.category_id == category_id:
                return category.category
        return None


# -------------------------------------------------테마----------------------------------------------


class ThemeManager:
    def __init__(self, user_id):
        self.th = st.session_state
        self.user_id = user_id

        if "themes" not in self.th:
            saved_theme = self.get_saved_theme(user_id)  # Load saved theme from DB or default to dark
            self.th.themes = {
                "current_theme": saved_theme,  # Load saved theme (light/dark) for the user
                "light": {
                    "theme.base": "dark",
                    "theme.backgroundColor": "black",
                    "theme.textColor": "white",
                    "button_face": localization.get_text("dark_mode_button_label")
                },
                "dark": {
                    "theme.base": "light",
                    "theme.backgroundColor": "white",
                    "theme.textColor": "#0a1464",
                    "button_face": localization.get_text("light_mode_button_label")
                }
            }
        else:
            # themes 딕셔너리에 'light'와 'dark'가 없으면 추가
            if "light" not in self.th.themes:
                self.th.themes["light"] = {
                    "theme.base": "light",
                    "theme.backgroundColor": "white",
                    "theme.textColor": "black",
                    "button_face": localization.get_text("dark_mode_button_label")
                }
            if "dark" not in self.th.themes:
                self.th.themes["dark"] = {
                    "theme.base": "dark",
                    "theme.backgroundColor": "black",
                    "theme.textColor": "white",
                    "button_face": localization.get_text("light_modee_button_label")
                }

    def get_saved_theme(self, user_id):
        setting = session.query(Settings).filter(Settings.user == user_id).first()
        session.close()

        # Return the theme if valid, otherwise default to 'dark'
        return setting.current_theme if setting and setting.current_theme in ["light", "dark"] else 'dark'

    def save_theme(self, user_id, theme):
        """Save the selected theme for a user."""
        setting = session.query(Settings).filter(Settings.user == user_id).first()

        if setting:
            setting.current_theme = theme  # Update existing theme
        else:
            # Create new entry for the user if no settings exist
            setting = Settings(user=user_id, current_theme=theme)
            session.add(setting)

        session.commit()
        session.close()

    def change_theme(self, user_id):
        previous_theme = self.get_saved_theme(user_id)
        new_theme = "light" if previous_theme == "dark" else "dark"

        # Ensure the new theme exists in the themes dictionary
        if new_theme not in self.th.themes:
            st.error(f"Theme '{new_theme}' not found in theme dictionary")
            return

        # Apply the new theme settings
        theme_dict = self.th.themes[new_theme]
        for key, value in theme_dict.items():
            if key.startswith("theme"):
                st._config.set_option(key, value)

        # Save the new theme for the user
        self.save_theme(user_id, new_theme)

    def render_button(self, user_id):
        current_theme = self.get_saved_theme(user_id)

        # 현재 테마에 따라 버튼 라벨을 동적으로 설정
        if current_theme == "dark":
            button_label = localization.get_text("dark_mode_button_label")  # 라이트 모드로 변경 버튼
        else:
            button_label = localization.get_text("light_mode_button_label")  # 다크 모드로 변경 버튼

        # 버튼을 렌더링하고 클릭 이벤트 처리
        if st.button(button_label, use_container_width=True, key='change_theme'):
            self.change_theme(user_id)
            st.rerun()

    def select_language(self, user_id):
        lang_options = ['ko', 'en', 'jp']  # 지원하는 언어 목록

        # 드롭다운을 왼쪽에 배치
        selected_lang = st.selectbox(
            localization.get_text("select_language"),  # "언어 선택" 문자열을 로컬라이제이션에서 가져옴
            lang_options,
            index=lang_options.index(st.session_state.current_language),  # 현재 언어에 맞게 기본값 설정
            key="language_select",
            help=localization.get_text("choose_language")  # 툴팁 문자열
        )

        if st.session_state.current_language != selected_lang:
            st.session_state.current_language = selected_lang  # 선택한 언어로 변경
            st.session_state.localization.lang = selected_lang  # Localization 객체의 언어도 변경
            st.rerun()  # 페이지를 다시 로드


# ----------------------------------------------------- 유저 프로필 ---------------------------------
class UserProfile:
    def __init__(self, upload_folder="profile_pictures"):
        self.upload_folder = upload_folder
        self.user_dao = UserDAO()
        # Default profile picture URL
        self.default_profile_picture = (
            "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        )

        # Attempt to create the directory
        os.makedirs(self.upload_folder, exist_ok=True)

    def save_file(self, uploaded_file):
        # 이미지 저장 후 경로 반환
        if uploaded_file is not None:
            file_path = os.path.join(self.upload_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return file_path
        return None

    def update_profile_picture(self, user_id, image_path):
        if image_path:
            success = self.user_dao.update_user_field(user_id, "profile_picture_path", image_path)
            return success, image_path
        return False, None

    def display_profile(self, user_id):
        user_vo = self.user_dao.get_user_vo(user_id)
        if user_vo:
            st.write(localization.get_text("user_email").format(email=user_vo.user_email))
            profile_picture = user_vo.user_profile_picture

            # 프로필 사진 경로가 없거나 파일이 존재하지 않으면 기본 이미지 사용
            if not profile_picture or not os.path.exists(profile_picture):
                profile_picture = self.default_profile_picture

            st.image(profile_picture, caption=user_id, width=300)
        else:
            st.error(localization.get_text("user_info_not_found"))

    def upload_new_profile_picture(self, user_id):
        st.button(localization.get_text("change_profile_picture"), use_container_width=True, key='change_profile')
        uploaded_file = st.file_uploader(localization.get_text("upload_new_profile_picture"),
                                         type=["jpg", "png", "jpeg"])

        if st.button(localization.get_text("upload_button"), key='upload', use_container_width=True):
            image_path = self.save_file(uploaded_file)
            if image_path:
                # 프로필 사진 업데이트
                self.update_profile_picture(user_id, image_path)
                st.success(localization.get_text("profile_picture_updated"))
            else:
                st.error(localization.get_text("file_save_failed"))


class SetView:
    def __init__(self, user_vo):
        self.user_vo = user_vo
        self.theme_manager = ThemeManager(user_vo.user_id)
        self.like_button = LikePost()
        self.user_profile = UserProfile()
        self.user_dao = UserDAO()

    def update_user_field(self, field_name, field_value):
        dao = UserDAO()
        if dao.update_user_field(self.user_vo.user_id, field_name, field_value):
            updated_user = dao.get_user_vo(self.user_vo.user_id)
            if updated_user:
                self.user_vo = updated_user
                st.session_state["user_vo"] = updated_user
                st.success(localization.get_text("field_updated").format(field=field_name))
            else:
                st.error(localization.get_text("user_info_fetch_failed"))
        else:
            st.error(localization.get_text("field_update_failed"))

    def render_user_profile(self):
        st.write(f"**{self.user_vo.user_id}**")
        st.write(localization.get_text("user_email").format(email=self.user_vo.user_email))

        profile_picture = self.user_vo.user_profile_picture or "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        st.image(profile_picture, width=100)

        with st.expander(localization.get_text("edit_my_info")):
            new_email = st.text_input(localization.get_text("new_email"), value=self.user_vo.user_email)
            if st.button(localization.get_text("change_email_button"), key='change_email', use_container_width=True):
                self.update_user_field("user_email", new_email)

            new_password = st.text_input(localization.get_text("new_password"), type='password')
            if st.button(localization.get_text("change_password_button"), key='change_password',
                         use_container_width=True):

                if len(new_password) >= 8:
                    self.user_dao.update_user_password(self.user_vo.user_id, new_password)
                    st.success(localization.get_text("password_change_success"))
                else:
                    st.warning(localization.get_text("password_minimum_length"))
            uploaded_file = st.file_uploader(localization.get_text("upload_new_profile_picture"),
                                             type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image_path = self.user_profile.save_file(uploaded_file)
                self.update_user_field("profile_picture_path", image_path)

                st.success(localization.get_text("profile_picture_changed"))
                st.rerun()

    def render_posts(self):
        with st.expander(localization.get_text("favorites"), icon='💗'):
            self.like_button.display_liked_posts()


# -----------------------------------------------------좋아요 목록 --------------------------------------------------

class LikePost:
    def __init__(self):
        if "posts" not in st.session_state:
            st.session_state.posts = []

    def fetch_liked_posts(self):

        try:
            # post_id를 기준으로 그룹화하여 중복되지 않도록 쿼리
            liked_posts = session.query(
                Posting.p_user,
                Posting.p_content,
                Posting.p_title,
                Posting.p_image_path,
                Posting.p_id
            ).join(Like, Like.post_id == Posting.p_id).filter(
                Like.like_id > 0
            ).group_by(Posting.p_id).all()  # post_id 기준으로 그룹화하여 중복 제거

            return liked_posts
        finally:
            # 세션 종료
            session.close()

    def display_liked_posts(self):
        liked_posts = self.fetch_liked_posts()
        # Display liked posts with the like button
        if liked_posts:
            for post in liked_posts:
                post_user, post_content, post_title, p_image, p_id = post
                st.write(f"**Creator ID**: {post_user}")
                st.write(f"Title: {post_title}, content : {post_content}")
                if p_image:
                    st.image(p_image, width=100)
                st.write('--------')


class Chatting:
    def __init__(self, group_id):
        self.group_id = group_id

    # 메세지를 저장하는 함수
    def save_message(self, sender_id, message_text):
        new_message = Message(
            group_id=self.group_id,
            sender_id=sender_id,
            message_text=message_text,
            sent_at=datetime.now()
        )
        session.add(new_message)
        session.commit()
        # 성공적으로 저장된 메세지에 대한 반환값
        return localization.get_text("message_saved").format(sender=sender_id)

    # 특정 그룹의 메세지를 불러오는 함수
    def load_messages(self):
        messages = session.query(Message).filter_by(group_id=self.group_id).all()
        return messages

    # 그룹 이름을 가져오는 함수
    def get_group_name(self, group_id):
        group = session.query(Group).filter_by(group_id=group_id).first()
        if group:
            return group.group_name
        else:
            return localization.get_text("group_not_found")

    @st.dialog(localization.get_text("chat"))
    def display_chat_interface(self):
        group_name = self.get_group_name(self.group_id)
        st.subheader(localization.get_text("chat_title").format(group=group_name))

        # 현재 사용자의 ID를 가져옴
        sender_id = st.session_state.get("user_id")
        if not sender_id:
            st.error(localization.get_text("login_required"))
            return

        # 그룹별 메세지 상태 초기화
        if f"messages_{self.group_id}" not in st.session_state:
            st.session_state[f"messages_{self.group_id}"] = self.load_messages()

        # 채팅 기록 표시
        st.markdown(localization.get_text("chat_history"))
        for msg in st.session_state[f"messages_{self.group_id}"]:
            st.write(f"**{msg.sender_id}** ({msg.sent_at}): {msg.message_text}")

        # 새로운 메세지 입력 필드 상태 초기화
        if f"new_message_{self.group_id}" not in st.session_state:
            st.session_state[f"new_message_{self.group_id}"] = ""

        # 새로운 메세지를 입력받는 필드
        new_message = st.text_input(
            localization.get_text("message_input"),
            value=st.session_state[f"new_message_{self.group_id}"],
            key=f"chat_input_{self.group_id}"
        )
        # 입력 상태를 유지
        st.session_state[f"new_message_{self.group_id}"] = new_message

        # 보내기 버튼 동작
        if st.button(localization.get_text("send_button"), key=f"send_button_{self.group_id}",
                     use_container_width=True):
            if new_message.strip():  # 메세지가 공백이 아니어야 함
                self.save_message(sender_id, new_message)
                st.session_state[f"new_message_{self.group_id}"] = ""  # 입력 필드 초기화
                st.session_state[f"messages_{self.group_id}"] = self.load_messages()  # 메세지 갱신
            else:
                st.warning(localization.get_text("message_required"))

        # 선택적으로 채팅 기록을 문자열로 반환
        chat_interface = ""
        for msg in st.session_state[f"messages_{self.group_id}"]:
            chat_interface += f"{msg.sent_at} - {msg.sender_id}: {msg.message_text}\n"

        return chat_interface


# -----------------------------------------------그룹관리 ----------------------------------------------------
class GroupManager:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_all_groups(self):
        groups = (session.query(Group).all())
        return groups

    def get_user_groups(self):
        groups = (session.query(Group).all())
        return groups

    # 그룹에 속해있는 멤버들의 아이디를 반환한다
    def get_group_members(self, group_id):
        # Query to get user_id, name, and role for the given group_id
        members = (
            session.query(User.user_id, GroupMember.role)  # Select user_name and role
            .join(GroupMember, User.user_id == GroupMember.user_id)  # Join User and GroupMember tables
            .filter(GroupMember.group_id == group_id)  # Filter by group_id
            .all()  # Fetch all results as a list of tuples
        )

        return members

    def invite_user_to_group(self, group_id, invitee_id):
        try:
            user_exists = session.query(User).filter(User.user_id == invitee_id).first()
            if not user_exists: return {"success": False, "message": "존재하지 않는 사용자입니다."}
            already_member = session.query(GroupMember).filter(GroupMember.group_id == group_id,
                                                               GroupMember.user_id == invitee_id).first()
            if already_member: return {"success": False, "message": "이미 그룹에 포함된 사용자입니다."}
            new_member = GroupMember(group_id=group_id, user_id=invitee_id, role="member", joined_at=datetime.now())
            session.add(new_member)
            session.commit()
            return {"success": True, "message": f"{invitee_id} 사용자가 그룹에 성공적으로 추가되었습니다."}
        except Exception as e:
            session.rollback()
            return {"success": False, "message": f"DB 오류:{e}"}
        finally:
            session.close()

    def get_user_groups(self):
        try:
            # 사용자가 속한 그룹을 조회 (GroupMember를 통해 User와 Group을 연결)
            user_groups = session.query(Group).join(GroupMember, Group.group_id == GroupMember.group_id) \
                .filter(GroupMember.user_id == self.user_id).all()
            return user_groups
        except Exception as e:
            session.rollback()  # 예외 발생 시 롤백
            st.error(localization.get_text("db_error").format(error=e))
            return []
        finally:
            session.close()

    def kick_member(self, group_id, user_id):
        try:
            group_member = session.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
            if group_member:
                session.delete(group_member)
                session.commit()
                return True
            else:
                st.warning("해당 사용자가 그룹에 없습니다.")
                return False
        except Exception as e:
            session.rollback()
            st.error(localization.get_text("db_error").format(error=e))
            return False
        # 그룹에 속해있는 멤버들의 아이디를 반환한다

    def get_group_members(self, group_id):
        # Query to get user_id, name, and role for the given group_id
        members = (
            session.query(User.user_id, GroupMember.role)  # Select user_name and role
            .join(GroupMember, User.user_id == GroupMember.user_id)  # Join User and GroupMember tables
            .filter(GroupMember.group_id == group_id)  # Filter by group_id
            .all()  # Fetch all results as a list of tuples
        )

        return members

    # 그룹 정보 반환
    def get_group_info(self, group_id):
        # Query to get the basic group information
        group_info = (
            session.query(
                Group.group_id,
                Group.group_name,
                Group.status,
                Group.modify_date,
                Group.meeting_date,
                Group.meeting_time
            )
            .filter(Group.group_id == group_id)  # Filter by group_id
            .first()  # Get the first result (similar to fetchone)
        )

        return group_info

        # 그룹에 속한 멤버 수를 반환

    # 그룹 멤버 수 반환
    def get_group_member_count(self, group_id):
        members = self.get_group_members(group_id)  # Use get_group_members to get the member list
        return len(members)

    # 그룹멤버 추가 함수
    def add_group_member(self, group_id, role="admin"):
        current_date = datetime.now()

        try:
            # 멤버 추가
            new_member = GroupMember(
                group_id=group_id,
                user_id=self.user_id,
                role=role,
                joined_at=current_date
            )
            session.add(new_member)
            session.commit()
            st.success(localization.get_text("group_member_added_success"))
        except Exception as e:
            session.rollback()
            st.error(localization.get_text("group_member_add_error").format(error=e))

    # 그룹의 상세정보를 반환함
    def show_group_details(self, group_id, group_name):
        st.subheader(localization.get_text("group_details").format(group_name=group_name))

        # 컨테이너로 세부 정보와 채팅 표시
        with st.container():
            self.display_chat_interface(group_name, group_id)

    def get_group_name(self, group_id):
        group = session.query(Group).filter_by(group_id=group_id).first()
        return group.group_name if group else localization.get_text("group_not_found")

    # 그룹의 creator인지 확인하는 함수
    def is_group_creator(self, group_id):
        group = session.query(Group).filter_by(group_id=group_id).first()
        return group and group.group_creator == self.user_id

    def is_group_member(self, group_id):
        try:
            # GroupMember 테이블에서 주어진 group_id와 user_id가 존재하는지 확인
            group_member = session.query(GroupMember).filter_by(group_id=group_id, user_id=self.user_id).first()

            # 만약 존재하면 그룹의 멤버로 확인
            return group_member is not None
        except Exception as e:
            session.rollback()  # 예외 발생 시 롤백
            return False
        finally:
            session.close()  # 세션 종료

    # 그룹 삭제
    def delete_group(self, group_id):
        try:
            # 그룹 삭제
            group = session.query(Group).filter_by(group_id=group_id).first()
            if group:
                session.delete(group)
                session.commit()
                st.success(localization.get_text("group_deleted_success"))
            else:
                st.error(localization.get_text("group_not_found"))
        except Exception as e:
            session.rollback()
            st.error(localization.get_text("group_delete_error").format(error=e))
        finally:
            session.close()  # 세션 종료
            st.rerun()

    def leave_group(self, group_id):
        try:
            # 그룹 탈퇴 확인
            group_member = session.query(GroupMember).filter_by(group_id=group_id, user_id=self.user_id).first()

            if not group_member:
                st.error(localization.get_text("not_in_group"))
                return

            # 그룹에서 사용자 제거
            session.delete(group_member)
            session.commit()

            st.success(localization.get_text("leave_group_success").format(group_id=group_id))
        except Exception as e:
            session.rollback()
            st.error(localization.get_text("leave_group_error").format(error=e))
        finally:
            session.close()  # 세션 종료

    def update_group(self, group_id, group_name, category, status, meeting_date, meeting_time):
        try:
            # 그룹 레코드를 조회
            group = session.query(Group).filter(Group.group_id == group_id).first()

            if not group:
                st.error(localization.get_text("group_not_found"))
                return

            # 그룹 이름 중복 확인 (다른 그룹과 중복 여부 확인)
            existing_group = session.query(Group).filter(
                Group.group_name == group_name,
                Group.group_id != group_id  # 현재 그룹 제외
            ).first()

            if existing_group:
                st.error('그룹 이름이 이미 존재합니다')
                return

            # 수정할 데이터 설정
            group.group_name = group_name
            group.category = category
            group.status = status
            group.meeting_date = meeting_date
            group.meeting_time = meeting_time
            group.modify_date = datetime.now()

            # 세션 커밋
            session.commit()
            st.success(localization.get_text("group_updated_success"))
        except Exception as e:
            st.error(localization.get_text("db_error").format(error=e))
            session.rollback()  # 오류 발생 시 롤백
        finally:
            session.close()  # 세션 종료

    def get_my_groups(self):
        groups = session.query(Group).filter_by(group_creator=self.user_id).all()
        return [
            {
                "group_id": group.group_id,
                "group_name": group.group_name,
                "category": group.category,
                "location": group.location,
                "status": group.status,
                "meeting_date": group.meeting_date,
                "meeting_time": group.meeting_time,
            }
            for group in groups
        ]

    def join_group(self, group_name):
        try:
            # 그룹 조회
            group = session.query(Group).filter(Group.group_name == group_name).first()
            if group:
                # 이미 멤버인지 확인
                existing_member = session.query(GroupMember).filter(
                    GroupMember.group_id == group.group_id, GroupMember.user_id == self.user_id).first()
                if existing_member:
                    st.warning(localization.get_text("already_member"))
                    return

                # 그룹 멤버 추가
                new_member = GroupMember(
                    group_id=group.group_id,
                    user_id=self.user_id,
                    role="member"
                )
                session.add(new_member)
                session.commit()
                st.success(localization.get_text("group_joined_success").format(group_name=group_name))
            else:
                st.error(localization.get_text("group_not_found").format(group_name=group_name))
        finally:
            session.close()  # 세션 종료


# --------------------------------------------------그룹 차단 데이터관리 -----------------------------------

class GroupBlockDAO:
    def __init__(self, user_id):
        self.user_id = user_id

    # 사용자가 그룹을 차단함
    def block_group(self, group_id):

        try:
            # 그룹 차단 추가
            block = GroupBlock(user_id=self.user_id, blocked_group_id=group_id)

            # 세션에 추가하고 커밋
            session.add(block)
            session.commit()
            session.close()
            # 차단 성공 메시지
            st.success(localization.get_text("group_blocked_success"))
            return True
        except Exception as e:
            # 오류 메시지 출력
            st.error(localization.get_text("group_block_error").format(error=e))
            session.rollback()  # 예외가 발생한 경우 롤백
        return False

    # 그룹 차단 해제
    def unblock_group(self, group_id):
        try:
            # 그룹 차단 레코드 삭제
            block = session.query(GroupBlock).filter_by(user_id=self.user_id, blocked_group_id=group_id).first()

            if block:
                # 해당 레코드를 삭제하고 커밋
                session.delete(block)
                session.commit()
                session.close()
                # 차단 해제 성공 메시지
                st.success(localization.get_text("group_unblocked_success"))
                return True
            else:
                # 차단된 그룹이 없을 경우 경고 메시지 출력
                st.warning(localization.get_text("group_not_blocked"))
                return False
        except Exception as e:
            # 오류 메시지 출력
            st.error(localization.get_text("group_unblock_error").format(error=e))
            session.rollback()  # 예외가 발생한 경우 롤백
        return False

    # 차단된 그룹 리스트를 반환
    def get_blocked_groups(self):
        try:
            # 차단된 그룹 조회
            blocked_groups = session.query(GroupBlock.blocked_group_id).filter_by(user_id=self.user_id).all()

            # 세션 종료
            session.close()

            # 결과를 리스트로 반환
            return [group[0] for group in blocked_groups]
        except Exception as e:
            # 오류 메시지 출력
            st.error(localization.get_text("blocked_groups_error").format(error=e))
            session.close()  # 세션 종료
        return []

    # 그룹이 차단되었는지 확인
    def is_group_blocked(self, group_id):
        try:
            # 조건에 맞는 차단된 그룹 레코드 존재 여부 확인
            result = session.query(GroupBlock).filter_by(user_id=self.user_id, blocked_group_id=group_id).first()

            # 세션 종료
            session.close()

            # 결과가 있으면 True, 없으면 False 반환
            return result is not None
        except Exception as e:
            # 오류 메시지 출력
            st.error(localization.get_text("is_group_blocked_error").format(error=e))
            session.close()  # 세션 종료
        return False


class GroupSearch:
    # 그룹 검색
    def search_groups(self, user_input, search_criteria):
        # 기본적인 Group 쿼리 시작
        query = session.query(
            Group.group_name, Group.group_creator, Group.meeting_date, Group.meeting_time,
            FoodCategory.category, Location.location_name,
            func.count(GroupMember.user_id).label('current_members')
        ).join(
            FoodCategory, Group.category == FoodCategory.category_id, isouter=True
        ).join(
            Location, Group.location == Location.location_id, isouter=True
        ).join(
            GroupMember, Group.group_id == GroupMember.group_id, isouter=True
        )

        # 검색 기준에 따른 조건 추가
        if search_criteria == localization.get_text("search_by_name"):
            query = query.filter(Group.group_name.like(f"%{user_input}%"))
        elif search_criteria == localization.get_text("search_by_date"):
            query = query.filter(Group.meeting_date == user_input)
        elif search_criteria == localization.get_text("search_by_category"):
            query = query.filter(Group.category == user_input)

        # 그룹 데이터 조회 실행
        groups = query.group_by(Group.group_id).all()

        # 세션 종료
        session.close()

        return groups


class FriendManager():
    def __init__(self, user_id):
        self.user_id = user_id

    def show_friend_list(self):
        session = SessionLocal()
        try:
            friends = session.query(Friend).filter(Friend.user_id == self.user_id).all()
            if friends:
                for friend in friends:
                    profile_picture = (
                        session.query(User.profile_picture_path)
                        .filter(User.user_id == friend.friend_user_id)
                        .scalar()
                    )
                    if not profile_picture or not os.path.exists(profile_picture):
                        profile_picture = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
                    st.image(profile_picture, width=50)
                    st.write(friend.friend_user_id)
                   
            else:
                st.write("친구가 없습니다.")
        finally:
            session.close()
    
    def show_friend_requests_page(self):
        st.title("친구 요청 관리")
        st.subheader("내가 보낸 친구 요청")
        sent_requests = self.friend_request.get_my_sent_requests()
        for req in sent_requests:
            st.write(f"- {req}")

        st.subheader("다른 사람이 보낸 친구 요청")
        received_requests = self.friend_request.get_received_requests()
        for req in received_requests:
            if st.button(f"수락 ({req})"):
                self.friend_request.accept_friend_request(req)
            if st.button(f"거절 ({req})"):
                self.friend_request.reject_friend_request(req)

        if st.button("뒤로 가기"):
            st.session_state["current_page"] = "after_login"
            st.rerun()

    # 차단 리스트 출력
    def show_blocked_list(self):
        try:
            # 차단된 사용자 목록 가져오기
            blocked_users = session.query(Block.blocked_user_id).filter(Block.user_id == self.user_id).all()

            if blocked_users:
                # 차단된 사용자 목록 제목 출력
                st.title(localization.get_text("blocked_list_title"))
                for blocked in blocked_users:
                    st.write(f"- {blocked.blocked_user_id}")
        finally:
            session.close()  # 세션 종료

    # 친구 차단
    def block_friend(self, friend_id):
        # 자신을 차단하려고 하면 오류 메시지 출력
        if self.user_id == friend_id:
            st.error(localization.get_text("block_self_error"))
            return

        try:
            # user 테이블에서 해당 ID 존재 여부 확인
            user_exists = session.query(User).filter(User.user_id == friend_id).first()
            if not user_exists:
                st.error(localization.get_text("user_not_found"))  # 해당 ID가 user 테이블에 없을 경우
                return

            # 이미 차단되었는지 확인
            already_blocked = session.query(Block).filter(
                Block.user_id == self.user_id,
                Block.blocked_user_id == friend_id
            ).first()
            if already_blocked:
                st.warning(localization.get_text("already_blocked"))
                return

            # 친구 목록에서 삭제
            session.query(Friend).filter(
                Friend.user_id == self.user_id,
                Friend.friend_user_id == friend_id
            ).delete()

            # 차단 테이블에 추가
            new_block = Block(user_id=self.user_id, blocked_user_id=friend_id)
            session.add(new_block)
            session.commit()

            # 차단 성공 메시지
            st.success(localization.get_text("block_success").format(friend_id=friend_id))
        finally:
            session.close()  # 세션 종료

    # 친구 차단 해제
    def unblock_friend(self, friend_id):
        try:
            # 차단된 사용자인지 확인
            blocked = session.query(Block).filter(
                Block.user_id == self.user_id,
                Block.blocked_user_id == friend_id
            ).first()

            if not blocked:
                # 차단된 사용자가 아닌 경우 경고 메시지 출력
                return

            # 차단 해제
            session.delete(blocked)
            session.commit()

            # 차단 해제 성공 메시지
            st.success(localization.get_text("unblock_success").format(friend_id=friend_id))
        finally:
            session.close()  # 세션 종료

    # 친구 삭제
    def delete_friend(self, friend_id):
        # 자신을 삭제하려고 하면 오류 메시지 출력
        if self.user_id == friend_id:
            st.error(localization.get_text("delete_self_error"))
            return

        try:
            # 친구 관계 확인
            is_friend = session.query(Friend).filter(
                (Friend.user_id == self.user_id) & (Friend.friend_user_id == friend_id) |
                (Friend.user_id == friend_id) & (Friend.friend_user_id == self.user_id)
            ).all()

            if not is_friend:
                # 친구가 아닌 경우 경고 메시지 출력
                st.warning(localization.get_text("not_in_friend_list"))
                return

            # 친구 삭제 - 양방향
            session.query(Friend).filter(
                (Friend.user_id == self.user_id) & (Friend.friend_user_id == friend_id) |
                (Friend.user_id == friend_id) & (Friend.friend_user_id == self.user_id)
            ).delete(synchronize_session="fetch")

            session.commit()

            # 삭제 성공 메시지
            st.success(localization.get_text("delete_friend_success").format(friend_id=friend_id))
        finally:
            session.close()  # 세션 종료
    
    def get_friend_posts(self):
        session = SessionLocal()
        try:
        # 친구들의 포스팅 가져오기
            friend_posts = (
                session.query(Posting)
                .join(Friend, Friend.friend_user_id == Posting.p_user)
                .filter(Friend.user_id == self.user_id)
                .all()
            )
            return friend_posts
        except Exception as e:
            st.error(f"오류 발생: {e}")
            return []
        finally:
            session.close()


# ------------------------------------------------------친구 요청 관리 --------------------------------------------------
class FriendRequest:
    def __init__(self, user_id):
        self.user_id = user_id

    # 친구 신청 함수
    def add_friend(self, friend_id):
        if self.user_id == friend_id:
            st.error("자신을 친구로 추가할 수 없습니다.")
            return

        session = SessionLocal()
        try:
            # 차단 여부 확인
            blocked = session.query(Block).filter(
                Block.user_id == self.user_id, Block.blocked_user_id == friend_id
            ).first()
            if blocked:
                st.error("먼저 차단을 해제해주세요.")
                return

            # 상대방 존재 확인
            user_exists = session.query(User).filter(User.user_id == friend_id).first()
            if not user_exists:
                st.error("없는 ID입니다.")
                return

            # 이미 친구인지 확인
            already_friends = session.query(Friend).filter(
                Friend.user_id == self.user_id, Friend.friend_user_id == friend_id
            ).first()
            if already_friends:
                st.error("이미 친구입니다.")
                return

            # 이미 요청을 보냈는지 확인
            already_requested = session.query(MyFriendRequest).filter(
                MyFriendRequest.user_id == self.user_id, MyFriendRequest.requested_user_id == friend_id
            ).first()
            if already_requested:
                st.error("이미 친구 요청을 보냈습니다.")
                return

            # 친구 요청 등록
            session.add(MyFriendRequest(user_id=self.user_id, requested_user_id=friend_id))
            session.add(OtherRequest(user_id=friend_id, requester_user_id=self.user_id))
            session.commit()
            st.success(f"{friend_id}님에게 친구 요청을 보냈습니다.")
        finally:
            session.close()

    # 내가 보낸 요청 목록
    def get_my_sent_requests(self):
        session = SessionLocal()
        try:
            requests = session.query(MyFriendRequest).filter(
                MyFriendRequest.user_id == self.user_id
            ).all()
            return [req.requested_user_id for req in requests]
        finally:
            session.close()

    # 내가 받은 친구 요청
    def get_received_requests(self):
        session = SessionLocal()
        try:
            requests = session.query(OtherRequest).filter(
                OtherRequest.user_id == self.user_id
            ).all()
            return [req.requester_user_id for req in requests]
        finally:
            session.close()
    # 친구 신청 받기
    def accept_friend_request(self, requester_id):
        session = SessionLocal()
        try:
            session.add(Friend(user_id=self.user_id, friend_user_id=requester_id))
            session.add(Friend(user_id=requester_id, friend_user_id=self.user_id))
            session.query(MyFriendRequest).filter(
                MyFriendRequest.user_id == requester_id, MyFriendRequest.requested_user_id == self.user_id
            ).delete()
            session.query(OtherRequest).filter(
                OtherRequest.user_id == self.user_id, OtherRequest.requester_user_id == requester_id
            ).delete()
            session.commit()
            st.success(f"{requester_id}님과 친구가 되었습니다.")
        finally:
            session.close()


    # 친구 신청 거절
    def reject_friend_request(self, requester_id):
        session = SessionLocal()
        try:
            session.query(MyFriendRequest).filter(
                MyFriendRequest.user_id == requester_id, MyFriendRequest.requested_user_id == self.user_id
            ).delete()
            session.query(OtherRequest).filter(
                OtherRequest.user_id == self.user_id, OtherRequest.requester_user_id == requester_id
            ).delete()
            session.commit()
            st.success(f"{requester_id}님의 친구 요청을 거절했습니다.")
        finally:
            session.close()


app = Page()
app.render_page()


