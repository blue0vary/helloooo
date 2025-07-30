import streamlit as st
import random
import smtplib
import time
import pandas as pd
import os
from email.message import EmailMessage

st.set_page_config(page_title="회원가입/로그인", page_icon="🔐")

USER_FILE = "users.csv"

# 사용자 정보 저장 및 불러오기
def save_user(name, email, password):
    new = pd.DataFrame([[name, email, password]], columns=["이름","이메일","비밀번호"])
    if os.path.exists(USER_FILE):
        new.to_csv(USER_FILE, mode='a', header=False, index=False)
    else:
        new.to_csv(USER_FILE, index=False)

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    return pd.DataFrame(columns=["이름","이메일","비밀번호"])

# 초기 세션 상태 설정
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'auth_code' not in st.session_state:
    st.session_state.auth_code = ""
if 'code_sent' not in st.session_state:
    st.session_state.code_sent = False
if 'code_sent_time' not in st.session_state:
    st.session_state.code_sent_time = 0

# 다국어 설정
language = st.sidebar.selectbox("언어 선택 / Select Language / 言語を選んでください / 请选择语言",
                                ["한국어","English","日本語","中文"])
T = {
    'signup': {'한국어':"회원가입",'English':"Sign Up",'日本語':"サインアップ",'中文':"注册账号"},
    'login': {'한국어':"로그인",'English':"Log In",'日本語':"ログイン",'中文':"登录"},
    'name': {'한국어':"이름",'English':"Name",'日本語':"名前",'中文':"姓名"},
    'email': {'한국어':"이메일",'English':"Email",'日本語':"メールアドレス",'中文':"电子邮箱"},
    'password': {'한국어':"비밀번호",'English':"Password",'日本語':"パスワード",'中文':"密码"},
    'confirm_pw': {'한국어':"비밀번호 확인",'English':"Confirm Password",'日本語':"パスワード確認",'中文':"确认密码"},
    'send_code': {'한국어':"인증번호 보내기",'English':"Send Code",'日本語':"認証コード送信",'中文':"发送验证码"},
    'enter_code': {'한국어':"인증번호 입력",'English':"Enter Code",'日本語':"認証コード入力",'中文':"输入验证码"},
    'submit_signup': {'한국어':"회원가입 완료",'English':"Complete Sign Up",'日本語':"サインアップ完了",'中文':"完成注册"},
    'submit_login': {'한국어':"로그인",'English':"Log In",'日本語':"ログイン",'中文':"登录"},
    'code_sent': {'한국어':"📧 이메일로 인증번호를 보냈습니다.",'English':"📧 Verification code sent to email.",'日本語':"📧 メールで認証コードを送りました。",'中文':"📧 验证码已发送到您的邮箱。"},
    'code_fail': {'한국어':"인증번호가 틀렸습니다.",'English':"Invalid code.",'日本語':"認証コードが間違っています。",'中文':"验证码错误。"},
    'code_expired': {'한국어':"⏰ 인증번호가 만료되었습니다. 다시 시도해주세요.",'English':"⏰ Code expired. Please request again.",'日本語':"⏰ 認証コードの有効期限が切れました。",'中文':"⏰ 验证码已过期，请重新获取。"},
    'pw_mismatch': {'한국어':"비밀번호가 일치하지 않습니다.",'English':"Passwords do not match.",'日本語':"パスワードが一致しません。",'中文':"两次密码不一致。"},
    'empty_field': {'한국어':"모든 항목을 입력해주세요.",'English':"Please fill in all fields.",'日本語':"すべての項目を入力してください。",'中文':"请填写所有信息。"},
    'signup_success': {'한국어':"{}님, 회원가입이 완료되었습니다!",'English':"Welcome, {}! Registration complete.",'日本語':"{}さん、サインアップ完了！",'中文':"{}，注册成功！"},
    'login_success': {'한국어':"{}님, 로그인 성공했습니다!",'English':"🎉 Welcome back, {}!",'日本語':"{}さん、ログイン成功！",'中文':"🎉 欢迎回来，{}！"},
    'login_fail': {'한국어':"이메일 또는 비밀번호가 올바르지 않습니다.",'English':"Email or password incorrect.",'日本語':"メールまたはパスワードが違います。",'中文':"邮箱或密码不正确。"},
    'enter_email': {'한국어':"이메일을 입력해주세요.",'English':"Please enter email.",'日本語':"メールを入力してください。",'中文':"请输入邮箱。"},
    'email_error': {'한국어':"이메일 전송 실패: {}",'English':"Failed to send email: {}",'日本語':"メール送信失敗: {}",'中文':"邮件发送失败：{}"}
}

# 로그인 유지: 이미 로그인 상태면 메인 페이지 표시
if st.session_state.logged_in:
    st.header(f"{T['login_success'][language].format(st.session_state.user_name)}")
    st.write("이곳이 로그인 후 보여줄 페이지 예시입니다.")
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
    st.stop()

# 페이지 선택
page = st.sidebar.radio("", [T['signup'][language], T['login'][language]])

# 회원가입 페이지
if page == T['signup'][language]:
    st.header(T['signup'][language])
    name = st.text_input(T['name'][language])
    email = st.text_input(T['email'][language])
    password = st.text_input(T['password'][language], type="password")
    confirm_pw = st.text_input(T['confirm_pw'][language], type="password")

    if st.button(T['send_code'][language]):
        if email:
            code = str(random.randint(100000,999999))
            st.session_state.auth_code = code
            st.session_state.code_sent = True
            st.session_state.code_sent_time = time.time()
            msg = EmailMessage()
            msg["Subject"] = "회원가입 인증번호 / Verification Code"
            msg["From"] = "blue0vary@gmail.com"
            msg["To"] = email
            msg.set_content(f"인증번호 / Verification code: {code}")
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:
                    smtp.login("blue0vary@gmail.com","tpms wssc fhjw ftyb")
                    smtp.send_message(msg)
                st.success(T['code_sent'][language])
                st.info("⚠️ 인증번호는 5분 동안만 유효합니다.")
            except Exception as e:
                st.error(T['email_error'][language].format(str(e)))
        else:
            st.warning(T['enter_email'][language])

    if st.session_state.code_sent:
        user_code = st.text_input(T['enter_code'][language])
        if st.button(T['submit_signup'][language]):
            if not all([name,email,password,confirm_pw,user_code]):
                st.warning(T['empty_field'][language])
            elif password != confirm_pw:
                st.error(T['pw_mismatch'][language])
            elif time.time() - st.session_state.code_sent_time > 300:
                st.error(T['code_expired'][language])
                st.session_state.code_sent = False
            elif user_code != st.session_state.auth_code:
                st.error(T['code_fail'][language])
            else:
                users = load_users()
                if email in users["이메일"].values:
                    st.warning("이미 등록된 이메일입니다.")
                else:
                    save_user(name,email,password)
                    st.success(T['signup_success'][language].format(name))

# 로그인 페이지
elif page == T['login'][language]:
    st.header(T['login'][language])
    email = st.text_input(T['email'][language])
    password = st.text_input(T['password'][language], type="password")
    if st.button(T['submit_login'][language]):
        users = load_users()
        match = users[(users["이메일"]==email)&(users["비밀번호"]==password)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.user_name = match.iloc[0]["이름"]
            st.rerun()
        else:
            st.error(T['login_fail'][language])
