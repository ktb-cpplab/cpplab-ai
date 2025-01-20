# uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.user_info import *
from services.chain_generator import *
from services.helper import *
from services.session import *

from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_community.vectorstores.pgvector import DistanceStrategy

import os
import time
import datetime
import asyncio
import numpy as np

# from dotenv import load_dotenv
# load_dotenv()

from langchain_teddynote import logging
logging.langsmith("cpplab_test")

app = FastAPI()

origins = [
    "https://cpplab.store"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 체인 선언
theme_chain = gentheme_chain()
details_chain = gendetails_chain()
regen_chain = regendetails_chain()
summary_chain = jobposting_summary_chain()

# 임베딩 모델 선언
embeddings = OpenAIEmbeddings(model = "text-embedding-3-small") 

# vectordb 연결
# conn = os.getenv('LOCAL_DB')
conn = os.getenv('CLOUD_DB')
vectorstore = PGVector.from_existing_index(
    embedding=embeddings,
    connection=conn,
    collection_name = 'cpplab_rag',
    distance_strategy=DistanceStrategy.COSINE,
    use_jsonb = True,
)

# redis 연결, session 관리용
r = redis.Redis(
    # host='localhost',
    host=os.getenv('CLOUD_REDIS'),
    port=6379,
    password = 'cpplab11',
    db=0,
    decode_responses=True
)

# heatlth check endpoint
@app.get("/ai/health")
async def health_check():
    return {"status": "healthy"}

# update chain endpoint
@app.post("/ai/updatechain")
async def update_chain():
    global theme_chain, details_chain, regen_chain, summary_chain
    summary_chain = jobposting_summary_chain()
    theme_chain = gentheme_chain()
    details_chain = gendetails_chain()
    regen_chain = regendetails_chain()
    return {"message": "Chains updated successfully"}

# generate project endpoint
@app.post('/ai/genproject')
async def genProject(userinfo: UserInfo):
    # 시작 시간 기록
    overall_start_time = time.time()

    # 초기 프로젝트 생성 시 세션 생성
    sessionId = create_sessionId(redis_client=r)
    print(f"{sessionId}: 세션 생성, 현재 시각: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    # userinfo 파싱 후 query로 사용
    user_query = makeQuery(userinfo)

    # 유사한 채용공고 검색
    results_with_scores = searchJobposting(user_query, vectorstore, k=20)

    # 검색된 문서를 LLM 프롬프트에 전달할 context로 파싱
    job_posting = convert_to_context(results_with_scores)

    # 채용 공고 요약
    k = 20
    summarized_job_posting = await summary_chain.ainvoke(
        input={
            "k": k,
            # "rank": userinfo.rank,
            "hopeJob": userinfo.hopeJob,
            # "mainStack": userinfo.mainStack,
            # "educations": userinfo.educations,
            # "companies": userinfo.companies,
            # "projects": userinfo.projects,
            # "prizes": userinfo.prizes,
            # "activities": userinfo.activities,
            # "certificates": userinfo.certificates,
            "job_posting": job_posting
        }
    )
    print(f"{sessionId}: 채용 공고 요약 완로, 현재 시각: {datetime.datetime.now().strftime('%H:%M:%S')}")

    # 프로젝트 주제들 생성
    themes = await theme_chain.ainvoke(
        input={
            "rank": userinfo.rank,
            "hopeJob": userinfo.hopeJob,
            "mainStack": userinfo.mainStack,
            "educations": userinfo.educations,
            "companies": userinfo.companies,
            "projects": userinfo.projects,
            "prizes": userinfo.prizes,
            "activities": userinfo.activities,
            "certificates": userinfo.certificates,
            "hopeCompany": userinfo.hopeCompany,
            "job_posting": summarized_job_posting,
            'isRegen': False,
            'prev_theme': '' # 첫 프로젝트 생성이므로 빈 문자열
        }
    )
    print(f"{sessionId}: 프로젝트 주제 생성 완료, 현재 시각: {datetime.datetime.now().strftime('%H:%M:%S')}")

    # 프로젝트 tasks 생성
    res = await details_chain.ainvoke(
        input={
            "recommended_project": themes['themes'][0] # 첫 번째 주제 사용
        }
    )

    # redis에 초기 세션 데이터 저장
    data = parseData(userinfo, summarized_job_posting, themes, res)
    set_data(redis_client = r, key = sessionId, data = data)
    
    res["sessionId"] = sessionId # response에 sessionid 필드 추가
    res['projectOptions'] = [theme['title'] for theme in themes['themes'][1:]] # response에 projectOptions 필드 추가

    # 전체 프로세스 끝 시간 기록
    overall_end_time = time.time()
    elapsed_overall_time = overall_end_time - overall_start_time
    print(f"{sessionId}: 전체 프로세스 종료, 소요 시간: {elapsed_overall_time:.2f}초")
    return res

# regenerate project endpoint
@app.post('/ai/regenproject')
async def regenProject(regeninfo: RegenInfo):
    # sessionId와 일치하는 데이터 조회
    data = get_data(redis_client=r, key = regeninfo.sessionId)
    # print(f"{regeninfo.sessionId}: 데이터 조회 완료")

    # projectOptions에서 사용자가 선택한 projectOption 검색
    hope_theme = findTheme(data, regeninfo)
    # print(data['projectOptions'])
    # print(hope_theme)

    # prev_theme에 이전 프로젝트 주제 추가
    data['prev_theme'] += [theme['title'] for theme in data['projectOptions']]
    
    # 프로젝트 주제들 생성
    themes = await theme_chain.ainvoke(
        input={
            "rank": data['user_portfolio']['rank'],
            "hopeJob": data['user_portfolio']['hopeJob'],
            "mainStack": data['user_portfolio']['mainStack'],
            "educations": data['user_portfolio']['educations'],
            "companies": data['user_portfolio']['companies'],
            "projects": data['user_portfolio']['projects'],
            "prizes": data['user_portfolio']['prizes'],
            "activities": data['user_portfolio']['activities'],
            "certificates": data['user_portfolio']['certificates'],
            "hopeCompany": data['user_portfolio']['hopeCompany'],
            "job_posting": data['summarized_job_posting'],
            'isRegen': True,
            'prev_theme': data['prev_theme']
        }
    )
    print(f"{regeninfo.sessionId}: 프로젝트 주제 재생성 완료")

    # 프로젝트 tasks 생성
    res = await regen_chain.ainvoke(
        input={
            # 'portfolio': data['user_portfolio'],
            'prev_project': data['project'],
            'prev_theme': data['prev_theme'],
            'hopeLevel': regeninfo.hopeLevel,
            'hope_theme': hope_theme,
            'hopeStacks': regeninfo.hopeStacks
        }
    )
    print(f"{regeninfo.sessionId}: 프로젝트 tasks 재생성 완료")

    res['projectOptions'] = [theme['title'] for theme in themes['themes']] # response에 projectOptions 필드 추가
    res["sessionId"] = regeninfo.sessionId # response에 sessionid 필드 추가

    # redis에 데이터 업데이트
    data['projectOptions']  = [theme for theme in themes['themes']]
    set_data(redis_client = r, key = regeninfo.sessionId, data = data)
    return res

# delete session endpoint
@app.delete('/ai/delsession')
def deleteSession(session: Session):
    delete_sessionId(redis_client=r, key = session.sessionId)
    return {"message": "Session deleted successfully"}

# test generate project endpoint
@app.post('/ai/test/asyncgenproject')
async def asyncgenProject(userinfo: UserInfo):
    # 시작 시간 기록
    overall_start_time = time.time()

    # 초기 프로젝트 생성 시 세션 생성
    sessionId = create_sessionId(redis_client=r)
    print(f"세션 생성: {sessionId}", datetime.datetime.now().strftime('%H:%M:%S'))
    
    # userinfo 파싱 후 query로 사용
    user_query = makeQuery(userinfo)
    
    # 비동기 sleep 대체
    # 평균이 40초이고 표준편차가 10인 정규분포를 따르는 시간 대기
    await asyncio.sleep(np.random.normal(40, 10))

    # 테스트 데이터 하드코딩
    summarized_job_posting = {
  "responsibilities": [
    "AI 학습 모델 연구 개발(딥러닝)",
    "AI 신기술 기반 응용 모델 연구 개발 (학습, 인식, 인지, 탐지, 생성, 예측, 추천 등)",
    "차량, UAM, 로봇 등의 이동체 내/외부 AI 기반 서비스를 위한 딥러닝 기술 연구 개발 및 검증",
    "AI 신기술 대응, AI 기반 분석 도구, AI 기반 시스템 설계 및 개발, 실 서비스 모델 개발/적용 등"
  ],
  "qualifications": [
    "기계학습(딥러닝), 인공지능 전반에 대한 이론적, 기술적 이해",
    "확률 및 통계, 선형대수, 해석학 기반의 수학적 모델링에 대한 이해",
    "인공지능 기반의 다중 데이터(영상, 센서, 텍스트) 융합 상황이해, 예측 및 판단 핵심기술 구현을 위한 개발 역량",
    "영상-언어, 영상-센서 융합 딥러닝 모델(CNNs, RNNs, Transformer 등) 설계/개발 역량",
    "AI 신기술 평가 및 검증을 위한 실험 설계 및 실험 수행 역량",
    "원활한 협업을 위한 소프트스킬 보유"
  ],
  "preferred_qualifications": [
    "인공지능 관련 개발 지식/경험 보유 및 임베디드 경험",
    "멀티모달 퓨전, 강화학습, 생성형AI, LLM, Human-Robot Interaction 경험",
    "기계학습(딥러닝), 이동체(차량, 비행체, 로봇), 인공지능 관련 최신 논문 이해 및 기법 재 구현 능력",
    "인공지능, 기계학습, 컴퓨터비전, 자연어처리, 로봇 유관 주요 학회 및 저널 논문 저술 경험",
    "기계학습(딥러닝), 이동체(차량, 비행체, 로봇), 인공지능 관련 국내외 챌린지 입상 경력"
  ],
  "required_stacks": [
    "Python",
    "TensorFlow",
    "PyTorch",
    "OpenCV",
    "scikit-learn",
    "Keras"
  ]
}
    themes ={
  "themes": [
    {
      "title": "딥러닝 기반 영상-언어 융합 모델 개발",
      "description": "영상과 언어 데이터를 융합하여 이해하고, 이를 통해 다양한 응용 모델을 개발하는 프로젝트입니다. CNN과 RNN을 활용하여 영상과 텍스트의 관계를 분석합니다.",
      "projectgoal": "영상과 언어를 융합한 딥러닝 모델을 설계하여, 새로운 AI 기반 응용 모델을 개발하고 성능을 평가합니다.",
      "techStacks": ["Python", "PyTorch", "OpenCV", "TensorFlow"],
      "qualifications": [
        "기계학습(딥러닝), 인공지능 전반에 대한 이론적, 기술적 이해",
        "영상-언어 융합 딥러닝 모델 설계/개발 역량"
      ],
      "preferred_qualifications": [
        "인공지능 관련 개발 지식/경험 보유",
        "기계학습(딥러닝), 인공지능 관련 최신 논문 이해 및 기법 재 구현 능력"
      ],
      "userskillgaps": [
        "영상-언어 융합 딥러닝 모델(CNNs, RNNs) 설계/개발 역량",
        "실험 설계 및 실험 수행 역량"
      ]
    },
    {
      "title": "강화학습을 이용한 이동체 제어 모델 개발",
      "description": "강화학습 기법을 활용하여 이동체(차량, 로봇)의 제어 모델을 개발하는 프로젝트입니다. 다양한 환경에서의 자율주행을 목표로 합니다.",
      "projectgoal": "강화학습을 통해 자율주행 이동체의 제어 모델을 설계하고, 이를 검증하여 실제 환경에서의 성능을 평가합니다.",
      "techStacks": ["Python", "PyTorch", "TensorFlow", "scikit-learn"],
      "qualifications": [
        "AI 신기술 기반 응용 모델 연구 개발",
        "확률 및 통계, 선형대수 기반의 수학적 모델링에 대한 이해"
      ],
      "preferred_qualifications": [
        "멀티모달 퓨전, 강화학습 경험",
        "기계학습(딥러닝), 이동체 관련 최신 논문 이해 및 기법 재 구현 능력"
      ],
      "userskillgaps": [
        "강화학습을 활용한 모델 개발 역량",
        "AI 신기술 평가 및 검증을 위한 실험 설계 역량"
      ]
    },
    {
      "title": "AI 기반 차량 센서 데이터 분석 및 예측 시스템 개발",
      "description": "차량의 센서 데이터를 수집하고 분석하여 예측 모델을 개발하는 프로젝트입니다. 다양한 데이터 융합 기술을 활용하여 정확한 예측을 목표로 합니다.",
      "projectgoal": "차량 센서 데이터를 분석하고, 이를 통해 예측 모델을 개발하여 실제 상황에서의 적용 가능성을 검증합니다.",
      "techStacks": ["Python", "PyTorch", "MongoDB", "PostgreSQL"],
      "qualifications": [
        "AI 기반 분석 도구 설계 및 개발 역량",
        "인공지능 기반 다중 데이터 융합 상황이해"
      ],
      "preferred_qualifications": [
        "기계학습(딥러닝), 이동체 관련 국내외 챌린지 입상 경력",
        "기계학습(딥러닝), 인공지능 관련 최신 논문 이해 및 기법 재 구현 능력"
      ],
      "userskillgaps": [
        "다중 데이터(영상, 센서) 융합 핵심기술 구현 역량",
        "실험 설계 및 실험 수행 역량"
      ]
    },
    {
      "title": "자연어처리 기법을 활용한 AI 기반 추천 시스템 개발",
      "description": "자연어처리 기법을 활용하여 사용자 맞춤형 추천 시스템을 개발하는 프로젝트입니다. 사용자 데이터를 분석하고, 이를 기반으로 추천 알고리즘을 설계합니다.",
      "projectgoal": "사용자 데이터 분석을 통해 개인화된 추천 시스템을 개발하고, 성능을 평가하여 실제 서비스에 적용 가능성을 검증합니다.",
      "techStacks": ["Python", "PyTorch", "scikit-learn"],
      "qualifications": [
        "기계학습(딥러닝), 인공지능 전반에 대한 이론적, 기술적 이해",
        "AI 기반 분석 도구 설계 및 개발 역량"
      ],
      "preferred_qualifications": [
        "기계학습(딥러닝), 인공지능 관련 최신 논문 이해 및 기법 재 구현 능력",
        "인공지능, 기계학습, 자연어처리 관련 주요 학회 및 저널 논문 저술 경험"
      ],
      "userskillgaps": [
        "자연어처리 기법을 활용한 모델 개발 역량",
        "AI 신기술 평가 및 검증을 위한 실험 설계 역량"
      ]
    }
  ]
}
    res = {
  "title": "딥러닝 기반 영상-언어 융합 모델 개발",
  "description": "영상과 언어 데이터를 융합하여 이해하고, 이를 통해 다양한 응용 모델을 개발하는 프로젝트입니다. CNN과 RNN을 활용하여 영상과 텍스트의 관계를 분석합니다.",
  "techStacks": [
    "Python",
    "PyTorch",
    "OpenCV",
    "TensorFlow"
  ],
  "difficultyLevel": "중급",
  "projectSummary": "영상과 언어를 융합한 딥러닝 모델을 설계하여, 새로운 AI 기반 응용 모델을 개발하고 성능을 평가하는 프로젝트입니다.",
  "steps": [
    {
      "stepTitle": "1단계: 데이터 수집 및 전처리",
      "tasks": [
        "영상 데이터셋 수집하기 (예: YouTube API 활용하여 영상 다운로드)",
        "텍스트 데이터셋 수집하기 (예: 이미지 설명 데이터셋 수집)",
        "수집한 데이터 정리하기 (예: CSV 파일로 저장)",
        "영상 데이터 전처리하기 (예: OpenCV를 사용하여 영상 크기 조정 및 정규화)",
        "텍스트 데이터 전처리하기 (예: 자연어 처리 라이브러리(NLTK)로 토큰화 및 불용어 제거)"
      ]
    },
    {
      "stepTitle": "2단계: 모델 설계",
      "tasks": [
        "CNN 모델 아키텍처 설계하기 (예: ResNet 또는 VGG 기반으로 설계)",
        "RNN 모델 아키텍처 설계하기 (예: LSTM 또는 GRU 기반으로 설계)",
        "영상과 텍스트 융합을 위한 구조 설계하기 (예: Attention Mechanism 활용)",
        "모델의 하이퍼파라미터 설정하기 (예: 배치 크기, 학습률 등)",
        "모델 설계 문서 작성하기 (예: 각 구성 요소의 설명 포함)"
      ]
    },
    {
      "stepTitle": "3단계: 모델 구현",
      "tasks": [
        "PyTorch를 사용하여 CNN 모델 코드 작성하기 (예: torch.nn.Module 상속하여 구현)",
        "PyTorch를 사용하여 RNN 모델 코드 작성하기 (예: torch.nn.LSTM 클래스를 사용)",
        "두 모델을 연결하는 융합 모듈 코드 작성하기 (예: Concatenate 및 Dense Layer 추가)",
        "모델 학습을 위한 손실 함수 및 옵티마이저 정의하기 (예: CrossEntropyLoss, Adam)",
        "모델 구현 과정 문서화하기 (예: 코드 주석 및 설명 추가)"
      ]
    },
    {
      "stepTitle": "4단계: 모델 훈련",
      "tasks": [
        "훈련 데이터와 검증 데이터 분리하기 (예: 80% 훈련, 20% 검증)",
        "모델 훈련 코드 작성하기 (예: epoch 및 배치 처리 구현)",
        "훈련 중 성능 모니터링하기 (예: 손실 및 정확도 그래프 생성)",
        "훈련 완료 후 모델 저장하기 (예: torch.save() 사용)",
        "훈련 결과 분석하기 (예: confusion matrix 및 ROC curve 시각화)"
      ]
    },
    {
      "stepTitle": "5단계: 모델 평가",
      "tasks": [
        "테스트 데이터셋 준비하기 (예: 새로운 데이터셋 수집 또는 기존 데이터 활용)",
        "훈련된 모델을 테스트 데이터셋으로 평가하기 (예: accuracy, precision, recall 계산)",
        "모델 성능에 대한 보고서 작성하기 (예: 성능 분석 및 개선 방안 제시)",
        "비교 모델과 성능 비교하기 (예: 기존 모델과 결과 비교)",
        "최종 결과를 시각화하여 프레젠테이션 자료 준비하기"
      ]
    },
    {
      "stepTitle": "6단계: 응용 모델 개발",
      "tasks": [
        "개발한 모델을 활용한 응용 프로그램 아이디어 구상하기 (예: 영상 기반 질문 답변 시스템)",
        "응용 프로그램의 사용자 인터페이스 설계하기 (예: 웹 애플리케이션 UI/UX 설계)",
        "모델을 응용 프로그램에 통합하기 (예: Flask 또는 Django를 사용하여 API 구축)",
        "최종 프로젝트 발표 자료 준비하기 (예: 슬라이드 및 데모 준비)",
        "프로젝트 결과를 블로그나 GitHub에 공유하기"
      ]
    }
  ]
}


    # redis에 초기 세션 데이터 저장
    data = parseData(userinfo, summarized_job_posting, themes, res)
    set_data(redis_client = r, key = sessionId, data = data)
    
    res["sessionId"] = sessionId # response에 sessionid 필드 추가
    res['projectOptions'] = [theme['title'] for theme in themes['themes'][1:]] # response에 projectOptions 필드 추가

    # 전체 프로세스 끝 시간 기록
    overall_end_time = time.time()
    elapsed_overall_time = overall_end_time - overall_start_time
    print(f"{sessionId}: 전체 프로세스 종료 at {overall_end_time} (소요 시간: {elapsed_overall_time:.2f}초)")
    return res

# test generate project endpoint
@app.post('/ai/test/syncgenproject')
def syncgenProject(userinfo: UserInfo):
    # 시작 시간 기록
    overall_start_time = time.time()

    # 초기 프로젝트 생성 시 세션 생성
    sessionId = create_sessionId(redis_client=r)
    print(f"세션 생성: {sessionId}", datetime.datetime.now().strftime('%H:%M:%S'))
    
    # userinfo 파싱 후 query로 사용
    user_query = makeQuery(userinfo)
    
    # 동기 sleep 대체
    # 평균이 40초이고 표준편차가 10인 정규분포를 따르는 시간 대기
    time.sleep(np.random.normal(40, 10))

    # 테스트 데이터 하드코딩
    summarized_job_posting = {
  "responsibilities": [
    "AI 학습 모델 연구 개발(딥러닝)",
    "AI 신기술 기반 응용 모델 연구 개발 (학습, 인식, 인지, 탐지, 생성, 예측, 추천 등)",
    "차량, UAM, 로봇 등의 이동체 내/외부 AI 기반 서비스를 위한 딥러닝 기술 연구 개발 및 검증",
    "AI 신기술 대응, AI 기반 분석 도구, AI 기반 시스템 설계 및 개발, 실 서비스 모델 개발/적용 등"
  ],
  "qualifications": [
    "기계학습(딥러닝), 인공지능 전반에 대한 이론적, 기술적 이해",
    "확률 및 통계, 선형대수, 해석학 기반의 수학적 모델링에 대한 이해",
    "인공지능 기반의 다중 데이터(영상, 센서, 텍스트) 융합 상황이해, 예측 및 판단 핵심기술 구현을 위한 개발 역량",
    "영상-언어, 영상-센서 융합 딥러닝 모델(CNNs, RNNs, Transformer 등) 설계/개발 역량",
    "AI 신기술 평가 및 검증을 위한 실험 설계 및 실험 수행 역량",
    "원활한 협업을 위한 소프트스킬 보유"
  ],
  "preferred_qualifications": [
    "인공지능 관련 개발 지식/경험 보유 및 임베디드 경험",
    "멀티모달 퓨전, 강화학습, 생성형AI, LLM, Human-Robot Interaction 경험",
    "기계학습(딥러닝), 이동체(차량, 비행체, 로봇), 인공지능 관련 최신 논문 이해 및 기법 재 구현 능력",
    "인공지능, 기계학습, 컴퓨터비전, 자연어처리, 로봇 유관 주요 학회 및 저널 논문 저술 경험",
    "기계학습(딥러닝), 이동체(차량, 비행체, 로봇), 인공지능 관련 국내외 챌린지 입상 경력"
  ],
  "required_stacks": [
    "Python",
    "TensorFlow",
    "PyTorch",
    "OpenCV",
    "scikit-learn",
    "Keras"
  ]
}
    themes ={
  "themes": [
    {
      "title": "딥러닝 기반 영상-언어 융합 모델 개발",
      "description": "영상과 언어 데이터를 융합하여 이해하고, 이를 통해 다양한 응용 모델을 개발하는 프로젝트입니다. CNN과 RNN을 활용하여 영상과 텍스트의 관계를 분석합니다.",
      "projectgoal": "영상과 언어를 융합한 딥러닝 모델을 설계하여, 새로운 AI 기반 응용 모델을 개발하고 성능을 평가합니다.",
      "techStacks": ["Python", "PyTorch", "OpenCV", "TensorFlow"],
      "qualifications": [
        "기계학습(딥러닝), 인공지능 전반에 대한 이론적, 기술적 이해",
        "영상-언어 융합 딥러닝 모델 설계/개발 역량"
      ],
      "preferred_qualifications": [
        "인공지능 관련 개발 지식/경험 보유",
        "기계학습(딥러닝), 인공지능 관련 최신 논문 이해 및 기법 재 구현 능력"
      ],
      "userskillgaps": [
        "영상-언어 융합 딥러닝 모델(CNNs, RNNs) 설계/개발 역량",
        "실험 설계 및 실험 수행 역량"
      ]
    },
    {
      "title": "강화학습을 이용한 이동체 제어 모델 개발",
      "description": "강화학습 기법을 활용하여 이동체(차량, 로봇)의 제어 모델을 개발하는 프로젝트입니다. 다양한 환경에서의 자율주행을 목표로 합니다.",
      "projectgoal": "강화학습을 통해 자율주행 이동체의 제어 모델을 설계하고, 이를 검증하여 실제 환경에서의 성능을 평가합니다.",
      "techStacks": ["Python", "PyTorch", "TensorFlow", "scikit-learn"],
      "qualifications": [
        "AI 신기술 기반 응용 모델 연구 개발",
        "확률 및 통계, 선형대수 기반의 수학적 모델링에 대한 이해"
      ],
      "preferred_qualifications": [
        "멀티모달 퓨전, 강화학습 경험",
        "기계학습(딥러닝), 이동체 관련 최신 논문 이해 및 기법 재 구현 능력"
      ],
      "userskillgaps": [
        "강화학습을 활용한 모델 개발 역량",
        "AI 신기술 평가 및 검증을 위한 실험 설계 역량"
      ]
    },
    {
      "title": "AI 기반 차량 센서 데이터 분석 및 예측 시스템 개발",
      "description": "차량의 센서 데이터를 수집하고 분석하여 예측 모델을 개발하는 프로젝트입니다. 다양한 데이터 융합 기술을 활용하여 정확한 예측을 목표로 합니다.",
      "projectgoal": "차량 센서 데이터를 분석하고, 이를 통해 예측 모델을 개발하여 실제 상황에서의 적용 가능성을 검증합니다.",
      "techStacks": ["Python", "PyTorch", "MongoDB", "PostgreSQL"],
      "qualifications": [
        "AI 기반 분석 도구 설계 및 개발 역량",
        "인공지능 기반 다중 데이터 융합 상황이해"
      ],
      "preferred_qualifications": [
        "기계학습(딥러닝), 이동체 관련 국내외 챌린지 입상 경력",
        "기계학습(딥러닝), 인공지능 관련 최신 논문 이해 및 기법 재 구현 능력"
      ],
      "userskillgaps": [
        "다중 데이터(영상, 센서) 융합 핵심기술 구현 역량",
        "실험 설계 및 실험 수행 역량"
      ]
    },
    {
      "title": "자연어처리 기법을 활용한 AI 기반 추천 시스템 개발",
      "description": "자연어처리 기법을 활용하여 사용자 맞춤형 추천 시스템을 개발하는 프로젝트입니다. 사용자 데이터를 분석하고, 이를 기반으로 추천 알고리즘을 설계합니다.",
      "projectgoal": "사용자 데이터 분석을 통해 개인화된 추천 시스템을 개발하고, 성능을 평가하여 실제 서비스에 적용 가능성을 검증합니다.",
      "techStacks": ["Python", "PyTorch", "scikit-learn"],
      "qualifications": [
        "기계학습(딥러닝), 인공지능 전반에 대한 이론적, 기술적 이해",
        "AI 기반 분석 도구 설계 및 개발 역량"
      ],
      "preferred_qualifications": [
        "기계학습(딥러닝), 인공지능 관련 최신 논문 이해 및 기법 재 구현 능력",
        "인공지능, 기계학습, 자연어처리 관련 주요 학회 및 저널 논문 저술 경험"
      ],
      "userskillgaps": [
        "자연어처리 기법을 활용한 모델 개발 역량",
        "AI 신기술 평가 및 검증을 위한 실험 설계 역량"
      ]
    }
  ]
}
    res = {
  "title": "딥러닝 기반 영상-언어 융합 모델 개발",
  "description": "영상과 언어 데이터를 융합하여 이해하고, 이를 통해 다양한 응용 모델을 개발하는 프로젝트입니다. CNN과 RNN을 활용하여 영상과 텍스트의 관계를 분석합니다.",
  "techStacks": [
    "Python",
    "PyTorch",
    "OpenCV",
    "TensorFlow"
  ],
  "difficultyLevel": "중급",
  "projectSummary": "영상과 언어를 융합한 딥러닝 모델을 설계하여, 새로운 AI 기반 응용 모델을 개발하고 성능을 평가하는 프로젝트입니다.",
  "steps": [
    {
      "stepTitle": "1단계: 데이터 수집 및 전처리",
      "tasks": [
        "영상 데이터셋 수집하기 (예: YouTube API 활용하여 영상 다운로드)",
        "텍스트 데이터셋 수집하기 (예: 이미지 설명 데이터셋 수집)",
        "수집한 데이터 정리하기 (예: CSV 파일로 저장)",
        "영상 데이터 전처리하기 (예: OpenCV를 사용하여 영상 크기 조정 및 정규화)",
        "텍스트 데이터 전처리하기 (예: 자연어 처리 라이브러리(NLTK)로 토큰화 및 불용어 제거)"
      ]
    },
    {
      "stepTitle": "2단계: 모델 설계",
      "tasks": [
        "CNN 모델 아키텍처 설계하기 (예: ResNet 또는 VGG 기반으로 설계)",
        "RNN 모델 아키텍처 설계하기 (예: LSTM 또는 GRU 기반으로 설계)",
        "영상과 텍스트 융합을 위한 구조 설계하기 (예: Attention Mechanism 활용)",
        "모델의 하이퍼파라미터 설정하기 (예: 배치 크기, 학습률 등)",
        "모델 설계 문서 작성하기 (예: 각 구성 요소의 설명 포함)"
      ]
    },
    {
      "stepTitle": "3단계: 모델 구현",
      "tasks": [
        "PyTorch를 사용하여 CNN 모델 코드 작성하기 (예: torch.nn.Module 상속하여 구현)",
        "PyTorch를 사용하여 RNN 모델 코드 작성하기 (예: torch.nn.LSTM 클래스를 사용)",
        "두 모델을 연결하는 융합 모듈 코드 작성하기 (예: Concatenate 및 Dense Layer 추가)",
        "모델 학습을 위한 손실 함수 및 옵티마이저 정의하기 (예: CrossEntropyLoss, Adam)",
        "모델 구현 과정 문서화하기 (예: 코드 주석 및 설명 추가)"
      ]
    },
    {
      "stepTitle": "4단계: 모델 훈련",
      "tasks": [
        "훈련 데이터와 검증 데이터 분리하기 (예: 80% 훈련, 20% 검증)",
        "모델 훈련 코드 작성하기 (예: epoch 및 배치 처리 구현)",
        "훈련 중 성능 모니터링하기 (예: 손실 및 정확도 그래프 생성)",
        "훈련 완료 후 모델 저장하기 (예: torch.save() 사용)",
        "훈련 결과 분석하기 (예: confusion matrix 및 ROC curve 시각화)"
      ]
    },
    {
      "stepTitle": "5단계: 모델 평가",
      "tasks": [
        "테스트 데이터셋 준비하기 (예: 새로운 데이터셋 수집 또는 기존 데이터 활용)",
        "훈련된 모델을 테스트 데이터셋으로 평가하기 (예: accuracy, precision, recall 계산)",
        "모델 성능에 대한 보고서 작성하기 (예: 성능 분석 및 개선 방안 제시)",
        "비교 모델과 성능 비교하기 (예: 기존 모델과 결과 비교)",
        "최종 결과를 시각화하여 프레젠테이션 자료 준비하기"
      ]
    },
    {
      "stepTitle": "6단계: 응용 모델 개발",
      "tasks": [
        "개발한 모델을 활용한 응용 프로그램 아이디어 구상하기 (예: 영상 기반 질문 답변 시스템)",
        "응용 프로그램의 사용자 인터페이스 설계하기 (예: 웹 애플리케이션 UI/UX 설계)",
        "모델을 응용 프로그램에 통합하기 (예: Flask 또는 Django를 사용하여 API 구축)",
        "최종 프로젝트 발표 자료 준비하기 (예: 슬라이드 및 데모 준비)",
        "프로젝트 결과를 블로그나 GitHub에 공유하기"
      ]
    }
  ]
}
    # redis에 초기 세션 데이터 저장
    data = parseData(userinfo, summarized_job_posting, themes, res)
    set_data(redis_client = r, key = sessionId, data = data)
    
    res["sessionId"] = sessionId # response에 sessionid 필드 추가
    res['projectOptions'] = [theme['title'] for theme in themes['themes'][1:]] # response에 projectOptions 필드 추가

    # 전체 프로세스 끝 시간 기록
    overall_end_time = time.time()
    elapsed_overall_time = overall_end_time - overall_start_time
    print(f"{sessionId}: 전체 프로세스 종료 at {overall_end_time} (소요 시간: {elapsed_overall_time:.2f}초)")
    return res
