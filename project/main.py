# uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.user_info import UserInfo
from models.project_info import RegenInfo
from services.chain_generator import create_gen_chain, create_regen_chain
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_community.vectorstores.pgvector import DistanceStrategy
from langchain_openai import OpenAIEmbeddings
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

gen_chain = create_gen_chain()
regen_chain = create_regen_chain()

embeddings = OpenAIEmbeddings(model = "text-embedding-3-small") # 임베딩 모델 선언

conn = os.getenv('CLOUD_DB')
vectorstore = PGVector.from_existing_index( # db 연결
    embedding=embeddings,
    connection=conn,
    collection_name = 'cpplab_rag',
    distance_strategy=DistanceStrategy.COSINE,
    use_jsonb = True,
)

retriever = vectorstore.as_retriever( # 검색기 선언
    search_type = 'similarity',
    search_kwargs={"k": 5}
    )

@app.get("/ai/health")
def health_check():
    return {"status": "healthy"}

@app.post('/ai/genproject')
def genProject(userinfo: UserInfo):
    # userinfo를 문자열로 변환하여 검색 query로 사용
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

    # 검색된 문서에서 context 구성
    retrieved_docs = retriever.invoke(user_query)

    # 검색된 문서를 LLM 프롬프트에 전달할 context로 변환
    job_posting = "\n\n".join(
        f"Content: {doc.page_content}\nMetadata: {doc.metadata}"
        for doc in retrieved_docs
    )
    print(user_query)
    print(job_posting)

    proj = gen_chain.invoke(
        input={
            "hopeJob": userinfo.hopeJob,
            "mainStack": userinfo.mainStack,
            "educations": userinfo.educations,
            "projects": userinfo.projects,
            "prizes": userinfo.prizes,
            "activities": userinfo.activities,
            "certificates": userinfo.certificates,
            "hopeCompany": userinfo.hopeCompany,
            "job_posting": job_posting
        }
    )
    return proj

@app.post('/ai/regenproject')
def regenProject(regeninfo: RegenInfo):
    job_posting = "" # 공백 하드코딩
    proj = regen_chain.invoke(
        input={
            'prev_project': regeninfo.prev_project,
            'level': regeninfo.level,
            'projectOption': regeninfo.projectOption,
            'domain': regeninfo.domain,
            'stacks': regeninfo.stacks,
            'job_posting': job_posting
        }
    )
    return proj