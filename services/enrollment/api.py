import logging.config
import boto3
from boto3.dynamodb.conditions import Key, Attr
from pydantic_settings import BaseSettings
from fastapi.routing import APIRoute
from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from internal.jwt_claims import require_x_roles, require_x_user


app = FastAPI()

# Connect to the database and logs it
def get_db():
    return boto3.resource('dynamodb', endpoint_url = 'http://localhost:8000')

@app.get("/courses")
def list_courses(
    department_name: str,
    db: boto3.session.Session = Depends(get_db),
):
    courses = db.Table("Courses").scan()["Items"]
    return {"Courses": courses}

@app.get("/courses/{course_code}")
def get_course(
    department_name: str,
    course_code: str,
    db: boto3.session.Session = Depends(get_db),
):
    response = db.Table('Course').query(
        KeyConditionExp = Key('course_code').eq(course_code)
    )
    return response('Items')
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
    sections = db.Table('Sections').scan()['Items']
    return {'Sections': sections}


@app.get("/sections/{section_id}")
def get_section(
    section_id: int,
    db: boto3.session.Session = Depends(get_db),
):
    response = db.Table('Sections').query(
        KeyConditionExp = Key('section_id').eq(section_id)
    )
    return response('Items')


@app.get("/sections/{section_id}/enrollments")
def list_section_enrollments(
    section_id: int,
    db: boto3.session.Session = Depends(get_db),
):
    response = db.Table('Enrollments').query(
        KeyConditionExp = Key('section_id').eq(section_id)
    )

'''
@app.get("/sections/{section_id}/waitlist")
def list_section_waitlist(
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
) -> ListSectionWaitlistResponse:
    rows = fetch_rows(
        db,
        """
        SELECT waitlist.user_id, waitlist.section_id
        FROM waitlist
        INNER JOIN sections ON sections.id = waitlist.section_id
        WHERE waitlist.section_id = ? AND sections.deleted = FALSE
        """,
        (section_id,),
    )
    rows = [extract_row(row, "waitlist") for row in rows]
    waitlist = database.list_waitlist(
        db,
        [(row["user_id"], row["section_id"]) for row in rows],
    )
    return ListSectionWaitlistResponse(
        waitlist=[ListSectionWaitlistItem(**dict(item)) for item in waitlist]
    )
'''
'''
@app.get("/users/{user_id}/enrollments")
def list_user_enrollments(
    user_id: int,
    status=EnrollmentStatus.ENROLLED,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
) -> ListUserEnrollmentsResponse:
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    rows = fetch_rows(
        db,
        """
        SELECT enrollments.user_id, enrollments.section_id
        FROM enrollments
        INNER JOIN sections ON sections.id = enrollments.section_id
        WHERE
            enrollments.status = ?
            AND sections.deleted = FALSE
            AND enrollments.user_id = ?
        """,
        (status, user_id),
    )
    rows = [extract_row(row, "enrollments") for row in rows]
    return ListUserEnrollmentsResponse(
        enrollments=database.list_enrollments(
            db,
            [(row["user_id"], row["section_id"]) for row in rows],
        )
    )


@app.get("/users/{user_id}/sections")
def list_user_sections(
    user_id: int,
    type: ListUserSectionsType = ListUserSectionsType.ALL,
    db: sqlite3.Connection = Depends(get_db),
) -> ListUserSectionsResponse:
    q = """
        SELECT sections.id
        FROM sections
        INNER JOIN enrollments ON enrollments.section_id = sections.id
        WHERE sections.deleted = FALSE AND
    """

    wheres = []
    q += "("
    if type == ListUserSectionsType.ALL or type == ListUserSectionsType.ENROLLED:
        wheres.append("enrollments.user_id = :user_id")
    if type == ListUserSectionsType.ALL or type == ListUserSectionsType.INSTRUCTING:
        wheres.append("sections.instructor_id = :user_id")
    q += " OR ".join(wheres)
    q += ")"

    rows = fetch_rows(db, q, {"user_id": user_id})
    return ListUserSectionsResponse(
        sections=database.list_sections(db, [row["sections.id"] for row in rows])
    )


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


@app.post("/courses")
def add_course(
    course: AddCourseRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> Course:
    try:
        row = fetch_row(
            db,
            """
            INSERT INTO courses(code, name, department_id)
            VALUES(:code, :name, :department_id)
            RETURNING id
            """,
            dict(course),
        )
        assert row
        courses = database.list_courses(db, [row["courses.id"]])
        return courses[0]
    except Exception:
        raise HTTPException(status_code=409, detail=f"Failed to add course:")


@app.post("/sections")
def add_section(
    section: AddSectionRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> Section:
    try:
        row = fetch_row(
            db,
            """
            INSERT INTO sections(course_id, classroom, capacity, waitlist_capacity, day, begin_time, end_time, freeze, instructor_id)
            VALUES(:course_id, :classroom, :capacity, :waitlist_capacity, :day, :begin_time, :end_time, :freeze, :instructor_id)
            RETURNING id
            """,
            dict(section),
        )
        assert row
        sections = database.list_sections(db, [row["sections.id"]])
        return sections[0]
    except Exception:
        raise HTTPException(status_code=409, detail=f"Failed to add course:")


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


@app.delete("/users/{user_id}/waitlist/{section_id}")
def drop_user_waitlist(
    user_id: int,
    section_id: int,
    db: sqlite3.Connection = Depends(get_db),
    jwt_user: int = Depends(require_x_user),
    jwt_roles: list[Role] = Depends(require_x_roles),
):
    if Role.REGISTRAR not in jwt_roles and jwt_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete the entry from the waitlist, storing the position.
    row = fetch_row(
        db,
        """
        DELETE FROM waitlist
        WHERE
            user_id = :user_id
            AND section_id = :section_id
        RETURNING position
        """,
        {"user_id": user_id, "section_id": section_id},
    )
    if row is None:
        raise HTTPException(
            status_code=400,
            detail="User is not on the waitlist.",
        )

    position = row["waitlist.position"]

    # Ensure that every waitlist entry after this one has its position decremented.
    write_row(
        db,
        """
        UPDATE waitlist
        SET position = position - 1
        WHERE
            section_id = :section_id
            AND position > :position
        """,
        {"section_id": section_id, "position": position},
    )

    # Delete the waitlist enrollment.
    write_row(
        db,
        """
        DELETE FROM enrollments
        WHERE
            user_id = :user_id
            AND section_id = :section_id
            AND status = 'Waitlisted'
        """,
        {"user_id": user_id, "section_id": section_id},
    )


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

# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#using-the-path-operation-function-name-as-the-operationid
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name