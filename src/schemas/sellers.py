from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from pydantic_core import PydanticCustomError
from typing import Optional, List
from .books import BookRead

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllsellers", "SellerUpdate"]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.

from src.schemas import ReturnedBook


class BaseSeller(BaseModel):
    first_name: str
    second_name: str
    e_mail: str


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    e_mail: str = Field(
        default='no_mail', alias="sellers_mail"
    )
    password: str = Field(
        default='no_password', alias="sellers_password"
    )

    # Пример использования тонкой настройки полей. Передачи в них метаинформации.


    @field_validator("e_mail")  # Валидатор, проверяет что e_mail адрес содержит @
    @staticmethod
    def validate_e_mail(val: str):
        if "@" not in val:
            raise PydanticCustomError("Validation error", "e_mail does not contain @")
        return val


    @field_validator("password")  # Валидатор, проверяет что password содержит больше одного знака
    @staticmethod
    def validate_password(val: str):
        if len(val) < 2:
            raise PydanticCustomError("Validation error", "password is too short")
        return val

# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int
    e_mail: str
    books: list[ReturnedBook]


# Класс для возврата массива объектов "Книга"
class ReturnedAllsellers(BaseModel):
    sellers: list[ReturnedSeller]


class SellerUpdate(BaseModel):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    e_mail: Optional[EmailStr] = None

class SellerRead(BaseModel):
    id: int
    first_name: str
    second_name: str
    e_mail: str
    books: Optional[List[BookRead]] = []
    model_config = ConfigDict(from_attributes=True)
