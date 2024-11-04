# uvicorn main:app --reload
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_teddynote import logging
from langchain import hub
logging.langsmith('cpplab_test')

prompt_gen_project = hub.pull("cpplab")
llm = ChatOpenAI(model="gpt-4o-mini") # 온도 튜닝
chain_gen_project = prompt_gen_project|llm
# print(prompt_gen_project)

app = FastAPI()

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

@app.get("/ai/health")
def health_check():
    return {"status": "healthy"}

@app.post('/ai/genproject')
def genProject(userinfo: UserInfo):
    proj = chain_gen_project.invoke(
        input = {
            "hopeJob": userinfo.hopeJob,
            "mainStack": userinfo.mainStack, 
            "educations": userinfo.educations, 
            "projects": userinfo.projects, 
            "prizes": userinfo.prizes,
            "activities": userinfo.activities,
            "certificates": userinfo.certificates,
            "language": "TEPS 404",
            "hopeCompany": userinfo.hopeCompany
        }
    )
    print(proj.content)
    return proj.content
