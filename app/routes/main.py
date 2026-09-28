from flask import Blueprint, render_template

# 'main'이라는 이름의 블루프린트 생성
# URL 프리픽스 없이 루트('/') 경로 등 메인 화면을 담당합니다.
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    메인 페이지 핸들러 함수:
    쇼핑몰 홈 화면에 보여줄 더미 상품 목록 4개를 정의하고
    index.html 템플릿에 전달하여 렌더링합니다.
    """
    # Unsplash 기반 감각적인 고해상도 패션 룩북 이미지 4개 데이터
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
        }
    ]

    # HTML 템플릿으로 상품 목록 데이터 전달
    return render_template('index.html', products=products)
