import psycopg2
from embedding_text_vec import SentenceEmbedding
import os

db_url = os.getenv("DB_URL")  # AWS ECS에서 제공하는 환경 변수

def create_db():
    try:
        connection = psycopg2.connect(db_url)
        
        cursor = connection.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS courseEntity (
            title TEXT,
            url TEXT,
            vec VECTOR(768)
        );
        """
        cursor.execute(query)
        connection.commit()
    except Exception as error:
        print("데이터베이스 생성 중 에러 발생:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def insert_db():
    try:
        connection_local = psycopg2.connect(db_url)
        connection_server = psycopg2.connect(db_url)

        cursor_local = connection_local.cursor()
        cursor_server = connection_server.cursor()

        query = """
            SELECT title, learning, target, difficulty, tech, url
            FROM embedding0
        """
        cursor_local.execute(query)
        results_local = cursor_local.fetchall()

        for row in results_local:
            title = row[0]
            learning = row[1]
            target = row[2]
            difficulty = row[3]
            tech = row[4]
            url = row[5]

            contents = [title, difficulty] + list(learning) + list(target) + list(tech)
            embeddingModel = SentenceEmbedding()
            vec = embeddingModel.get_mean_embedding(contents)

            query = """
                INSERT INTO courseEntity (title, url, vec)
                VALUES (%s, %s, %s)
            """
            data_to_insert = (title, url, vec)
            cursor_server.execute(query, data_to_insert)
            connection_server.commit()

        print("데이터가 성공적으로 삽입되었습니다.")
    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)
    finally:
        if connection_local:
            cursor_local.close()
            connection_local.close()
        if connection_server:
            cursor_server.close()
            connection_server.close()

def search_db(sentence):
    try:
        connection = psycopg2.connect(db_url)
        cursor = connection.cursor()
        embeddingModel = SentenceEmbedding()
        vec = embeddingModel.get_mean_embedding(sentence)

        query = """
        SELECT title, url, vec <#> %s::vector AS similarity
        FROM courseEntity
        ORDER BY similarity
        LIMIT 10;
        """
        cursor.execute(query, (vec, ))
        results = cursor.fetchall()

        ret = [(row[0], row[1]) for row in results]
        return ret
    except Exception as error:
        print("데이터 검색 중 에러 발생:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()