import re
from abc import ABC
from typing import Optional

import pydantic


class AbstractAd(pydantic.BaseModel, ABC):
    title: str
    description: str
    user_id: int


class CreateAd(AbstractAd):
    title: str
    description: str
    user_id: int


class UpdateAd(AbstractAd):
    title: Optional[str] = None
    description: Optional[str] = None
    user_id: int


class AbstractUser(pydantic.BaseModel, ABC):
    name: str
    second_name: str
    mail: str
    password: str

    # Проверка корректности переданного mail

    @pydantic.field_validator("mail")
    @classmethod
    def check_mail(cls, mail: str) -> str:
        if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$', mail):
            return mail
        else:
            raise ValueError(f"Incorrect format mail")


class CreateUser(AbstractUser):
    name: str
    second_name: str
    mail: str
    password: str


class UpdateUser(AbstractUser):
    name: Optional[str] = None
    second_name: Optional[str] = None
    mail: Optional[str] = None
    password: Optional[str] = None
