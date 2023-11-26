import logging.config
import boto3
from boto3.dynamodb.conditions import Key, Attr
from pydantic_settings import BaseSettings
from fastapi.routing import APIRoute
from fastapi import FastAPI, Depends, HTTPException, Request, status
# from pydantic import BaseModel
from fastapi.responses import JSONResponse
from internal.jwt_claims import require_x_roles, require_x_user
from redis import Redis

from internal.database_dynamo import get_db
from .model_requests import *
from .models import *

app = FastAPI()

# Connect to Redis
def get_redis_db():
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
    
'''
@app.get("/courses/{course_id}/waitlist")
def get_course_waitlist(
    course_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> GetCourseWaitlistResponse:
    rows = fetch_rows(
        db,
        """
        SELECT waitlist.user_id, sections.id
        FROM waitlist
        INNER JOIN sections ON waitlist.section_id = sections.id
        WHERE sections.course_id = ? AND sections.deleted = FALSE
        """,
        (course_id,),
    )
    return GetCourseWaitlistResponse(
        waitlist=database.list_waitlist(
            db,
            [(row["waitlist.user_id"], row["sections.id"]) for row in rows],
        )
    )
'''

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
    table = db.Table('Enrollment')
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

    table = db.Table('Enrollment')
    response = table.scan(
        FilterExpression='student_id = :student_id',
        ExpressionAttributeValues={':student_id': student_id}
    )

    items = response.get('Items',[])
    
    if not items:
        raise HTTPException(status_code=404, detail= "No enrollments found for:" + str(student_id))
    else:
        return {'response': items}


app.get("/users/{user_id}/enrollments")
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
  
   

''' To tired to think this one out
@app.get("/users/{user_id}/waitlist")
def list_user_waitlist(
    user_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> ListUserWaitlistResponse:
    section_ids = fetch_rows(
        db,
        """
        SELECT waitlist.user_id, waitlist.section_id
        FROM waitlist
        INNER JOIN sections ON sections.id = waitlist.section_id
        WHERE
            sections.deleted = FALSE
            AND (user_id = :user_id OR instructor_id = :user_id)
        """,
        {"user_id": user_id},
    )
    rows = [extract_row(row, "waitlist") for row in section_ids]
    return ListUserWaitlistResponse(
        waitlist=database.list_waitlist(
            db,
            [(row["user_id"], row["section_id"]) for row in rows],
        )
    )


@app.post("/users/{user_id}/enrollments")  # student attempt to enroll in class
def create_enrollment(
    user_id: int,
    enrollment: CreateEnrollmentRequest,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> CreateEnrollmentResponse:
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    d = {
        "user": user_id,
        "section": enrollment.section,
    }

    waitlist_position = None

    # Verify that the class still has space.
    id = fetch_row(
        db,
        """
        SELECT id
        FROM sections as s
        WHERE s.id = :section
        AND s.capacity > (SELECT COUNT(*) FROM enrollments WHERE section_id = :section)
        AND s.freeze = FALSE
        AND s.deleted = FALSE
        """,
        d,
    )
    if id:
        # If there is space, enroll the student.
        write_row(
            db,
            """
            INSERT INTO enrollments (user_id, section_id, status, grade, date)
            VALUES(:user, :section, 'Enrolled', NULL, CURRENT_TIMESTAMP)
            """,
            d,
        )
    else:
        # Otherwise, try to add them to the waitlist.
        id = fetch_row(
            db,
            """
            SELECT id
            FROM sections as s
            WHERE s.id = :section
            AND s.waitlist_capacity > (SELECT COUNT(*) FROM waitlist WHERE section_id = :section)
            AND (SELECT COUNT(*) FROM waitlist WHERE user_id = :user) < 3
            AND s.freeze = FALSE
            AND s.deleted = FALSE
            """,
            d,
        )
        if id:
            row = fetch_row(
                db,
                """
                INSERT INTO waitlist (user_id, section_id, position, date)
                VALUES(:user, :section, (SELECT COUNT(*) FROM waitlist WHERE section_id = :section), CURRENT_TIMESTAMP)
                RETURNING position
                """,
                d,
            )

            # Read back the waitlist position.
            assert row
            waitlist_position = row["waitlist.position"]

            # Ensure that there's also a waitlist enrollment.
            write_row(
                db,
                """
                INSERT INTO enrollments (user_id, section_id, status, grade, date)
                VALUES(:user, :section, 'Waitlisted', NULL, CURRENT_TIMESTAMP)
                """,
                d,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Section is full and waitlist is full.",
            )

    enrollments = database.list_enrollments(db, [(d["user"], d["section"])])
    return CreateEnrollmentResponse(
        **dict(enrollments[0]),
        waitlist_position=waitlist_position,
    )
'''

@app.post("/courses")
def add_course(
    course: AddCourseRequest,
    db: boto3.session.Session = Depends(get_db),
):
    try:
        db.Table("Courses").put_item(
            Item=course.dict()
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
            Item=section.dict()
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Unable to add section")

'''
@app.patch("/sections/{section_id}")
def update_section(
    section_id: int,
    section: UpdateSectionRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> Section:
    q = """
    UPDATE sections
    SET
    """
    v = {}
    for key, value in section.dict().items():
        if value is not None:
            q += f"{key} = :{key}, "
            v[key] = value

    if len(v) == 0:
        raise HTTPException(
            status_code=400,
            detail="No fields provided to update.",
        )

    q = q[:-2]  # remove trailing comma

    q += """
    WHERE id = :section_id
    """
    v["section_id"] = section_id

    try:
        write_row(db, q, v)
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Failed to update section:{e}")

    sections = database.list_sections(db, [section_id])
    return sections[0]


@app.delete("/users/{user_id}/enrollments/{section_id}")
def drop_user_enrollment(
    user_id: int,
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> Enrollment:
    write_row(
        db,
        """
        UPDATE enrollments
        SET status = 'Dropped'
        WHERE
            user_id = :user_id
            AND section_id = :section_id
            AND status = 'Enrolled'
        """,
        {"user_id": user_id, "section_id": section_id},
    )

    enrollments = database.list_enrollments(db, [(user_id, section_id)])
    return enrollments[0]

'''

@app.delete("/users/{user_id}/waitlist/{section_id}")
def drop_user_waitlist(
    user_id: int,
    section_id: int,
    db: boto3.session.Session = Depends(get_db),
    redis: Redis = Depends(get_redis_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
):
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    ### Remove waitlist entry in Redis ###
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

    ### Delete the waitlist enrollment from DynamoDB ###
    # TODO: DynamoDB call that deletes enrollment entry (does NOT mark for deletion)



    return {"message": f"Section '{section_id}' deleted for user {user_id} from waitlist"}

'''
@app.delete("/sections/{section_id}/enrollments/{user_id}")
def drop_section_enrollment(
    section_id: int,
    user_id: int,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> Enrollment:
    # Ensure the user is instructing the section or is a registrar.
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        row = fetch_row(
            db,
            """
            SELECT instructor_id FROM sections
            WHERE id = :section_id
            """,
            {"section_id": section_id},
        )
        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Section not found.",
            )
        if row["sections.instructor_id"] != jwt_user:
            raise HTTPException(status_code=403, detail="Not authorized")

    # No auth so these two methods behave virtually identically.
    return drop_user_enrollment(user_id, section_id, db)


@app.delete("/sections/{section_id}")
def delete_section(section_id: int, db: sqlite3.Connection = Depends(get_db)):
    # check validity of section_id
    get_section(section_id, db)

    # mark section as deleted
    write_row(
        db,
        """
        UPDATE sections
        SET deleted = TRUE
        WHERE id = :section_id
        """,
        {"section_id": section_id},
    )

    # drop enrolled users
    ue = fetch_rows(
        db,
        f"""
        SELECT user_id FROM enrollments
        WHERE 
            section_id = :section_id
        """,
        {"section_id": section_id},
    )
    for u in ue:
        print(u)
        drop_user_enrollment(u[0], section_id, db)

    # drop waitlisted users
    uw = fetch_rows(
        db,
        f"""
        SELECT user_id FROM waitlist
        WHERE 
            section_id = :section_id
        """,
        {"section_id": section_id},
    )
    for u in uw:
        drop_user_waitlist(u[0], section_id, db)
'''

# Endpoint to add a user to the waitlist
@app.post("/waitlist/")
async def add_to_waitlist(item: WaitlistItem, redis: Redis = Depends(get_redis_db)):
    waitlist_key = f"waitlist:user_id:{item.user_id}:section_id:{item.section_id}"

    # Check if the user is already in the waitlist for the sectwssion
    if redis.exists(waitlist_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already in the waitlist for this section")

    # Store additional information in a hash
    redis.hset(waitlist_key, "position", item.position)
    redis.hset(waitlist_key, "date", item.date)

    return JSONResponse(content={"message": "User added to the waitlist"}, status_code=status.HTTP_201_CREATED)




@app.delete("/deleteFromWaitlist/{user_id}/{section_id}")
async def delete_from_waitlist(user_id:int, section_id:int, redis: Redis = Depends(get_redis_db)):
    
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

#To get wailtists for a user
@app.get("/user_waitlist/{user_id}")
async def get_user_waitlist(user_id: int, redis: Redis = Depends(get_redis_db)):
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
    

# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
