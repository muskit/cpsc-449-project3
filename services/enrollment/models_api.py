from pydantic import BaseModel

class AddCourseRequest(BaseModel):
    course_id: str
    course_name: str
    department: str

class AddSectionRequest(BaseModel):
    course_id: str
    course_name: str
    classroom: str
    capacity: int
    waitlist_capacity: int
    days: str
    begin_time: str
    end_time: str
    freeze: int #bool 0 or 1
    deleted: int #bool 0 or 1
    instructor_id: int