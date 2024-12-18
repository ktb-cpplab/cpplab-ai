import redis
import json
import uuid

def create_sessionId(redis_client, ttl: int = 3600) -> str:
    sessionId = str(uuid.uuid4())
    
    data = {}

    # 데이터를 JSON 직렬화해서 Redis에 저장하고 TTL 설정
    redis_client.setex(sessionId, ttl, json.dumps(data, ensure_ascii=False))

    return sessionId

def set_data(redis_client, key: str, data: dict, ttl: int = 3600):
    json_dict = json.dumps(data, ensure_ascii=False)
    redis_client.setex(key, ttl, json_dict)


def get_data(redis_client, key:str) -> dict:
    json_dict = redis_client.get(key)
    return json.loads(json_dict)

def delete_sessionId(redis_client, key: str):
    redis_client.delete(key)

