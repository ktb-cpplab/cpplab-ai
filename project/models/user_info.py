from pydantic import BaseModel
from typing import List, Dict

# 생성을 위한 사용자 정보
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

# 재생성을 위한 정보
class RegenInfo(BaseModel):
    sessionId: str
    # portfolio: Dict
    # prev_project: Dict
    hopeLevel: str
    projectOption: str
    # domain: str
    hopeStacks: List[str]

# 세션 만료
class Session(BaseModel):
    sessionId: str