from pydantic import BaseModel, Field
from typing import List, Dict

class TaskStep(BaseModel):
    stepTitle: str = Field(description="각 단계의 제목")
    tasks: List[str] = Field(description="단계 내에서 수행할 작업 목록")

# 생성되는 프로젝트의 정보
class Project(BaseModel):
    title: str = Field(description="프로젝트의 제목")
    description: str = Field(description="프로젝트의 간단한 설명")
    techStacks: List[str] = Field(description="프로젝트에 사용되는 기술 스택 목록")
    difficultyLevel: str = Field(description="프로젝트의 난이도 수준 ('초급', '중급', '고급' 중 하나)")
    projectSummary: str = Field(description="프로젝트의 전체 요약")
    steps: List[TaskStep] = Field(description="프로젝트 진행 단계와 각 단계별 작업들")
    projectOptions: List[str] = Field(description= "후보 추천 프로젝트의 키워드")

# 재생성을 위한 정보
class RegenInfo(BaseModel):
    prev_project: Dict
    level: str
    projectOption: str
    domain: str
    stacks: List[str]