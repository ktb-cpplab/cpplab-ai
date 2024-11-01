from embedding_text_vec import SentenceEmbedding
from connect_ai_db import search_db

def get_recommend_course(sentences):
    search_result = search_db(sentences)
    json_data = [{"title": search_result[i], "url": search_result[i + 1]} for i in range(0, len(search_result), 2)]
    # {"title" : , "url" : }의 형태로 1,2,3위 반환
    return json_data