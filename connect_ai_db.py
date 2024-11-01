import psycopg2
from embedding_text_vec import SentenceEmbedding

# 데이터베이스 연결 함수
def connect_db():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="localTest",
            user="postgres",
            password="tlatkd22@@"
        )
        return connection
    except Exception as error:
        print("데이터베이스 연결 중 에러 발생:", error)
        return None

# 데이터 검색 함수
def search_db(connection, sentence):
    try:
        cursor = connection.cursor()
        vec = SentenceEmbedding.get_mean_embedding(sentence)  

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

# 데이터베이스 연결 종료 함수
def close_db(connection):
    if connection:
        connection.close()
        print("데이터베이스 연결이 종료되었습니다.")
