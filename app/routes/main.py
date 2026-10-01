from datetime import datetime
import os
import uuid
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.routes.auth import login_required, get_supabase_client

# 'main'이라는 이름의 블루프린트 생성
# URL 프리픽스 없이 루트('/') 경로 등 메인 화면을 담당합니다.
main_bp = Blueprint('main', __name__)

# 전역 상품 마스터 목록 (ID로 검색 가능하도록 딕셔너리 및 리스트 제공)
PRODUCTS = [
    # --- 쥬얼리 / 악세사리 (BEST 다이아 목걸이 컬렉션) ---
    {
        "id": 1,
        "name": "1부 다이아목걸이 데끌라 프로포즈목걸이",
        "category": "JEWELRY",
        "badge": "BEST",
        "price": "395,000",
        "original_price": None,
        "sub_desc": "여친선물 1위 / 디자이너 극찬! 당일발송 가능",
        "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80",
        "description": "물방울 라인 프레임에 세팅된 영롱한 1부 다이아몬드 프로포즈 목걸이"
    },
    {
        "id": 2,
        "name": "1부 다이아목걸이 프로포즈 크로벨 목걸이",
        "category": "JEWELRY",
        "badge": "BEST",
        "price": "436,500",
        "original_price": "485,000",
        "sub_desc": "여친선물 1위 / 쿠폰적용 10% 특별할인",
        "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&auto=format&fit=crop&q=80",
        "description": "유려한 트위스트 곡선과 서브 스톤이 조화로운 프리미엄 프로포즈 목걸이"
    },
    {
        "id": 3,
        "name": "1부 다이아 프로포즈목걸이 키스미",
        "category": "JEWELRY",
        "badge": "BEST",
        "price": "481,500",
        "original_price": "535,000",
        "sub_desc": "섬세하고 입체적인 하트라인 / 10% 할인",
        "image": "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800&auto=format&fit=crop&q=80",
        "description": "로맨틱한 하트 프레임 속에 빛나는 1부 다이아몬드 펜던트"
    },
    {
        "id": 4,
        "name": "1부 다이아 듀얼 링 서클 프로포즈 목걸이",
        "category": "JEWELRY",
        "badge": "BEST",
        "price": "490,500",
        "original_price": "545,000",
        "sub_desc": "투톤 서클 링 & 드롭 큐빅 포인트 인기상품",
        "image": "https://images.unsplash.com/photo-1600003014755-ba31aa59c4b6?w=800&auto=format&fit=crop&q=80",
        "description": "로즈골드와 화이트골드 링이 교차되며 드롭되는 우아한 듀얼 링 목걸이"
    },
    # --- 시계 / 워치 (BEST 클래식 스퀘어 메쉬 시계) ---
    {
        "id": 5,
        "name": "KUMTTON 스퀘어 자개 다이얼 실버 메쉬 시계",
        "category": "WATCH",
        "badge": "BEST",
        "price": "89,000",
        "original_price": "128,000",
        "sub_desc": "로마자 자개 다이얼 & 메탈 메쉬 스트랩 / 베스트 1위",
        "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&auto=format&fit=crop&q=80",
        "description": "우아한 스퀘어 실버 프레임과 은은한 빛의 자개 다이얼이 돋보이는 쿼츠 손목시계"
    },
    # --- 악세사리 (귀걸이, 반지) ---
    {
        "id": 6,
        "name": "14K 골드 도금 볼드 드롭 귀걸이",
        "category": "ACC",
        "badge": "NEW",
        "price": "32,000",
        "original_price": None,
        "sub_desc": "은은한 골드 광택 / 모던 드롭 라인",
        "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&auto=format&fit=crop&q=80",
        "description": "은은한 골드 광택과 감각적인 곡선이 돋보이는 모던 드롭 이어링"
    },
    {
        "id": 7,
        "name": "빈티지 실버 925 와이드 링 (반지)",
        "category": "ACC",
        "badge": "NEW",
        "price": "29,000",
        "original_price": None,
        "sub_desc": "핸드메이드 텍스처 / 925 실버",
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&auto=format&fit=crop&q=80",
        "description": "볼드하면서도 감성적인 텍스처를 살린 핸드메이드 실버 925 링"
    },
    # --- 잡화 / 패션 (신발, 가방, 아우터) ---
    {
        "id": 8,
        "name": "클래식 레더 더비 슈즈",
        "category": "SHOES",
        "badge": "MD추천",
        "price": "145,000",
        "original_price": None,
        "sub_desc": "천연 소가죽 / 쿠셔닝 인솔",
        "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80",
        "description": "미니멀한 실루엣과 편안한 쿠셔닝을 갖춘 데일리 천연 소가죽 슈즈"
    },
    {
        "id": 9,
        "name": "레트로 미니멀 크로스백",
        "category": "BAG",
        "badge": "MD추천",
        "price": "89,000",
        "original_price": None,
        "sub_desc": "탄탄한 가죽 / 넉넉한 수납력",
        "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&auto=format&fit=crop&q=80",
        "description": "탄탄한 가죽 소재와 실용적인 수납력을 자랑하는 미니멀 크로스백"
    },
    {
        "id": 10,
        "name": "오버핏 미니멀 블레이저",
        "category": "OUTER",
        "badge": "BEST",
        "price": "129,000",
        "original_price": None,
        "sub_desc": "트렌디한 오버핏 / 고밀도 원단",
        "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80",
        "description": "어떤 룩에도 자연스럽게 어우러지는 트렌디한 오버핏 실루엣 블레이저"
    },
    # --- 의류 (원피스, 바지, 티셔츠 등) ---
    {
        "id": 11,
        "name": "플로럴 쉬폰 미디 랩 원피스",
        "category": "DRESS",
        "badge": "BEST",
        "price": "48,000",
        "original_price": "58,000",
        "sub_desc": "여리여리한 랩 실루엣 / 페미닌 무드",
        "image": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&auto=format&fit=crop&q=80",
        "description": "화사한 플라워 패턴과 허리 리본 디테일이 돋보이는 쉬폰 랩 미디 원피스"
    },
    {
        "id": 12,
        "name": "모던 슬림 골지 니트 롱 원피스",
        "category": "DRESS",
        "badge": "NEW",
        "price": "52,000",
        "original_price": None,
        "sub_desc": "탄탄한 골지 텍스처 / 슬림 핏 라인",
        "image": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800&auto=format&fit=crop&q=80",
        "description": "우아하고 단정한 무드를 연출해주는 프리미엄 골지 니트 롱 원피스"
    },
    {
        "id": 13,
        "name": "투턱 와이드 슬랙스 팬츠",
        "category": "PANTS",
        "badge": "BEST",
        "price": "45,000",
        "original_price": "52,000",
        "sub_desc": "체형 커버 투턱 라인 / 롱 레그 실루엣",
        "image": "https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?w=800&auto=format&fit=crop&q=80",
        "description": "깔끔하게 떨어지는 투턱 핀턱 디테일과 하이웨이스트 와이드 핏 슬랙스"
    },
    {
        "id": 14,
        "name": "데일리 빈티지 와이드 데님 팬츠",
        "category": "PANTS",
        "badge": "MD추천",
        "price": "42,000",
        "original_price": None,
        "sub_desc": "은은한 워싱 & 탄탄한 코튼 100%",
        "image": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&auto=format&fit=crop&q=80",
        "description": "사계절 내내 다양하게 코디하기 좋은 미드 블루 컬러의 와이드 데님 팬츠"
    },
    {
        "id": 15,
        "name": "베이직 헤비 코튼 크롭 반팔 티셔츠",
        "category": "TOP",
        "badge": "BEST",
        "price": "24,000",
        "original_price": "29,000",
        "sub_desc": "탄탄한 20수 코튼 / 넥라인 늘어짐 방지",
        "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80",
        "description": "군더더기 없는 베이직 디자인과 트렌디한 크롭 기장의 데일리 반팔 티셔츠"
    },
    {
        "id": 16,
        "name": "프렌치 빈티지 레터링 오버핏 티셔츠",
        "category": "TOP",
        "badge": "NEW",
        "price": "28,000",
        "original_price": None,
        "sub_desc": "감각적인 컬러 배색 / 여유로운 루즈핏",
        "image": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800&auto=format&fit=crop&q=80",
        "description": "빈티지 무드의 프렌치 감성 폰트가 포인트인 루즈핏 오버사이즈 티셔츠"
    },
    {
        "id": 17,
        "name": "클래식 릴렉스드 스트라이프 셔츠",
        "category": "TOP",
        "badge": "MD추천",
        "price": "46,000",
        "original_price": "54,000",
        "sub_desc": "내추럴 링클 프리 코튼 / 모던 캐주얼",
        "image": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80",
        "description": "단독 또는 가벼운 아우터로 레이어드하기 좋은 클래식 스트라이프 셔츠"
    },
    {
        "id": 18,
        "name": "코튼 린넨 맥시 셔츠 원피스",
        "category": "DRESS",
        "badge": "BEST",
        "price": "56,000",
        "original_price": "68,000",
        "sub_desc": "시원한 린넨 혼방 / 허리 스트링 조절",
        "image": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&auto=format&fit=crop&q=80",
        "description": "자연스러운 핏과 편안한 활동성을 갖춘 클래식 버튼업 맥시 원피스"
    },
    {
        "id": 19,
        "name": "세미 슬림 컷팅 일자 데님 팬츠",
        "category": "PANTS",
        "badge": "NEW",
        "price": "43,000",
        "original_price": None,
        "sub_desc": "밑단 내추럴 컷팅 / 탄탄 스판",
        "image": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&auto=format&fit=crop&q=80",
        "description": "어떤 슈즈와도 매칭하기 좋은 감각적인 워싱의 세미 일자 핏 청바지"
    },
    {
        "id": 20,
        "name": "카고 스트링 조거 팬츠",
        "category": "PANTS",
        "badge": "BEST",
        "price": "39,000",
        "original_price": "48,000",
        "sub_desc": "트렌디 스트릿 무드 / 편안한 밴딩",
        "image": "https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?w=800&auto=format&fit=crop&q=80",
        "description": "밑단 조절 가능한 스트링과 포켓 디테일이 돋보이는 데일리 카고 조거팬츠"
    },
    {
        "id": 21,
        "name": "프리미엄 수피마 코튼 무지 티셔츠",
        "category": "TOP",
        "badge": "기획특가",
        "price": "19,900",
        "original_price": "28,000",
        "sub_desc": "부드러운 촉감 & 탁월한 내구성 1+1",
        "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80",
        "description": "최상급 수피마 코튼 소재로 제작되어 세탁 후에도 변형 없는 데일리 무지 티"
    },
    {
        "id": 22,
        "name": "오버핏 그래픽 아트웍 반팔 티셔츠",
        "category": "TOP",
        "badge": "NEW",
        "price": "31,000",
        "original_price": None,
        "sub_desc": "감각적인 백프린팅 & 드롭숄더 핏",
        "image": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800&auto=format&fit=crop&q=80",
        "description": "후면의 감각적인 빈티지 그래픽이 시선을 사로잡는 오버핏 스트릿 티셔츠"
    },
    {
        "id": 23,
        "name": "소프트 케이블 브이넥 니트 베스트",
        "category": "TOP",
        "badge": "MD추천",
        "price": "34,000",
        "original_price": "42,000",
        "sub_desc": "레이어드 찰떡 아이템 / 폭신한 착용감",
        "image": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&auto=format&fit=crop&q=80",
        "description": "셔츠나 티셔츠 위에 가볍게 덧입어 센스있는 룩을 완성하는 꽈배기 니트 조끼"
    },
    {
        "id": 24,
        "name": "모던 클래식 롱 트렌치 코트",
        "category": "OUTER",
        "badge": "BEST",
        "price": "148,000",
        "original_price": "185,000",
        "sub_desc": "생활 방수 원단 / 고급스러운 더블 버튼",
        "image": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=800&auto=format&fit=crop&q=80",
        "description": "클래식한 디테일과 세련된 실루엣으로 봄/가을 시즌을 완성하는 프리미엄 트렌치코트"
    },
    # --- 로맨틱 & 샤랄라 부티크 컬렉션 (LOVELY & ELEGANT) ---
    {
        "id": 25,
        "name": "페어리 쉬폰 플라워 캉캉 롱 원피스",
        "category": "DRESS",
        "badge": "HOT",
        "price": "92,000",
        "original_price": "115,000",
        "sub_desc": "살랑살랑 봄바람 실루엣 / 하객룩 & 데이트룩 베스트",
        "image": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&auto=format&fit=crop&q=80",
        "description": "은은한 플로럴 나염과 층층이 퍼지는 티어드 캉캉 주름이 움직일 때마다 로맨틱한 샤랄라 무드를 완성합니다."
    },
    {
        "id": 26,
        "name": "오간자 시스루 리본 타이 퍼프 블라우스",
        "category": "TOP",
        "badge": "NEW",
        "price": "68,000",
        "original_price": "85,000",
        "sub_desc": "은은한 광택 오간자 / 풍성한 볼륨 퍼프소매",
        "image": "https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=800&auto=format&fit=crop&q=80",
        "description": "빛을 받을 때마다 영롱하게 반짝이는 오간자 시스루 원단과 로맨틱한 리본 타이로 여신 분위기를 연출합니다."
    },
    {
        "id": 27,
        "name": "발레리나 튤 메쉬 롱 플레어 스커트",
        "category": "PANTS",
        "badge": "MD추천",
        "price": "59,000",
        "original_price": None,
        "sub_desc": "3중 샤스커트 튤 레이어드 / 밴딩 허리",
        "image": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800&auto=format&fit=crop&q=80",
        "description": "풍성한 3겹 메쉬 튤 소재로 걸을 때마다 구름 위를 걷는 듯 가볍고 우아하게 흩날리는 샤랄라 발레코어 스커트입니다."
    },
    {
        "id": 28,
        "name": "파스텔 프릴 레이스 드레이핑 미니 원피스",
        "category": "DRESS",
        "badge": "NEW",
        "price": "86,000",
        "original_price": "108,000",
        "sub_desc": "화사한 파스텔 핑크 / 입체 프릴 디테일",
        "image": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800&auto=format&fit=crop&q=80",
        "description": "섬세한 물결 프릴과 입체적인 레이스 드레이핑이 어우러져 청순하면서도 화사한 아우라를 선사하는 미니 드레스입니다."
    }
]

# ID로 빠른 조회가 가능한 상품 사전
PRODUCT_DICT = {p["id"]: p for p in PRODUCTS}

# 세션 내 장바구니 총 수량 계산 헬퍼 함수
def get_cart_count():
    cart = session.get('cart', {})
    return sum(cart.values())

@main_bp.context_processor
def inject_global_data():
    """모든 템플릿에서 로그인 사용자 정보와 장바구니 수량에 접근 가능하도록 컨텍스트 주입"""
    user = session.get('user')
    return {
        'current_user': user,
        'cart_count': get_cart_count()
    }

@main_bp.route('/')
def index():
    """
    메인 페이지 핸들러 함수:
    쇼핑몰 홈 화면에 보여줄 상품 목록을 정의하고
    index.html 템플릿에 전달하여 렌더링합니다.
    """
    return render_template('index.html', products=PRODUCTS)


# ==============================================================================
# 회원가입 / 로그인 / 로그아웃 / 마이페이지 / 탈퇴 라우트
# ==============================================================================

@main_bp.route('/signup-policy')
def signup_policy():
    """회원가입 정책 및 이용약관 페이지"""
    return render_template('signup_policy.html')


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 페이지 (auth 블루프린트로 리다이렉트)"""
    return redirect(url_for('auth.signup'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지 (auth 블루프린트로 리다이렉트)"""
    return redirect(url_for('auth.login'))


@main_bp.route('/logout')
def logout():
    """로그아웃 처리 (auth 블루프린트로 리다이렉트)"""
    return redirect(url_for('auth.logout'))


@main_bp.route('/mypage', methods=['GET', 'POST'])
@login_required
def mypage():
    """
    [마이페이지]
    - profiles 테이블에서 로그인 사용자 정보 조회하여 내 정보 표시
    - 내 정보 수정 폼 처리 (POST)
    - Bootstrap 5 nav-tabs 3개 (내 정보 / 주문 내역 / 환불 내역)
    """
    user_id = session.get('user_id')
    user = session.get('user') or {}
    supabase = get_supabase_client()

    # POST 요청 시 내 정보 수정 처리
    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        new_phone = request.form.get('phone', '').strip()
        new_address = request.form.get('address', '').strip()

        try:
            # 1. profiles 테이블 업데이트
            update_data = {
                "full_name": new_name,
                "phone": new_phone
            }
            try:
                supabase.table("profiles").update({**update_data, "address": new_address}).eq("id", user_id).execute()
            except Exception:
                supabase.table("profiles").update(update_data).eq("id", user_id).execute()

            # 2. 세션 및 user_metadata 동기화
            session['shipping_address'] = new_address
            if 'user' in session:
                session['user']['name'] = new_name
            session.modified = True

            access_token = session.get('access_token')
            if access_token:
                try:
                    supabase.auth.set_session(access_token, session.get('refresh_token', ''))
                    supabase.auth.update_user({
                        "data": {
                            "name": new_name,
                            "full_name": new_name,
                            "phone": new_phone,
                            "address": new_address
                        }
                    })
                except Exception:
                    pass

            flash("회원 정보가 성공적으로 수정되었습니다.", "success")
            return redirect(url_for('main.mypage'))

        except Exception as e:
            flash(f"회원 정보 수정 중 오류가 발생했습니다: {e}", "danger")
            return redirect(url_for('main.mypage'))

    # GET 요청 시 profiles 테이블에서 정보 조회
    profile = {
        'id': user_id,
        'email': user.get('email', ''),
        'full_name': user.get('name', '고객'),
        'phone': '',
        'address': session.get('shipping_address') or '',
        'grade': 'BRONZE',
        'total_spent': 0
    }

    try:
        profile_res = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if profile_res.data:
            p = profile_res.data[0]
            profile['full_name'] = p.get('full_name') or user.get('name', '고객')
            profile['email'] = p.get('email') or user.get('email', '')
            profile['phone'] = p.get('phone') or ''
            if p.get('address'):
                profile['address'] = p.get('address')
            profile['grade'] = p.get('grade') or 'BRONZE'
            profile['total_spent'] = p.get('total_spent', 0)
    except Exception as e:
        import logging
        logging.error(f"[Mypage Profile Fetch Error] {e}")

    return render_template(
        'mypage.html',
        user=user,
        profile=profile,
        cart_count=get_cart_count()
    )


@main_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """
    장바구니 상품을 기반으로 실제 주문(orders) 및 주문 품목(order_items) 스냅샷 생성
    """
    user_id = session.get('user_id')
    user = session.get('user') or {}
    raw_cart = session.get('cart', {})

    if not raw_cart:
        flash("장바구니가 비어 있어 주문을 진행할 수 없습니다.", "warning")
        return redirect(url_for('main.cart'))

    order_items_to_create = []
    total_amount = 0

    for pid_str, quantity in raw_cart.items():
        try:
            pid = int(pid_str)
        except ValueError:
            continue
        product = PRODUCT_DICT.get(pid)
        if product:
            price_int = int(product['price'].replace(',', ''))
            subtotal = price_int * quantity
            total_amount += subtotal
            order_items_to_create.append({
                "product_id": product['id'],
                "product_name": product['name'],
                "option_info": product.get('sub_desc') or '기본 옵션',
                "price": price_int,
                "quantity": quantity,
                "subtotal": subtotal
            })

    if not order_items_to_create:
        flash("주문 가능한 상품이 없습니다.", "danger")
        return redirect(url_for('main.cart'))

    shipping_fee = 0 if total_amount >= 50000 else 3000
    final_amount = total_amount + shipping_fee

    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    try:
        supabase = get_supabase_client()
        order_payload = {
            "order_number": order_number,
            "user_id": user_id,
            "status": "paid",  # 즉시 결제 완료 상태로 생성
            "total_amount": total_amount,
            "discount_amount": 0,
            "shipping_fee": shipping_fee,
            "final_amount": final_amount,
            "recipient_name": user.get('name') or '고객',
            "recipient_phone": "010-1234-5678",
            "shipping_address": "서울특별시 강남구 테헤란로 123 VIBE 빌딩 4층",
            "shipping_memo": "배송 전 연락 바랍니다.",
            "payment_method": "간편결제",
            "paid_at": datetime.utcnow().isoformat()
        }

        order_insert_res = supabase.table("orders").insert(order_payload).execute()
        if not order_insert_res.data:
            flash("주문 생성 중 오류가 발생했습니다. 다시 시도해주세요.", "danger")
            return redirect(url_for('main.cart'))

        created_order = order_insert_res.data[0]
        new_order_id = created_order["id"]

        for item in order_items_to_create:
            item["order_id"] = new_order_id

        supabase.table("order_items").insert(order_items_to_create).execute()

        # 장바구니 비우기
        session.pop('cart', None)
        session.modified = True

        flash(f"주문이 성공적으로 완료되었습니다! (주문번호: {order_number})", "success")
        return redirect(url_for('main.mypage'))

    except Exception as e:
        import logging
        logging.error(f"[Checkout Error] {e}")
        flash(f"주문 처리 중 오류가 발생했습니다: {e}", "danger")
        return redirect(url_for('main.cart'))


@main_bp.route('/orders/<order_id>/refund', methods=['POST'])
@login_required
def request_refund(order_id):
    """
    배송완료(delivered) 주문에 대해 환불 신청 생성 및 주문 상태를 refunded로 전환
    """
    user_id = session.get('user_id')
    reason = request.form.get('reason', '고객 변심 및 상품 불만족').strip()

    try:
        supabase = get_supabase_client()
        # 1. 해당 주문이 본인 주문이고 delivered 상태인지 확인
        order_res = supabase.table("orders").select("*").eq("id", order_id).eq("user_id", user_id).execute()
        if not order_res.data:
            flash("주문 정보를 찾을 수 없습니다.", "danger")
            return redirect(url_for('main.mypage'))

        order = order_res.data[0]
        if order.get("status") != "delivered":
            flash("환불 신청은 배송 완료(delivered) 상태의 주문만 가능합니다.", "warning")
            return redirect(url_for('main.mypage'))

        # 2. 이미 환불 신청이 존재하는지 확인
        refund_check = supabase.table("refunds").select("*").eq("order_id", order_id).execute()
        if refund_check.data:
            flash("이미 환불 처리가 접수된 주문입니다.", "info")
            return redirect(url_for('main.mypage'))

        # 3. refunds 레코드 생성
        refund_payload = {
            "order_id": order_id,
            "user_id": user_id,
            "status": "requested",
            "reason": reason,
            "refund_amount": order.get("final_amount", 0)
        }
        supabase.table("refunds").insert(refund_payload).execute()

        # 4. orders 상태를 refunded로 업데이트
        supabase.table("orders").update({"status": "refunded"}).eq("id", order_id).execute()

        flash(f"주문({order.get('order_number')})에 대한 환불 신청이 정상적으로 접수되었습니다.", "success")

    except Exception as e:
        import logging
        logging.error(f"[Refund Request Error] {e}")
        flash(f"환불 신청 처리 중 오류가 발생했습니다: {e}", "danger")

    return redirect(url_for('main.mypage'))


@main_bp.route('/delete-account', methods=['POST'])
def delete_account():
    """회원 탈퇴 처리"""
    user = session.get('user')
    name = user.get('name', '고객') if user else '고객'

    # 세션 데이터 완전 초기화 (로그인 정보, 장바구니 비우기)
    session.pop('user_id', None)
    session.pop('user', None)
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    session.pop('cart', None)

    flash(f"{name} 님의 회원 탈퇴가 안전하게 처리되었습니다. 그동안 VIBE-FASHION을 이용해주셔서 감사드립니다.", "info")
    return redirect(url_for('main.index'))


# ==============================================================================
# 장바구니 담기 / 수량 조절(갯수 추가) / 삭제 라우트
# ==============================================================================

@main_bp.route('/cart')
def cart():
    """장바구니 화면"""
    raw_cart = session.get('cart', {})
    cart_items = []
    total_price = 0
    total_count = 0

    for pid_str, quantity in raw_cart.items():
        try:
            pid = int(pid_str)
        except ValueError:
            continue

        product = PRODUCT_DICT.get(pid)
        if product:
            price_int = int(product['price'].replace(',', ''))
            subtotal = price_int * quantity
            total_price += subtotal
            total_count += quantity
            cart_items.append({
                'id': product['id'],
                'name': product['name'],
                'category': product['category'],
                'image': product['image'],
                'unit_price': price_int,
                'unit_price_formatted': product['price'],
                'quantity': quantity,
                'subtotal': subtotal
            })

    return render_template('cart.html', cart_items=cart_items, total_price=total_price, total_count=total_count)


@main_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """상품을 장바구니에 담기"""
    product = PRODUCT_DICT.get(product_id)
    if not product:
        flash("존재하지 않는 상품입니다.", "danger")
        return redirect(url_for('main.index'))

    cart = session.get('cart', {})
    pid_str = str(product_id)
    cart[pid_str] = cart.get(pid_str, 0) + 1
    session['cart'] = cart
    session.modified = True

    flash(f"[{product['name']}] 상품을 장바구니에 담았습니다! (수량: {cart[pid_str]}개)", "success")
    return redirect(request.referrer or url_for('main.cart'))


@main_bp.route('/cart/update/<int:product_id>/<action>', methods=['POST'])
def update_cart(product_id, action):
    """장바구니 수량 추가(증가), 감소 및 삭제"""
    cart = session.get('cart', {})
    pid_str = str(product_id)

    if pid_str in cart:
        if action == 'increase':
            cart[pid_str] += 1
            flash("상품 수량을 1개 추가했습니다.", "success")
        elif action == 'decrease':
            cart[pid_str] -= 1
            if cart[pid_str] <= 0:
                del cart[pid_str]
                flash("상품이 장바구니에서 삭제되었습니다.", "info")
            else:
                flash("상품 수량을 1개 줄였습니다.", "info")
        elif action == 'remove':
            del cart[pid_str]
            flash("상품이 장바구니에서 삭제되었습니다.", "info")

    session['cart'] = cart
    session.modified = True
    return redirect(url_for('main.cart'))


@main_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    """장바구니 전체 비우기"""
    session.pop('cart', None)
    flash("장바구니를 모두 비웠습니다.", "info")
    return redirect(url_for('main.cart'))


# ==============================================================================
# 문의사항 & 정책 라우트
# ==============================================================================

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    1:1 문의사항 및 고객센터 페이지 핸들러
    """
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        flash(f"{name} 님의 [{category}] 문의가 성공적으로 접수되었습니다. 확인 후 신속히 답변드리겠습니다.", "success")
        return redirect(url_for('main.contact'))

    return render_template('contact.html')


@main_bp.route('/refund-policy')
def refund_policy():
    """
    교환 및 환불정책 안내 페이지 핸들러
    """
    return render_template('refund_policy.html')
