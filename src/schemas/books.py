from pydantic import BaseModel, Field, field_validator,ConfigDict
from pydantic_core import PydanticCustomError

__all__ = ["IncomingBook", "ReturnedBook", "ReturnedAllbooks"]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BaseBook):
    pages: int = Field(
        default=150, alias="count_pages",
    )
    seller_id: int

    # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("year")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_year(val: int):
        if val < 2020:
            raise PydanticCustomError("Validation error", "Year is too old!")

        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBook):
    id: int
    pages: int
    seller_id: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllbooks(BaseModel):
    books: list[ReturnedBook]

class BookRead(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)
