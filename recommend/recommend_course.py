from connect_ai_db import search_db
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class RecommendRequest(BaseModel):
    hopeJob: str
    difficultyLevel: str
    techStacks: list[str]
    projectTitle: str
    projectSummary: str
    
    def get_sentences(self) -> list[str]:
        ret = []
        ret.append(self.hopeJob)
        ret.append(self.difficultyLevel)
        ret.extend(self.techStacks)
        ret.append(self.projectTitle)
        ret.append(self.projectSummary)

        return ret

origins = [
    "https://cpplab.store",
    "https://be.cpplab.store"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ai/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ai/recommend")
def recommend_course_endpoint(request: RecommendRequest):
    sentences = request.get_sentences()
    print("인풋데이터 : ", sentences)
    search_result = search_db(sentences)
    
    result = []
    for i in range(0, len(search_result), 2):
        result.append({
            "title": search_result[i],
            "url": search_result[i + 1]
        })

    return result

# uvicorn recommend_course:app --reload // 실행코드입니다