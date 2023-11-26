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
    student_id: int
    section_id: int
    enrollment_status: EnrollmentStatus


class WaitlistItem(BaseModel):
    user_id: int
    section_id: Section
    position: int
    date: str