import os
from flask import Flask
from dotenv import load_dotenv

# .env 파일에 정의된 환경 변수 불러오기
load_dotenv()

def create_app():
    """
    [앱 팩토리 함수]
    Flask 애플리케이션 객체를 생성하고 설정하는 함수입니다.
    애플리케이션을 여러 인스턴스로 생성하거나 테스트할 때 매우 유용한 구조입니다.
    """
    # 1. Flask 애플리케이션 객체 생성
    #    instance_relative_config=True 설정 시 인스턴스 폴더 기준 설정 파일 로딩 가능
    app = Flask(__name__)

    # 2. 기본 보안 및 앱 설정
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-secret-key-1234')

    # 3. 블루프린트(Blueprint) 등록
    #    각 라우트(URL 경로)를 기능별로 분리 관리하기 위해 블루프린트를 등록합니다.
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
