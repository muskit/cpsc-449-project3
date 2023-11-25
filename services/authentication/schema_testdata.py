from pydantic import BaseModel
from internal import password
from .models import *
from .api import RegisterRequest

users: list[RegisterRequest] = [
    RegisterRequest(
        username="johndoe",
        password="password",
        roles=[Role.STUDENT],
        first_name="John",
        last_name="Doe",
    ),
    RegisterRequest(
        username="kenyttavery",
        password="password",
        roles=[Role.INSTRUCTOR, Role.REGISTRAR],
        first_name="Kenytt",
        last_name="Avery",
    ),
    RegisterRequest(
        username="janedoe",
        password="password",
        roles=[Role.REGISTRAR],
        first_name="Jane",
        last_name="Doe",
    ),
    RegisterRequest(
        username="bobbymuir",
        password="password",
        roles=[Role.INSTRUCTOR],
        first_name="Bobby",
        last_name="Muir",
    ),
    RegisterRequest(
        username="alicesmith",
        password="password",
        roles=[Role.STUDENT],
        first_name="Alice",
        last_name="Smith",
    ),
    RegisterRequest(
        username="bobjones",
        password="password",
        roles=[Role.STUDENT],
        first_name="Bob",
        last_name="Jones",
    ),
    RegisterRequest(
        username="carolwilliams",
        password="password",
        roles=[Role.STUDENT],
        first_name="Carol",
        last_name="Williams",
    ),
    RegisterRequest(
        username="davebrown",
        password="password",
        roles=[Role.STUDENT],
        first_name="Dave",
        last_name="Brown",
    ),
    RegisterRequest(
        username="evemiller",
        password="password",
        roles=[Role.STUDENT],
        first_name="Eve",
        last_name="Miller",
    ),
    RegisterRequest(
        username="frankdavis",
        password="password",
        roles=[Role.STUDENT],
        first_name="Frank",
        last_name="Davis",
    ),
    RegisterRequest(
        username="gracegarcia",
        password="password",
        roles=[Role.STUDENT],
        first_name="Grace",
        last_name="Garcia",
    ),
    RegisterRequest(
        username="henryrodriguez",
        password="password",
        roles=[Role.STUDENT],
        first_name="Henry",
        last_name="Rodriguez",
    ),
    RegisterRequest(
        username="isabelwilson",
        password="password",
        roles=[Role.STUDENT],
        first_name="Isabel",
        last_name="Wilson",
    ),
    RegisterRequest(
        username="jackmartinez",
        password="password",
        roles=[Role.STUDENT],
        first_name="Jack",
        last_name="Martinez",
    ),
]
