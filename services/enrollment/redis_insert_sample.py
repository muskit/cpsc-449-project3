import redis 
from datetime import datetime
from redis import StrictRedis

# Connect to Redis
redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Sample data from SQL INSERT statements => userid, sectionid, position, date
sample_data = [
    (6, 11310, 1, '2023-09-15'),
    (6, 11312, 1, '2023-09-15'),
    (8, 11011, 1, '2023-09-15'),
    (9, 11310, 2, '2023-09-15'),
    (11, 11312, 2, '2023-09-15'),
    (12, 11310, 3, '2023-09-15'),
    (13, 11312, 3, '2023-09-15'),
    (14, 11312, 4, '2023-09-15'),
    (15, 11211, 1, '2023-09-15')
]

# Insert sample data into Redis
for user_id, section_id, position, date_str in sample_data:
    waitlist_key = f"waitlist:user_id:{user_id}:section_id:{section_id}"       #remember this is the key format
    
    # Check if the user is already in the waitlist for the section
    if redis.exists(waitlist_key):
        print(f"User {user_id} is already in the waitlist for section {section_id}")
    else:
        # Store additional information in a hash
        redis.hset(waitlist_key, "position", position)
        redis.hset(waitlist_key, "date", date_str)

# Display the stored data
for user_id, section_id, _, _ in sample_data:
    waitlist_key = f"waitlist:user_id:{user_id}:section_id:{section_id}"
    position = redis.hget(waitlist_key, "position")
    date = redis.hget(waitlist_key, "date")
    print(f"User {user_id} in section {section_id}: Position {position}, Date {date}")
