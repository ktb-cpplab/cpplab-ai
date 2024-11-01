from embedding_text_vec import SentenceEmbedding
from connect_ai_db import search_db

def get_recommend_course(sentences):
    print("search_db 전 : ", sentences)
    search_result = search_db(sentences)
    print("json 변환 전 search_result", search_result)
    json_data = [{"title": search_result[i], "url": search_result[i + 1]} for i in range(0, len(search_result), 2)]
    print(json_data)

get_recommend_course(["C", "C++", "임베디드", "인공지능"])