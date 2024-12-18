# uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.user_info import *
from services.chain_generator import *
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_community.vectorstores.pgvector import DistanceStrategy
from services.session import *
import os

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
conn = os.getenv('CLOUD_DB')
vectorstore = PGVector.from_existing_index(
    embedding=embeddings,
    connection=conn,
    collection_name = 'cpplab_rag',
    distance_strategy=DistanceStrategy.COSINE,
    use_jsonb = True,
)

# redis 연결, session 관리용
r = redis.StrictRedis(host=os.getenv('CLOUD_REDIS'), port=6379, password = 'cpplab11', db=0, decode_responses=True)

@app.get("/ai/health")
def health_check():
    return {"status": "healthy"}

# 일단 모든 체인 다 업데이트
@app.post("/ai/updatechain")
def update_chain():
    global theme_chain, details_chain, regen_chain, summary_chain
    summary_chain = jobposting_summary_chain()
    theme_chain = gentheme_chain()
    details_chain = gendetails_chain()
    regen_chain = regendetails_chain()

@app.post('/ai/genproject')
def genProject(userinfo: UserInfo):
    # 초기 프로젝트 생성 시 세션 생성
    sessionId = create_sessionId(redis_client=r)
    print(sessionId)

    # userinfo 파싱 후 query로 사용
    user_query = "\n".join([
        f"희망 직무: {userinfo.hopeJob}",
        f"주요 기술 스택: {', '.join(userinfo.mainStack)}",
        f"희망 회사: {', '.join(userinfo.hopeCompany)}",
        f"학력: {', '.join([f'{edu.university}({edu.department}) GPA: {edu.gpa}/{edu.gpaMax}' for edu in userinfo.educations])}",
        f"프로젝트 경험: {', '.join([proj.title for proj in userinfo.projects])}",
        f"수상 내역: {', '.join([prize.title for prize in userinfo.prizes])}",
        f"활동: {', '.join([activity.title for activity in userinfo.activities])}",
        f"보유 자격증: {', '.join([cert.certificateName for cert in userinfo.certificates])}"
    ])

    # 유사한 채용공고 검색
    k = 20 
    results_with_scores = vectorstore.similarity_search_with_score(user_query, k = k)

    # 검색된 문서를 LLM 프롬프트에 전달할 context로 변환
    job_posting = "\n\n".join(
        f"{doc.page_content}\n사용자와의 Cosine Distance: {score}"
        for doc, score in results_with_scores
    )
    
    # 채용 공고 요약
    summarized_job_posting = summary_chain.invoke(
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
    print(summarized_job_posting)

    # 프로젝트 주제들 생성
    themes = theme_chain.invoke(
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
            'isRegen': False
        }
    )
    # 첫 번째 주제 사용
    theme = themes['themes'][0]
    print(theme)

    # 프로젝트 tasks 생성
    proj = details_chain.invoke(
        input={
            "recommended_project": theme
        }
    )

    # redis에 초기 세션 데이터 저장
    data = {}
    # data["session_Id"] = session_Id
    data['user_portfolio'] = userinfo.model_dump()
    data['summarized_job_posting'] = summarized_job_posting
    data['theme'] = theme
    data['project'] = proj
    data['regenCount'] = 0
    data['projectOptions'] = [theme for theme in themes['themes'][1:]]
    print(sessionId)
    set_data(redis_client = r, key = sessionId, data = data)
    
    # response에 sessionid 필드 추가
    proj["sessionId"] = sessionId

    # response에 projectOptions 필드 추가
    proj['projectOptions'] = [theme['title'] for theme in themes['themes'][1:]]
    return proj

@app.post('/ai/regenproject')
def regenProject(regeninfo: RegenInfo):
    # sessionId와 일치하는 데이터 조회
    data = get_data(redis_client=r, key = regeninfo.sessionId)
    print(data)
    
    # 재생성 횟수 증가
    data['regenCount'] += 1

    # projectOptions에서 사용자가 선택한 projectOption 검색
    for i in data['projectOptions']:
        print('\n')
        print(i['title'])
        if i['title'] == regeninfo.projectOption:
            hope_theme = i

    proj = regen_chain.invoke(
        input={
            # 'portfolio': data['user_portfolio'],
            'prev_project': data['project'],
            'hopeLevel': regeninfo.hopeLevel,
            'hope_theme': hope_theme,
            'hopeStacks': regeninfo.hopeStacks
        }
    )
    return proj

@app.delete('/ai/delsession')
def deleteSession(sessionId: Session):
    delete_sessionId(redis_client=r, key = sessionId)
