import psycopg2
from embedding_text_vec import SentenceEmbedding
import os
# from dotenv import load_dotenv

# load_dotenv()

db_url = os.getenv("DB_URL")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

def search_db(sentence):
    try:
        connection = psycopg2.connect(
            host = db_url,
            database = db_name,
            user = db_user,
            password = db_password,
            port = db_port
        )
        cursor = connection.cursor()
        embeddingModel = SentenceEmbedding() 
        vec = embeddingModel.get_mean_embedding(sentence)  

        query = f"""
        SELECT title, url, vec <#> %s::vector AS similarity
        FROM courseEntity
        ORDER BY similarity
        LIMIT 3;
        """
        cursor.execute(query, (vec, ))
        results = cursor.fetchall()
        
        ret = []
        for row in results:
            ret.append(row[0])
            ret.append(row[1])

        return ret
        
    except Exception as error:
        print("데이터 검색 중 에러 발생:", error)
    
    finally:
        if connection:
            cursor.close()
            connection.close()
        else:
            print("데이터 베이스 연결에 실패했습니다")