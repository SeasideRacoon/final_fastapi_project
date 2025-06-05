import pytest
from sqlalchemy import select
from src.models.books import Book
from src.models.sellers import Seller
from fastapi import status
from icecream import ic


# Тест на ручку, создающую книгу
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "Ivan",
        "second_name": "Petrov",
        "sellers_mail": "ivan@petrov.ru",
        "sellers_password": "my_password",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id, "Seller id not returned from endpoint"

    assert result_data == {
        "first_name": "Ivan",
        "second_name": "Petrov",
        "e_mail": "ivan@petrov.ru",
        "books": [],
    }

    print("result_data =", result_data)


@pytest.mark.asyncio
async def test_create_seller_with_wrong_email(async_client):
    data = {
        "first_name": "Petr",
        "second_name": "Petrov",
        "sellers_mail": "petrpetrov.ru",
        "sellers_password": "my_password",
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_seller_with_wrong_password(async_client):
    data = {
        "first_name": "Kirill",
        "second_name": "Petrov",
        "sellers_mail": "Kirill@petrov.ru",
        "sellers_password": "k",
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку, которая
    # может случиться в POST ручке
    seller = Seller(first_name="Evgeniy", second_name="Smirnov", e_mail="evgeniysmirnov@mail.ru", password="pass")
    seller_2 = Seller(first_name="Igor", second_name="Sidorov", e_mail="igorsidorov@mail.ru", password="word")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert (
            len(response.json()["sellers"]) == 2
    )  # Опасный паттерн! Если в БД есть данные, то тест упадет

    result_data = response.json()
    sellers = result_data.get("sellers", [])

    print("result_data =", result_data)

    for seller in sellers:
        assert "id" in seller, f"No 'id' in seller object: {seller}"
        assert seller["id"] is not None, f"Seller id is None: {seller}"

        # Проверяем только релевантные поля (без id)
        expected_sellers = [
            {
                "first_name": "Evgeniy",
                "second_name": "Smirnov",
                "e_mail": "evgeniysmirnov@mail.ru",
                "books": [],
            },
            {
                "first_name": "Igor",
                "second_name": "Sidorov",
                "e_mail": "igorsidorov@mail.ru",
                "books": [],
            },
        ]

        actual_simplified = [
            {k: seller[k] for k in ["first_name", "second_name", "e_mail", "books"]}
            for seller in sellers
        ]

        assert actual_simplified == expected_sellers


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = Seller(first_name="Evgeniy", second_name="Smirnov", e_mail="evgeniysmirnov@mail.ru", password="pass")
    seller_2 = Seller(first_name="Igor", second_name="Sidorov", e_mail="igorsidorov@mail.ru", password="word")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Evgeniy",
        "second_name": "Smirnov",
        "e_mail": "evgeniysmirnov@mail.ru",
        "id": seller.id,
        "books": [],
    }

# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = Seller(first_name="Evgeniy", second_name="Smirnov", e_mail="evgeniysmirnov@mail.ru", password="pass")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={
            "first_name": "Evgeniy",
            "second_name": "Smirnov",
            "e_mail": "evgeniy@mail.ru",
            "password": "word",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Evgeniy"
    assert res.second_name == "Smirnov"
    assert res.e_mail == "evgeniy@mail.ru"
    assert res.id == seller.id



@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="Evgeniy", second_name="Smirnov", e_mail="evgeniysmirnov@mail.ru", password="pass")

    db_session.add(seller)
    await db_session.flush()
    ic(seller.id)

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_seller_with_invalid_seller_id(db_session, async_client):
    seller = Seller(first_name="Evgeniy", second_name="Smirnov", e_mail="evgeniysmirnov@mail.ru", password="pass")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND