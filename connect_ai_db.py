import psycopg2
from embedding_text_vec import SentenceEmbedding

# 데이터 삽입 함수 최초 한번 실행
def insert_db():
    try:
        # 데이터베이스에 연결
        connection_local = psycopg2.connect(
            host="localhost",       # 데이터베이스 호스트 주소
            database="localTest",  # 데이터베이스 이름
            user="postgres",    # 사용자 이름
            password="tlatkd22@@" # 비밀번호
        )

        connection_server = psycopg2.connect(
            host="localhost",       # 데이터베이스 호스트 주소
            database="localTest",  # 데이터베이스 이름
            user="postgres",    # 사용자 이름
            password="tlatkd22@@" # 비밀번호
        )

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

# 데이터 검색 함수
def search_db(sentence):
    try:
        connection = psycopg2.connect(
        host="localhost",       # 데이터베이스 호스트 주소
        database="localTest",  # 데이터베이스 이름
        user="postgres",    # 사용자 이름
        password="tlatkd22@@" # 비밀번호
        )
        
        cursor = connection.cursor()
        embeddingModel = SentenceEmbedding() 
        vec = embeddingModel.get_mean_embedding(sentence)  

        print("search_db에서 첫번째 vec : ", vec)

        query = f"""
        SELECT title, url, vec <#> %s::vector AS similarity
        FROM embedding3
        ORDER BY similarity
        LIMIT 3;
        """
        cursor.execute(query, (vec, ))
        results = cursor.fetchall()
        
        ret = []
        for row in results:
            ret.append(row[0])
            ret.append(row[1])

        print("search_db 리턴 전 ret : ", ret)

        return ret
        
    except Exception as error:
        print("데이터 검색 중 에러 발생:", error)
    
    finally:
        if connection:
            cursor.close()
            connection.close()


