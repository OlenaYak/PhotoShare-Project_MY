1️⃣ Документація (Documentation)

У FastAPI документація автоматично генерується через Swagger та ReDoc, але для повноти проєкту потрібно:

a) API Documentation

Використати FastAPI OpenAPI/Swagger.

Для кожного маршруту додати:

summary – короткий опис.

description – детальний опис, включаючи приклади.

response_model – Pydantic моделі для повернення.

status_code – HTTP-код відповіді.

tags – групування маршрутів, наприклад: Auth, Users, Photos, Comments, Ratings.

Приклад:

from fastapi import APIRouter, Depends, status
from app.schemas import UserOut, UserUpdate
from app.services.auth import auth_service

router = APIRouter(tags=["Users"])

@router.get("/users/{username}", response_model=UserOut, status_code=status.HTTP_200_OK,
            summary="Отримати профіль користувача",
            description="Повертає інформацію про користувача за його унікальним юзернеймом")
async def get_user_profile(username: str):
    user = await auth_service.get_user_by_username(username)
    return user

b) Документація для JWT Auth

Пояснити:

access_token – короткостроковий токен (15 хв).

refresh_token – довгостроковий (7 днів).

email_token – для підтвердження email (3 дні).

Вказати приклади запитів і відповіді (JSON).

c) Документація для роботи з фото

CRUD світлин: POST, GET, PUT, DELETE.

Теги: як створювати, перевіряти на унікальність.

Трансформації Cloudinary та QR-коди.

Приклад JSON запиту:

{
  "description": "Моя подорож в гори",
  "tags": ["travel", "mountains"]
}

d) Документація для коментарів та рейтингів

CRUD коментарів, обмеження редагування та видалення.

Рейтинг: опис обмежень (не можна оцінювати власні фото, один раз на користувача).

e) README.md

Повинна містити:

Опис проєкту.

Як встановити та запустити локально.

Використання Docker / Docker Compose.

Інструкції для тестування.

Приклад запитів через Swagger UI.

2️⃣ Покриття тестами до 90%
a) Типи тестів

Unit tests – окремі функції / методи (auth, токени, хешування пароля).

Integration tests – маршрути FastAPI, перевірка CRUD фото, коментарів, рейтингу.

End-to-End tests (опційно) – повний потік: реєстрація → завантаження фото → оцінка → коментар.

b) Інструменти

pytest + pytest-asyncio (асинхронні тести).

httpx.AsyncClient для тестування FastAPI маршрутів.

pytest-cov для збору покриття.

Приклад unit-тесту для auth:

import pytest
from app.services.auth import Auth

auth_service = Auth()

def test_password_hashing():
    password = "supersecret"
    hashed = auth_service.get_password_hash(password)
    assert auth_service.verify_password(password, hashed)


Приклад тесту маршруту:

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_signup_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Sign up
        response = await ac.post("/api/auth/signup", json={"email":"test@example.com", "password":"123456"})
        assert response.status_code == 201
        
        # Login
        response = await ac.post("/api/auth/login", data={"username":"test@example.com", "password":"123456"})
        assert response.status_code == 200
        assert "access_token" in response.json()

c) План покриття

Auth (JWT, хешування) – 20%

Users (CRUD, профіль, бан) – 20%

Photos (CRUD, теги, Cloudinary, QR) – 25%

Comments – 15%

Ratings – 10%

Search/Filter – 10%

Разом → ≥ 90%

Якщо хочеш, я можу зробити готовий шаблон документації для PhotoShare з прикладами Swagger, README.md і Pydantic схемами, а паралельно скласти пакет тестів з pytest, щоб відразу можна було запустити покриття ≥90%.


Чудово! Давай структуруємо план дій, щоб ти міг одночасно працювати над документацією і тестами, орієнтуючись на досягнення покриття >90 %.

1️⃣ Документація FastAPI

FastAPI автоматично генерує Swagger та Redoc документацію, але треба, щоб вона була повною та інформативною.

Що треба зробити:

Додати опис до кожного маршруту

@router.get("/users/{username}", response_model=UserOut,
            summary="Отримати профіль користувача",
            description="Повертає всю інформацію про користувача за його унікальним юзернеймом")
async def get_user_profile(username: str):
    ...


Вказати типи даних у Pydantic-схемах

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    role: UserRoleEnum


Додати приклади запитів та відповідей

class UserOut(BaseModel):
    ...
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "username": "natalya",
                "email": "natalya@example.com",
                "created_at": "2025-11-21T20:00:00",
                "role": "admin"
            }
        }


Документувати параметри запитів і помилки

@router.get("/photos/{photo_id}", responses={
    404: {"description": "Фото не знайдено"},
    401: {"description": "Неавторизований доступ"}
})


Перевірити всі маршрути, щоб у Swagger був повний опис (/docs) та Redoc (/redoc).

2️⃣ Покриття тестами >90 %
Крок 1: Налаштувати тестове середовище

Використовуй pytest та pytest-asyncio для асинхронних маршрутів.

Можна підключити pytest-cov для вимірювання покриття.

pip install pytest pytest-asyncio pytest-cov httpx

Крок 2: Тестування маршрутів

Використовуй httpx.AsyncClient для тестування FastAPI.

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_user_profile():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users/natalya")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "natalya"


Тестувати всі CRUD операції: для фото, тегів, коментарів, рейтингу.

Тестувати аутентифікацію та ролі (user, moderator, admin).

Крок 3: Чорний список токенів і кеш Redis

Можна мокати Redis через unittest.mock:

from unittest.mock import AsyncMock
auth_service.redis_cache.get = AsyncMock(return_value=None)

Крок 4: Запуск покриття
pytest --cov=app --cov-report=term-missing


--cov-report=term-missing покаже, які файли не покриті тестами.

Мета: покрити усі ключові методи і маршрути, особливо _create_token, аутентифікацію, CRUD для фото та коментарів.

3️⃣ Рекомендації для покриття 90 %

Тестувати усі гілки умов (if expires_delta is not None, if not user, etc.).

Мокати зовнішні сервіси (Redis, Cloudinary), щоб тести були стабільні.

Створити фікстури для користувачів і фото, щоб повторно використовувати в тестах.

Включити тести на помилки (401, 404, 422).