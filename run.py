"""
VIBE-FASHION 실행 엔트리포인트 스크립트
앱 팩토리 패턴(create_app)을 사용하여 Flask 애플리케이션을 생성하고 실행합니다.
"""

from app import create_app

# create_app() 함수를 호출하여 Flask 앱 인스턴스 생성
app = create_app()

if __name__ == '__main__':
    # 개발 모드(debug=True)로 5000번 포트에서 서버 실행
    # 코드 변경 시 자동으로 서버가 재시작되어 개발 편의성을 높입니다.
    app.run(host='127.0.0.1', port=5000, debug=True)
