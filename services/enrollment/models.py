from enum import Enum
from pydantic import BaseModel
from typing import List

from services.authentication.models import *


class Course(BaseModel):
    course_id: str
    course_name: str
    department: str


class Section(BaseModel):
    section_id: int
    course_id: str
    classroom: str
    capacity: int
    waitlist_capacity: int
    days: List[str]
    begin_time: str
    end_time: str
    freeze: bool
    deleted: bool
    instructor_id: int


class EnrollmentStatus(str, Enum):
    ENROLLED = "Enrolled"
    WAITLISTED = "Waitlisted"
    DROPPED = "Dropped"


class Enrollment(BaseModel):
    user_id: int
    section: Section
    status: EnrollmentStatus


class Waitlist(BaseModel):
    user_id: int
    section: Section
    position: int
