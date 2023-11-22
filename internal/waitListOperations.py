from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from redis import StrictRedis
from pydantic import BaseModel

app = FastAPI()

# Connect to Redis
def get_redis_db():
    redis_client = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    return redis_client

class WaitlistItem(BaseModel):
    user_id: int
    section_id: int
    position: int
    date: str

# Endpoint to add a user to the waitlist
@app.post("/waitlist/")
async def add_to_waitlist(item: WaitlistItem, redis: StrictRedis = Depends(get_redis_db)):
    waitlist_key = f"waitlist:user_id:{item.user_id}:section_id:{item.section_id}"

    # Check if the user is already in the waitlist for the section
    if redis.exists(waitlist_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already in the waitlist for this section")

    # Store additional information in a hash
    redis.hset(waitlist_key, "position", item.position)
    redis.hset(waitlist_key, "date", item.date)

    return JSONResponse(content={"message": "User added to the waitlist"}, status_code=status.HTTP_201_CREATED)

# Endpoint to retrieve the waitlist for a section => Will return every entry for a section
@app.get("/waitlist/{section_id}", status_code=status.HTTP_200_OK)
async def get_waitlist(section_id: int, redis: StrictRedis = Depends(get_redis_db)):
    waitlist_keys = redis.keys(f"waitlist:user_id:*:section_id:{section_id}")
    
    waitlist_data = []
    for waitlist_key in waitlist_keys:
        user_id = int(waitlist_key.split(":")[2])
        position = int(redis.hget(waitlist_key, "position"))
        date = redis.hget(waitlist_key, "date")

        waitlist_data.append({"user_id": user_id, "position": position, "date": date})

    return {"section_id": section_id, "waitlist": waitlist_data}


@app.delete("/deleteFromWaitlist/{user_id}/{section_id}")
async def delete_from_waitlist(user_id:int, section_id:int, redis: StrictRedis = Depends(get_redis_db)):
    
    waitlist_key = f"waitlist:user_id:{user_id}:section_id:{section_id}"

    # Check if the field exists in the hash
    if not redis.exists(waitlist_key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Section '{section_id}' not found for user {user_id}")

    redis.delete(waitlist_key)

    return {"message": f"Section '{section_id}' deleted for user {user_id} from waitlist"}