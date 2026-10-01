from functools import wraps
import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from supabase import create_client, Client
from supabase_auth.errors import AuthApiError, AuthError

# 'auth' 블루프린트 생성 (url_prefix='/auth')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ==============================================================================
# Supabase 클라이언트 초기화 헬퍼 함수
# ==============================================================================
def get_supabase_client() -> Client:
    """
    Supabase 클라이언트를 반환합니다.
    환경변수 SUPABASE_URL 및 SUPABASE_KEY(또는 SUPABASE_ANON_KEY)를 사용합니다.
    """
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
    if not supabase_url or not supabase_key:
        # 환경변수가 없을 경우 빈 클라이언트를 방지하기 위해 예외 발생 가능
        pass
    return create_client(supabase_url, supabase_key)


# ==============================================================================
# 로그인 필수 데코레이터
# ==============================================================================
def login_required(f):
    """
    Flask 세션에서 'user_id' 존재 여부를 확인하는 데코레이터.
    로그인되지 않은 경우 안내 메시지와 함께 로그인 페이지로 리다이렉트합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', error='login_required'))
        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# [1] GET / POST /auth/login - 로그인 폼 및 처리
# ==============================================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    [1] 로그인 처리
    - GET: 로그인 폼 표시 (error / msg 파라미터 처리)
    - POST: Supabase sign_in_with_password 처리
      - 이메일 미인증 시 error=email_not_confirmed
    """
    # 이미 로그인된 상태라면 마이페이지로 이동
    if request.method == 'GET' and session.get('user_id'):
        return redirect(url_for('main.mypage'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            return redirect(url_for('auth.login', error='empty_fields'))

        try:
            supabase = get_supabase_client()
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            user = res.user
            auth_session = res.session

            if not user:
                return redirect(url_for('auth.login', error='invalid_credentials'))

            # 이메일 미인증 검사: email_confirmed_at 또는 confirmed_at 확인
            email_confirmed = getattr(user, 'email_confirmed_at', None) or getattr(user, 'confirmed_at', None)
            if not email_confirmed:
                return redirect(url_for('auth.login', error='email_not_confirmed'))

            # 사용자 이름 추출 (user_metadata -> email 앞부분)
            user_metadata = getattr(user, 'user_metadata', {}) or {}
            display_name = user_metadata.get('name') or user_metadata.get('full_name') or email.split('@')[0]

            # Flask session에 user_id 및 세션 정보 저장
            session['user_id'] = user.id
            session['user'] = {
                'id': user.id,
                'email': user.email,
                'name': display_name
            }
            if auth_session:
                session['access_token'] = auth_session.access_token
                session['refresh_token'] = auth_session.refresh_token

            return redirect(url_for('main.mypage'))

        except (AuthApiError, AuthError) as e:
            error_msg = str(e).lower()
            if 'email not confirmed' in error_msg:
                return redirect(url_for('auth.login', error='email_not_confirmed'))
            elif 'invalid login credentials' in error_msg or 'invalid_credentials' in error_msg:
                return redirect(url_for('auth.login', error='invalid_credentials'))
            else:
                return redirect(url_for('auth.login', error='auth_error'))
        except Exception:
            return redirect(url_for('auth.login', error='server_error'))

    error_code = request.args.get('error')
    msg_code = request.args.get('msg')
    return render_template('auth/login.html', error_code=error_code, msg_code=msg_code)


# ==============================================================================
# [2] GET / POST /auth/signup - 회원가입 폼 및 처리
# ==============================================================================
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    [2] 회원가입 처리
    - GET: 회원가입 폼 표시
    - POST: Supabase sign_up 처리
      - 성공 시 /auth/signup-complete 로 리다이렉트
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        policy_agree = request.form.get('policy_agree')

        if not policy_agree:
            return redirect(url_for('auth.signup', error='policy_required'))

        if not name or not email or not password:
            return redirect(url_for('auth.signup', error='empty_fields'))

        if len(password) < 6:
            return redirect(url_for('auth.signup', error='password_too_short'))

        site_url = os.getenv("SITE_URL", "http://localhost:5000").rstrip('/')
        email_redirect_to = f"{site_url}/auth/confirm"

        try:
            supabase = get_supabase_client()
            res = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name,
                        "full_name": name
                    },
                    "email_redirect_to": email_redirect_to
                }
            })

            # 가입 성공 시 인증 메일 안내 페이지로 이동
            return redirect(url_for('auth.signup_complete', email=email))

        except (AuthApiError, AuthError) as e:
            error_msg = str(e).lower()
            if 'user already registered' in error_msg or 'already exists' in error_msg:
                return redirect(url_for('auth.signup', error='already_registered'))
            return redirect(url_for('auth.signup', error='signup_failed'))
        except Exception:
            return redirect(url_for('auth.signup', error='server_error'))

    error_code = request.args.get('error')
    msg_code = request.args.get('msg')
    return render_template('auth/signup.html', error_code=error_code, msg_code=msg_code)


# ==============================================================================
# [3] GET /auth/signup-complete - 인증 메일 발송 안내
# ==============================================================================
@auth_bp.route('/signup-complete')
def signup_complete():
    """
    [3] 회원가입 완료 및 이메일 인증 링크 확인 안내 페이지
    """
    email = request.args.get('email', '')
    return render_template('auth/signup_complete.html', email=email)


# ==============================================================================
# [4] GET /auth/confirm - 이메일 인증 링크 클릭 처리
# ==============================================================================
@auth_bp.route('/confirm')
def confirm():
    """
    [4] 이메일 인증 링크 콜백 처리
    Supabase 인증 이메일의 링크를 타고 들어올 때 token_hash 및 type 전달됨.
    verify_otp 호출 -> 성공 시 Flask session 저장 -> /mypage 리다이렉트
    """
    token_hash = request.args.get('token_hash')
    otp_type = request.args.get('type', 'signup')
    code = request.args.get('code')

    try:
        supabase = get_supabase_client()
        res = None

        if token_hash:
            # token_hash 기반 verify_otp
            res = supabase.auth.verify_otp({
                "token_hash": token_hash,
                "type": otp_type
            })
        elif code:
            # PKCE 코드 기반 exchange (세션에 저장된 code_verifier 사용)
            code_verifier = session.pop('code_verifier', None)
            exchange_params = {"auth_code": code}
            if code_verifier:
                exchange_params["code_verifier"] = code_verifier
            res = supabase.auth.exchange_code_for_session(exchange_params)
        else:
            return redirect(url_for('auth.login', error='invalid_verification_link'))

        if res and res.user:
            user = res.user
            auth_session = res.session

            user_metadata = getattr(user, 'user_metadata', {}) or {}
            display_name = user_metadata.get('name') or user_metadata.get('full_name') or (user.email.split('@')[0] if user.email else '고객')

            session['user_id'] = user.id
            session['user'] = {
                'id': user.id,
                'email': user.email,
                'name': display_name
            }
            if auth_session:
                session['access_token'] = auth_session.access_token
                session['refresh_token'] = auth_session.refresh_token

            # 비밀번호 복구(recovery) 인증일 경우 새 비밀번호 설정 페이지로 안내
            if otp_type == 'recovery':
                return redirect(url_for('auth.reset_password', msg='recovery_verified'))

            return redirect(url_for('main.mypage'))
        else:
            return redirect(url_for('auth.login', error='verification_failed'))

    except (AuthApiError, AuthError):
        return redirect(url_for('auth.login', error='verification_expired'))
    except Exception:
        return redirect(url_for('auth.login', error='verification_failed'))


# ==============================================================================
# [5] GET / POST /auth/forgot-password - 비밀번호 재설정 메일 발송
# ==============================================================================
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    [5] 비밀번호 재설정 링크 발송 요청
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            return redirect(url_for('auth.forgot_password', error='empty_email'))

        site_url = os.getenv("SITE_URL", "http://localhost:5000").rstrip('/')
        redirect_to = f"{site_url}/auth/confirm"

        try:
            supabase = get_supabase_client()
            supabase.auth.reset_password_email(
                email,
                options={"redirect_to": redirect_to}
            )
            return redirect(url_for('auth.forgot_password', msg='reset_email_sent'))
        except (AuthApiError, AuthError):
            # 보안상 이메일 존재 여부와 무관하게 전송 메시지를 띄우거나 에러 표기
            return redirect(url_for('auth.forgot_password', msg='reset_email_sent'))
        except Exception:
            return redirect(url_for('auth.forgot_password', error='server_error'))

    error_code = request.args.get('error')
    msg_code = request.args.get('msg')
    return render_template('auth/forgot_password.html', error_code=error_code, msg_code=msg_code)


# ==============================================================================
# [6] GET / POST /auth/reset-password - 새 비밀번호 설정
# ==============================================================================
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """
    [6] 새 비밀번호 입력 및 변경 처리
    인증 링크(recovery)를 통해 세션이 수립되었거나 access_token이 있는 상태에서 호출됩니다.
    """
    # 세션이나 토큰이 없는 비로그인 상태일 경우 확인
    if not session.get('user_id') and not session.get('access_token'):
        return redirect(url_for('auth.login', error='reset_session_expired'))

    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            return redirect(url_for('auth.reset_password', error='empty_fields'))

        if new_password != confirm_password:
            return redirect(url_for('auth.reset_password', error='password_mismatch'))

        if len(new_password) < 6:
            return redirect(url_for('auth.reset_password', error='password_too_short'))

        try:
            supabase = get_supabase_client()

            # 세션에 access_token과 refresh_token이 있다면 세션 복원
            access_token = session.get('access_token')
            refresh_token = session.get('refresh_token', '')
            if access_token:
                try:
                    supabase.auth.set_session(access_token, refresh_token)
                except Exception:
                    pass

            supabase.auth.update_user({
                "password": new_password
            })

            # 비밀번호 변경 완료 후 로그인 페이지로 안내 (성공 메시지)
            return redirect(url_for('auth.login', msg='password_reset_success'))

        except (AuthApiError, AuthError):
            return redirect(url_for('auth.reset_password', error='update_password_failed'))
        except Exception:
            return redirect(url_for('auth.reset_password', error='server_error'))

    error_code = request.args.get('error')
    msg_code = request.args.get('msg')
    return render_template('auth/reset_password.html', error_code=error_code, msg_code=msg_code)


# ==============================================================================
# [7] GET /auth/kakao - 카카오 간편 로그인 요청
# ==============================================================================
@auth_bp.route('/kakao')
def kakao():
    """
    [7] 카카오 간편 로그인 처리
    Supabase OAuth 인증을 통해 카카오 로그인 동의 화면으로 리다이렉트합니다.
    """
    site_url = os.getenv("SITE_URL", "http://localhost:5000").rstrip('/')
    redirect_to = f"{site_url}/auth/confirm"

    try:
        supabase = get_supabase_client()
        res = supabase.auth.sign_in_with_oauth({
            "provider": "kakao",
            "options": {
                "redirect_to": redirect_to,
                "query_params": {
                    "scope": "profile_nickname profile_image"
                }
            }
        })
        verifier = getattr(supabase.auth, '_storage', None)
        if verifier:
            storage_key = getattr(supabase.auth, '_storage_key', 'supabase.auth')
            code_verifier = supabase.auth._storage.get_item(f"{storage_key}-code-verifier")
            if code_verifier:
                session['code_verifier'] = code_verifier

        if res and res.url:
            return redirect(res.url)
        return redirect(url_for('auth.login', error='kakao_failed'))
    except Exception:
        return redirect(url_for('auth.login', error='kakao_failed'))


# ==============================================================================
# 로그아웃 라우트
# ==============================================================================
@auth_bp.route('/logout')
def logout():
    """
    로그아웃 처리
    - Supabase sign_out 호출 및 Flask 세션 정리
    """
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception:
        pass

    session.pop('user_id', None)
    session.pop('user', None)
    session.pop('access_token', None)
    session.pop('refresh_token', None)

    return redirect(url_for('auth.login', msg='logout_success'))
