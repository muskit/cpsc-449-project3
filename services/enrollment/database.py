import contextlib
import sqlite3
import time
import os
from internal.database import fetch_rows, extract_row, set_db_path
from typing import Any, Generator, Iterable, Type
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models import *


db_path = "run/enrollment.db"
set_db_path(db_path)


def list_courses(
    db: sqlite3.Connection,
    course_ids: list[int] | None = None,
) -> list[Course]:
    courses_rows = fetch_rows(
        db,
        """
        SELECT
            courses.*,
            departments.*
        FROM courses
        INNER JOIN departments ON departments.id = courses.department_id
        """
        + (
            "WHERE courses.id IN (%s)" % ",".join(["?"] * len(course_ids))
            if course_ids is not None
            else ""
        ),
        course_ids,
    )
    return [
        Course(
            **extract_row(row, "courses"),
            department=Department(**extract_row(row, "departments")),
        )
        for row in courses_rows
    ]


def list_sections(
    db: sqlite3.Connection,
    section_ids: list[int] | None = None,
) -> list[Section]:
    rows = fetch_rows(
        db,
        """
        SELECT
            sections.*,
            courses.*,
            departments.*
        FROM sections
        INNER JOIN courses ON courses.id = sections.course_id
        INNER JOIN departments ON departments.id = courses.department_id
        """
        + (
            "WHERE sections.id IN (%s)" % ",".join(["?"] * len(section_ids))
            if section_ids is not None
            else ""
        ),
        section_ids,
    )
    return [
        Section(
            **extract_row(row, "sections"),
            course=Course(
                **extract_row(row, "courses"),
                department=Department(
                    **extract_row(row, "departments"),
                ),
            ),
        )
        for row in rows
    ]


def list_enrollments(
    db: sqlite3.Connection,
    user_section_ids: list[tuple[int, int]] | None = None,
) -> list[Enrollment]:
    q = """
        SELECT
            courses.*,
            sections.*,
            enrollments.*,
            departments.*
        FROM enrollments
        INNER JOIN sections ON sections.id = enrollments.section_id
        INNER JOIN courses ON courses.id = sections.course_id
        INNER JOIN departments ON departments.id = courses.department_id
    """
    p = []
    if user_section_ids is not None:
        q += "WHERE (enrollments.user_id, sections.id) IN (%s)" % ",".join(
            ["(?, ?)"] * len(user_section_ids)
        )
        p = [item for sublist in user_section_ids for item in sublist]  # flatten list

    rows = fetch_rows(db, q, p)
    return [
        Enrollment(
            **extract_row(row, "enrollments"),
            section=Section(
                **extract_row(row, "sections"),
                course=Course(
                    **extract_row(row, "courses"),
                    department=Department(
                        **extract_row(row, "departments"),
                    ),
                ),
            ),
        )
        for row in rows
    ]


def list_waitlist(
    db: sqlite3.Connection,
    user_section_ids: list[tuple[int, int]] | None = None,
) -> list[Waitlist]:
    q = """
        SELECT
            waitlist.*,
            sections.*,
            courses.*,
            departments.*
        FROM waitlist
        INNER JOIN sections ON sections.id = waitlist.section_id
        INNER JOIN courses ON courses.id = sections.course_id
        INNER JOIN departments ON departments.id = courses.department_id
    """
    p = []
    if user_section_ids is not None:
        q += "WHERE (waitlist.user_id, sections.id) IN (%s)" % ",".join(
            ["(?, ?)"] * len(user_section_ids)
        )
        p = [item for sublist in user_section_ids for item in sublist]  # flatten list

    rows = fetch_rows(db, q, p)
    return [
        Waitlist(
            **extract_row(row, "waitlist"),
            section=Section(
                **extract_row(row, "sections"),
                course=Course(
                    **extract_row(row, "courses"),
                    department=Department(
                        **extract_row(row, "departments"),
                    ),
                ),
            ),
        )
        for row in rows
    ]
