from typing import Generator
import boto3
from boto3.dynamodb.conditions import Key, Attr
from pydantic_settings import BaseSettings
from fastapi.routing import APIRoute
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from internal.jwt_claims import require_x_roles, require_x_user
from redis import Redis

from internal.database_dynamo import get_db
from .model_requests import *
from .models import *

app = FastAPI()

# Connect to Redis
def get_redis_db() -> Generator[Redis, None, None]:
    redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)
    return redis_client

@app.get("/courses")
def list_courses(
    db: boto3.session.Session = Depends(get_db),
):
    table = db.Table('Courses').scan()['Items']
    return {'courses': table}

@app.get("/courses/{course_code}")
def get_course(
    course_id: str,
    db: boto3.session.Session = Depends(get_db),
):
    table = db.Table('Courses')
    response = table.query(
        KeyConditionExpression=Key('course_id').eq(course_id)
    )

    items = response.get('Items',[])
    
    if not items:
        raise HTTPException(status_code=404, detail="Course not found")
    else:
        return {'response': items}

@app.get("/sections")
def list_sections(
    db: boto3.session.Session = Depends(get_db),
):
    table = db.Table('Sections').scan()['Items']
    return {'Sections': table}


@app.get("/sections/{section_id}")
def get_section(
    section_id: int,
    db: boto3.session.Session = Depends(get_db),
):
    table = db.Table('Sections')
    response = table.query(
        KeyConditionExpression=Key('section_id').eq(section_id)
    )

    items = response.get('Items',[])
    
    if not items:
        raise HTTPException(status_code=404, detail="Section not found")
    else:
        return {'response': items}


@app.get("/sections/{section_id}/enrollments")
def list_section_enrollments(
    section_id: int,
    db: boto3.session.Session = Depends(get_db),
):
    table = db.Table('Enrollments')
    response = table.query(
        KeyConditionExpression=Key('section_id').eq(section_id)
    )

    items = response.get('Items',[])
    
    if not items:
        raise HTTPException(status_code=404, detail="Enrollmet reccords not found")
    else:
        return {'response': items}

# Endpoint to retrieve the waitlist for a section => Will return every entry for a section
@app.get("/sections/{section_id}/waitlist", status_code=status.HTTP_200_OK)
async def list_section_waitlist(section_id: int, redis: Redis = Depends(get_redis_db)):
    waitlist_keys = redis.keys(f"waitlist:user_id:*:section_id:{section_id}")
    
    waitlist_data = []
    for waitlist_key in waitlist_keys:
        user_id = int(waitlist_key.split(":")[2])
        position = int(redis.hget(waitlist_key, "position"))
        date = redis.hget(waitlist_key, "date")

        waitlist_data.append({"user_id": user_id, "position": position, "date": date})

    if len(waitlist_data) ==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given Section Id doesnt exist")

    return {"section_id": section_id, "waitlist": waitlist_data}

# lists the courses the student is enrolled in
@app.get("/users/{user_id}/enrollments")
def list_user_enrollments(
    student_id: int,
    status=EnrollmentStatus.ENROLLED,
    db: boto3.session.Session = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
):
    if Role.REGISTRAR not in jwt_roles and jwt_user != student_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    table = db.Table('Enrollments')
    response = table.scan(
        FilterExpression='student_id = :student_id',
        ExpressionAttributeValues={':student_id': student_id}
    )

    items = response.get('Items',[])
    
    if not items:
        raise HTTPException(status_code=404, detail= "No enrollments found for:" + str(student_id))
    else:
        return {'response': items}


@app.get("/users/{user_id}/enrollments")
def list_user_sections(
    user_id: int,
    type: ListUserSectionsType = ListUserSectionsType.ALL,
    db: boto3.session.Session = Depends(get_db),
):
    table_name = 'Enrollments'
    table = db.resource('dynamodb').Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('student_id').eq(user_id),
        FilterExpression=Attr('status').eq('enrolled')
    )

    items = response.get('Items', [])
    
    if not items:
        raise HTTPException(status_code=404, detail="No enrolled students found for the section")
    else:
        return {'enrolled_students': items}

@app.get("/users/{user_id}/waitlist")
def list_user_waitlist(
    user_id: int,
    redis = Depends(get_redis_db),
) -> ListUserWaitlistResponse:
    waitlist_keys = redis.keys(f"waitlist:user_id:{user_id}:section_id:*")
    
    user_waitlist_data = []
    for waitlist_key in waitlist_keys:
        section_id = int(waitlist_key.split(":")[4])
        position = int(redis.hget(waitlist_key, "position"))
        date = redis.hget(waitlist_key, "date")

        user_waitlist_data.append({"section_id": section_id, "position": position, "date": date})

    if len(user_waitlist_data) ==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Doesn't Exist")

    return {"user_id": user_id, "user_waitlist": user_waitlist_data}


@app.post("/users/{user_id}/enrollments")  # student attempt to enroll in class
def create_enrollment(
    user_id: int,
    enrollment: CreateEnrollmentRequest,
    db: boto3.session.Session = Depends(get_db),
    redis: Redis = Depends(get_redis_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> CreateEnrollmentResponse:

    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # DynamoDB table
    enrollment_table = db.Table('Enrollments')
    section_table = db.Table('Sections')

    section_id = enrollment.section

    # Verify that the class still has space.
    section_data = section_table.get_item(Key={'section_id' : section_id})

    enrollment_count = section_enrollment_count(db, section_id)
    waitlist_key = None

    if (
        section_data.get('Item') and
        section_data['Item']['capacity'] > enrollment_count and
        not section_data['Item']['freeze'] and
        not section_data['Item']['deleted']
    ):
        # If there is space, enroll the student.
        enrollment_table.put_item(
            Item=Enrollment(
                student_id=user_id,
                section_id=section_id,
                enrollment_status=EnrollmentStatus.ENROLLED
            ).model_dump()
        )
    else:
        # Otherwise, try to add them to the waitlist
        
        # TODO: use Redis
        # Check redis_insert_sample.py for reference
        waitlist_key = redis.keys(f"waitlist:*section_id:{section_id}")
        print(waitlist_key)
        waitlist_size = len(waitlist_key)

        if (
            section_data.get('Item') and
            section_data['Item']['waitlist_capacity'] > waitlist_size and
            not section_data['Item']['freeze'] and
            not section_data['Item']['deleted']
        ):
            # Add user to the waitlist
            waitlist_position = redis.zcard(waitlist_key) + 1
            redis.zadd(waitlist_key, {user_id: waitlist_position})

        else:
            raise HTTPException(
                status_code = 400,
                detail = "Section is full and waitlist is full.",
            )
    # Retrieve and return enrollment details
    enrollment_data = enrollment_table.get_item(Key={'student_id': user_id, 'section_id' : section_id})
    waitlist_position = redis.zrank(waitlist_key, user_id) if waitlist_key is not None else -1

    return CreateEnrollmentResponse(
        **enrollment_data.get('Item', {}),
        waitlist_position = waitlist_position,
    )

@app.post("/courses")
def add_course(
    course: AddCourseRequest,
    db: boto3.session.Session = Depends(get_db),
):
    try:
        db.Table("Courses").put_item(
            Item = course.dict()
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Unable to add course")


@app.post("/sections")
def add_section(
    section: AddSectionRequest,
    db: boto3.session.Session = Depends(get_db),
):
    try:
        db.Table("EnrollmentService").put_item(
            Item = section.dict()
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Unable to add section")


@app.patch("/sections/{section_id}")
def update_section(
    section_id: int,
    section: UpdateSectionRequest,
    db: boto3.session.Session = Depends(get_db),
) -> Section:
    
    section_table = db.Table('Sections')

    q = "SET"
    v = {}

    for key, value in section.dict().items():
        if value is not None:
            q += f"{key} = :{key}, "
            v[f":{key}"] = value

    
    if len(v) == 0:
        raise HTTPException(
            status_code=400,
            detail = "No fields provided to update.",
        )

    q = q[:-2]  # remove trailing comma

    # Update the section
    try:
        section_table.update_item(
            Key={'id': section_id},
            Q = q,
            V = v,
        )
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Failed to update section:{e}")
    
    # Retrieve the updated section
    section_data =section_table.get_item(Key={'id': section_id})

    if 'Item' not in section_data:
        raise HTTPException(status_code=404, details="section not found")
    
    return Section(**section_data['Item'])

@app.delete("/users/{user_id}/enrollments/{section_id}")
def drop_user_enrollment(
    student_id: int,
    section_id: int,
    db: boto3.session.Session = Depends(get_db),
):
    try:
        # Update the status for the specified section_id and student_id
        db.Table('Enrollments').update_item(
            Key = {"section_id": section_id, "student_id": student_id},
            UpdateExpression = "SET enrollment_status = :status",
            ExpressionAttributeValues = {':status': EnrollmentStatus.DROPPED}
        )

        # Retrieve the updated enrollment
        try:
        # Retrieve the enrollment for the specified section_id and student_id
            response = db.Table('Enrollments').get_item(
                Key={"section_id": section_id, "student_id": student_id}
            )
            item = response.get('Item')

            if item:
                return {
                    "section_id": item.get("section_id"),
                    "student_id": item.get("student_id"),
                    "enrollment_status": item.get("enrollment_status"),
                    "date": item.get("date")
                }
            else:
                raise HTTPException(status_code=404, detail="Enrollment not found")
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Failed to retrieve enrollment")
        
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Failed to update section:{e}")


@app.delete("/users/{user_id}/waitlist/{section_id}")
def drop_user_waitlist(
    user_id: int,
    section_id: int,
    redis: Redis = Depends(get_redis_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
):
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    waitlist_key = f"waitlist:user_id:{user_id}:section_id:{section_id}"

    # Check if the field exists in the hash
    if not redis.exists(waitlist_key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Section '{section_id}' not found for user {user_id}")

    deleted_position = int(redis.hget(waitlist_key, 'position'))
    redis.delete(waitlist_key)
    # Decrement the position for all users with position greater than the deleted position
    waitlist_keys = redis.keys(f"waitlist:user_id:*:section_id:{section_id}")
    for key in waitlist_keys:
        position = int(redis.hget(key, "position"))
        if position > deleted_position:
            redis.hset(key, "position", position - 1)

    return {"message": f"Section '{section_id}' deleted for user {user_id} from waitlist"}


@app.delete("/sections/{section_id}/enrollments/{user_id}")
def drop_section_enrollment(
    section_id: int,
    user_id: int,
    db = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> Enrollment:

    # Ensure the user is instructing the section or is a registrar.
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        # Requester is instructor and requested user is not self

        # Course existence check
        table = db.Table('Sections')
        response = table.query(
            KeyConditionExpression=Key('section_id').eq(section_id)
        )
        items = response.get('Items', [])
        if not items:
            raise HTTPException(
                status_code=404,
                detail="Section not found.",
            )
        
        # Instructor auth check
        if items[0]["instructor_id"] != jwt_user:
            raise HTTPException(status_code=403, detail="Not authorized")
        
    # No auth so these two methods behave virtually identically.
    return drop_user_enrollment(user_id, section_id, db)


@app.delete("/sections/{section_id}")
def delete_section(section_id: int, db: boto3.session.Session = Depends(get_db), redis_db: Redis = Depends(get_redis_db)):
    # DynamoDB Table
    section_table = db.Table('Sections')
    enrollment_table = db.Table('Enrollments')

    # Check validity of section_id
    section_data = section_table.get_item(
        Key={'section_id': section_id}
    )
    if 'Item' not in section_data:
        raise HTTPException(status_code=404, detail="Section not found")

    # Mark section as deleted
    section_table.update_item(
        Key={'section_id': section_id},
        UpdateExpression="SET deleted = :deleted",
        ExpressionAttributeValues={":deleted": True},
    )

    # Drop enrolled users
    enrolled_users = enrollment_table.query( 
        KeyConditionExpression=Key('section_id').eq(section_id)
    )
    for user_data in enrolled_users.get('Items', []):
        print(user_data)
        drop_user_enrollment(user_data['student_id'], section_id, db)

    # Drop waitlisted users in Redis
    keys = redis_db.keys(f"waitlist:*section_id:{section_id}")
    for k in keys:
        redis_db.delete(k)

    return {"message": "Section deleted successfully"}

# Internal function: get current class enrollment count
def section_enrollment_count(db, section_id):
    table = db.Table('Enrollments')
    response = table.query(
        KeyConditionExpression=Key('section_id').eq(section_id)
    )
    items = response.get("Items", [])

    if items is None:
        return 0
    
    count = 0
    for i in items:
        print(i)
        if i['enrollment_status'] == 'Enrolled':
            count += 1
    return count

# Internal function: add user to the waitlist
async def add_to_waitlist(item: WaitlistItem, redis: Redis = Depends(get_redis_db)):
    waitlist_key = f"waitlist:user_id:{item.user_id}:section_id:{item.section_id}"

    # Check if the user is already in the waitlist for the sectwssion
    if redis.exists(waitlist_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already in the waitlist for this section")

    # Store additional information in a hash
    redis.hset(waitlist_key, "position", item.position)
    redis.hset(waitlist_key, "date", item.date)

    return JSONResponse(content={"message": "User added to the waitlist"}, status_code=status.HTTP_201_CREATED)


# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
