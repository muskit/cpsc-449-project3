import redis

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status
from fastapi import Depends
import redis


class Waitlist(BaseModel):
    user_id: int
    section: str  # Assuming Section is a string field
    position: int

# Sample data for Waitlist can be edit later 
sample_data = [
    {"user_id": 1, "section": "A", "position": 1},
    {"user_id": 2, "section": "B", "position": 2},
    {"user_id": 3, "section": "C", "position": 3},
    {"user_id": 4, "section": "A", "position": 4},
    {"user_id": 5, "section": "B", "position": 5}
]

def get_redis_db():
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    return redis_client

redisClient = get_redis_db()
for data in sample_data:
    key = f'user:{data["user_id"]}:{data["section"]}'   #use this keep user id and section as unique constraint
    redisClient.hmset(key, {'position': str(data["position"])})


#creating end points
app = FastAPI()


@app.post("/insertIntoWaitlist")
async def insert_user_in_Waitlist(user_data: Waitlist, redis_client: redis.StrictRedis = Depends(get_redis_db)):
    key = f"user:{user_data.user_id}"

    if redis_client.exists(key):
        raise HTTPException(status_code=400, detail=f"Entry for user {user_data.user_id} and section { user_data.section} already exists.")

    redis_client.hmset(key, {'position': str(user_data.position)})
    return {"Data": "Inserted User Successfully"}

@app.delete("/deleteFromWaitlist/{user_id}/{section}")
async def delete_from_waitlist(user_id:int, section:str, redis_client: redis.StrictRedis = Depends(get_redis_db)):
    
    key = f"user:{user_id}"

    # Check if the field exists in the hash
    if not redis_client.exists(key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field '{section}' not found for user {user_id}")

    redis_client.delete(key)

    return {"message": f"Section '{section}' deleted for user {user_id} in Redis"}

# Sample data retrieval route
@app.get("/get-data/{user_id}/{section}")
def get_data(user_id: int, section: str, redis_client: redis.StrictRedis = Depends(get_redis_db)):
    key = f"user:{user_id}:{section}"

    # Check if the key exists
    if not redis_client.exists(key):
        raise HTTPException(status_code=404, detail=f"Entry not found for user {user_id} with section {section}")

    # Retrieve all fields and values from the hash
    data = redis_client.hgetall(key)

    # Print information for debugging
    print(f"Key: {key}, Hash Data: {data}")

    # Decode byte values to strings
    data = {k.decode(): v.decode() for k, v in data.items()}

    return {"User Id": user_id, "Section": section, "Position": data['position']}
