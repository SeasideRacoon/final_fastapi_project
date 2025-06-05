from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth.utils import verify_password, hash_password, create_access_token
from src.models.users import User
from src.schemas.auth import Token, AuthData, UserCreate
from src.configurations.database import get_async_session

router = APIRouter()


@router.post("/token", response_model=Token)
async def get_or_create_token(auth_data: AuthData, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User).where(User.e_mail == auth_data.e_mail))
    user = result.scalars().first()

    if user:
        # Проверка пароля
        if not verify_password(auth_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    else:
        # Регистрация нового пользователя
        user = User(
            e_mail=auth_data.e_mail,
            password=hash_password(auth_data.password)
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}