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
    # Unsplash 기반 감각적인 고해상도 패션 및 악세사리/잡화 이미지 상품 데이터
    products = [
        {
            "id": 1,
            "name": "오버핏 미니멀 블레이저",
            "category": "OUTER",
            "price": "129,000",
            "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80",
            "description": "어떤 룩에도 자연스럽게 어우러지는 트렌디한 오버핏 실루엣 블레이저"
        },
        {
            "id": 2,
            "name": "클래식 레더 바이커 자켓",
            "category": "OUTER",
            "price": "189,000",
            "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80",
            "description": "고급스러운 질감과 핏을 살린 시크한 무드의 레더 바이커 자켓"
        },
        {
            "id": 3,
            "name": "와이드 빈티지 데님 팬츠",
            "category": "PANTS",
            "price": "79,000",
            "image": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&auto=format&fit=crop&q=80",
            "description": "자연스러운 워싱과 편안한 착용감을 선사하는 와이드 스트레이트 핏 데님"
        },
        {
            "id": 4,
            "name": "캐시미어 블렌드 크루넥 니트",
            "category": "TOP",
            "price": "95,000",
            "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&auto=format&fit=crop&q=80",
            "description": "부드러운 터치감과 따뜻한 보온성을 자랑하는 프리미엄 캐시미어 니트"
        },
        {
            "id": 5,
            "name": "클래식 레더 더비 슈즈",
            "category": "SHOES",
            "price": "145,000",
            "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80",
            "description": "미니멀한 실루엣과 편안한 쿠셔닝을 갖춘 데일리 천연 소가죽 슈즈"
        },
        {
            "id": 6,
            "name": "레트로 미니멀 크로스백",
            "category": "BAG",
            "price": "89,000",
            "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&auto=format&fit=crop&q=80",
            "description": "탄탄한 가죽 소재와 실용적인 수납력을 자랑하는 미니멀 크로스백"
        },
        {
            "id": 7,
            "name": "14K 골드 도금 볼드 드롭 귀걸이",
            "category": "ACC",
            "price": "32,000",
            "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&auto=format&fit=crop&q=80",
            "description": "은은한 골드 광택과 감각적인 곡선이 돋보이는 모던 드롭 이어링"
        },
        {
            "id": 8,
            "name": "레이어드 실버 체인 목걸이",
            "category": "ACC",
            "price": "38,000",
            "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80",
            "description": "모던한 두 줄 레이어드로 다양한 스타일에 포인트가 되는 실버 네크리스"
        },
        {
            "id": 9,
            "name": "빈티지 실버 925 와이드 링 (반지)",
            "category": "ACC",
            "price": "29,000",
            "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&auto=format&fit=crop&q=80",
            "description": "볼드하면서도 감성적인 텍스처를 살린 핸드메이드 실버 925 링"
        }
    ]

    # HTML 템플릿으로 상품 목록 데이터 전달
    return render_template('index.html', products=products)
