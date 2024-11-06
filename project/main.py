# uvicorn main:app --reload
from fastapi import FastAPI
from pydantic import BaseModel, Field, constr
from typing import List, Optional

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_teddynote import logging
from langchain import hub
logging.langsmith('cpplab_test')

# 프로젝트 생성
# 프로젝트 생성 input class
class Activity(BaseModel):
    title: str
    description: str
    startDate: str
    endDate: str

class Certificate(BaseModel):
    certificateName: str
    date: str

class Company(BaseModel):
    company: str
    job: str
    startDate: str
    endDate: str

class Education(BaseModel):
    university: str
    department: str
    gpa: float
    gpaMax: float

class Prize(BaseModel):
    title: str
    description: str
    date: str

class Project(BaseModel):
    title: str
    description: str
    stacks: List[str]

class UserInfo(BaseModel):
    rank: str
    mainStack: List[str]
    hopeCompany: List[str]
    hopeJob: str
    activities: List[Activity]
    certificates: List[Certificate]
    companies: List[Company]
    educations: List[Education]
    prizes: List[Prize]
    projects: List[Project]

# 프로젝트 생성 및 재생성 output class
class TaskStep(BaseModel):
    stepTitle: str = Field(description="각 단계의 제목")
    tasks: List[str] = Field(description="단계 내에서 수행할 작업 목록")

class Project(BaseModel):
    title: str = Field(description="프로젝트의 제목")
    description: str = Field(description="프로젝트의 간단한 설명")
    techStacks: List[str] = Field(description="프로젝트에 사용되는 기술 스택 목록")
    difficultyLevel: str = Field(description="프로젝트의 난이도 수준 ('초급', '중급', '고급' 중 하나)")
    projectSummary: str = Field(description="프로젝트의 전체 요약")
    steps: List[TaskStep] = Field(description="프로젝트 진행 단계와 각 단계별 작업들")

# 프로젝트 재생성
# 프로젝트 재생성 input class
class RegenInfo(BaseModel):
    prev_project: str
    level: str
    theme: str
    domain: str
    stacks: List[str]

# 공통 json parser
parser = JsonOutputParser(pydantic_object=Project)

# 프로젝트 생성 chain(prompt, llm, parser)
gen_prompt = hub.pull("cpplab")
gen_llm = ChatOpenAI(model="gpt-4o-mini") # 온도 튜닝
gen_prompt = gen_prompt.partial(format_instructions=parser.get_format_instructions())
gen_chain = gen_prompt|gen_llm|parser

# 프로젝트 재생성 chain(prompt, llm, parser)
regen_prompt = hub.pull("regen_prompt")
regen_llm = ChatOpenAI(model="gpt-4o-mini") # 온도 튜닝
regen_prompt = regen_prompt.partial(format_instructions=parser.get_format_instructions())
regen_chain = regen_prompt|regen_llm|parser

app = FastAPI()


@app.post('/ai/genproject')
def genProject(userinfo: UserInfo):
    proj = gen_chain.invoke(
        input = {
            "hopeJob": userinfo.hopeJob,
            "mainStack": userinfo.mainStack, 
            "educations": userinfo.educations, 
            "projects": userinfo.projects, 
            "prizes": userinfo.prizes,
            "activities": userinfo.activities,
            "certificates": userinfo.certificates,
            "language": "TEPS 404", # hard coding
            "hopeCompany": userinfo.hopeCompany
        }
    )
    print(proj)
    return proj

@app.post('/ai/regenproject')
def regenProject(regeninfo: RegenInfo):
    proj = regen_chain.invoke(
        input = {
            'prev_project': regeninfo.prev_project,
            'level': regeninfo.level,
            'theme': regeninfo.theme,
            'domain': regeninfo.domain,
            'stacks': regeninfo.stacks
        }
    )
    print(proj)
    return proj