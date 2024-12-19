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
    print(f"세션 생성: {sessionId}", datetime.datetime.now().strftime('%H:%M:%S'))
    
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
    print(f"{sessionId}: 채용 공고 요약 완료")

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
    print(f"{sessionId}: 프로젝트 주제 생성 완료")

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
    print(f"{sessionId}: 전체 프로세스 종료 at {overall_end_time} (소요 시간: {elapsed_overall_time:.2f}초)")
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
