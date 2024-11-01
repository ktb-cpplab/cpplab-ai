import psycopg2
from embedding1 import get_embedding
from embedding2 import get_embedding2

def search_data(sentence):
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="localTest",
            user="postgres",
            password="psw"
        )
        cursor = connection.cursor()

        search_case = ['-','=','#','+']
        vec = get_embedding(sentence)

        for sc in search_case:
            query = f"""
            SELECT title, vec1 <{sc}> %s::vector AS similarity, summary
            FROM embedding3
            ORDER BY similarity
            LIMIT 5;
            """
            cursor.execute(query, (vec, ))

            results = cursor.fetchall()
            
            print(f"------------------------------   < {sc} >   ------------------------------")
            print(f"------------------------------   < {sc} >   ------------------------------")
            print(f"------------------------------   < {sc} >   ------------------------------")

            sum = 0
            for idx, row in enumerate(results, start=1):
                print(f"Top{idx}")
                print(f"Title     : {row[0]}")
                print(f"Summary   : {row[2]}")
                ##print(f"URL       : {row[1]}")
                print(f"Similarity: {row[1]}")

    except Exception as error:
        print("데이터베이스 작업 중 에러 발생:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("데이터베이스 연결이 종료되었습니다.")
