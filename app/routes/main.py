from flask import Blueprint, render_template

# 'main'이라는 이름의 블루프린트 생성
# URL 프리픽스 없이 루트('/') 경로 등 메인 화면을 담당합니다.
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    메인 페이지 핸들러 함수:
    쇼핑몰 홈 화면에 보여줄 상품 목록을 정의하고
    index.html 템플릿에 전달하여 렌더링합니다.
    """
    # Unsplash 및 쥬얼리 컬렉션 기반 고해상도 상품 데이터
    products = [
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
        # --- 악세사리 (귀걸이, 반지) ---
        {
            "id": 5,
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
            "id": 6,
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
            "id": 7,
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
            "id": 8,
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
            "id": 9,
            "name": "오버핏 미니멀 블레이저",
            "category": "OUTER",
            "badge": "BEST",
            "price": "129,000",
            "original_price": None,
            "sub_desc": "트렌디한 오버핏 / 고밀도 원단",
            "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80",
            "description": "어떤 룩에도 자연스럽게 어우러지는 트렌디한 오버핏 실루엣 블레이저"
        }
    ]

    # HTML 템플릿으로 상품 목록 데이터 전달
    return render_template('index.html', products=products)
