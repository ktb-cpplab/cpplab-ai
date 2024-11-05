import psycopg2
from embedding_text_vec import SentenceEmbedding
import os

db_url = os.getenv("DB_URL")

def create_db():
    try:
        connection = psycopg2.connect(db_url)
        
        cursor = connection.cursor()

        query = f"""
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

        # 테이블에 삽입할 데이터
        query = f"""
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

            contents = []
            contents.append(title)
            contents.append(difficulty)
            for l in learning:
                contents.append(l)
            for ta in target:
                contents.append(ta)
            for te in tech:
                contents.append(te)

            embeddingModel = SentenceEmbedding()
            vec = embeddingModel.get_mean_embedding(contents) 

            query = """
                    INSERT INTO courseEntity (title, url, vec)
                    VALUES (%s, %s, %s)
                    """

            data_to_insert = (title, url, vec)

            # 데이터 삽입 실행
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

        query = f"""
        SELECT title, url, vec <#> %s::vector AS similarity
        FROM courseEntity
        ORDER BY similarity
        LIMIT 10;
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

def update_db():
    try:
        connection = psycopg2.connect(db_url)

        cursor = connection.cursor()

        # 테이블에 삽입할 데이터
        query = f"""
            SELECT title, difficulty
            FROM embedding0
            """
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            title = row[0]
            difficulty = row[1]
            modified_difficulty = difficulty.rstrip("자")

            query = """
                    UPDATE embedding0
                    SET difficulty = %s
                    WHERE title = %s
                    """
            

            
            # 데이터 삽입 실행
            cursor.execute(query, (modified_difficulty, title))
            connection.commit()

        print("데이터가 성공적으로 삽입되었습니다.")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()  