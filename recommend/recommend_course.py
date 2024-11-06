from embedding_text_vec import SentenceEmbedding
from connect_ai_db import search_db
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RecommendRequest(BaseModel):
    job: str
    level: str
    stack: list[str]
    subject: str
    summary: str

    def get_sentences(self) -> list[str]:
        ret = []
        ret.append(self.job)
        ret.append(self.level)
        ret.extend(self.stack)
        ret.append(self.subject)
        ret.append(self.summary)

        return ret

@app.get("/ai/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ai/recommend")
def recommend_course_endpoint(request: RecommendRequest):
    sentences = request.get_sentences()
    search_result = search_db(sentences)
    
    result = []
    for i in range(0, len(search_result), 2):
        result.append({
            "title": search_result[i],
            "url": search_result[i + 1]
        })

    return result

# uvicorn recommend_course:app --reload // 실행코드입니다