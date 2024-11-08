```
project/
│
├── main.py                # FastAPI 애플리케이션의 엔트리 포인트
├── models/                # Pydantic 모델을 저장하는 폴더
│   ├── __init__.py
│   ├── user_info.py       # UserInfo 및 관련 모델 정의
│   └── project_info.py    # Project, TaskStep, RegenInfo 등 모델 정의
├── services/              # 비즈니스 로직 및 체인을 포함하는 폴더
│   ├── __init__.py
│   ├── chain_generator.py # 체인 로직
│   └── helper.py          # 필요 시 추가적인 헬퍼 함수
└── config/                # 환경 설정 관련 파일
    └── settings.py
```