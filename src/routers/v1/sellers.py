# Для импорта из корневого модуля
# import sys
# sys.path.append("..")
# from main import app

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from src.models.sellers import Seller
from src.models.users import User
from src.schemas import IncomingSeller, ReturnedAllsellers, ReturnedSeller, SellerUpdate
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from auth.deps import get_current_user

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# CRUD - Create, Read, Update, Delete

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о продавце в БД. Возвращает созданного продавца.
# @sellers_router.post("/sellers/", status_code=status.HTTP_201_CREATED)
@sellers_router.post(
    "/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED
)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller,
    session: DBSession,
):  # прописываем модель валидирующую входные данные
    # session = get_async_session() вместо этого мы используем иньекцию зависимостей DBSession

    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        **{
            "first_name": seller.first_name,
            "second_name": seller.second_name,
            "e_mail": seller.e_mail,
            "password": seller.password
        }
    )

    session.add(new_seller)
    await session.flush()
    await session.refresh(new_seller)

    # повторно получаем объект, чтобы подгрузить books
    result = await session.execute(
        select(Seller).options(selectinload(Seller.books)).where(Seller.id == new_seller.id)
    )
    full_seller = result.scalar_one()

    return full_seller



# Ручка, возвращающая всех продавцов с книгами
@sellers_router.get("/", response_model=ReturnedAllsellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller).options(selectinload(Seller.books))
    result = await session.execute(query)
    sellers = result.scalars().all()
    return {"sellers": sellers}

# Ручка, возвращающая одного продавца с книгами
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession, current_user: User = Depends(get_current_user)):
    query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    result = await session.execute(query)
    seller = result.scalar_one_or_none()

    if seller:
        return seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_seller:
        await session.delete(deleted_seller)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о книге
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_seller_data: SellerUpdate, session: DBSession):
    result = await session.execute(
        select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    )
    updated_seller = result.scalar_one_or_none()

    if updated_seller is None:
        raise HTTPException(status_code=404, detail="Seller not found")

    if new_seller_data.first_name is not None:
        updated_seller.first_name = new_seller_data.first_name
    if new_seller_data.second_name is not None:
        updated_seller.second_name = new_seller_data.second_name
    if new_seller_data.e_mail is not None:
        updated_seller.e_mail = new_seller_data.e_mail

    await session.flush()
    await session.refresh(updated_seller)

    return updated_seller  # FastAPI теперь сможет корректно сериализовать с books