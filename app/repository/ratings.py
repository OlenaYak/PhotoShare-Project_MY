"""
ratings.py — функції для роботи з оцінками (rating) постів у PhotoShare API.

Містить CRUD-операції над рейтингами, перевірку прав користувача і обмеження голосування.
"""

from typing import Type
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from starlette import status

from app.database.models import Rating, User, Post, UserRoleEnum
from app.conf import messages as message


async def create_rate(post_id: int, rate: int, db: Session, user: User) -> Rating:
    """
    Створює новий рейтинг для поста користувача.

    Перевіряє:
    - користувач не може оцінювати власний пост,
    - користувач не може голосувати двічі за один пост.

    :param post_id: ID поста
    :param rate: Значення рейтингу (1 або -1)
    :param db: SQLAlchemy сесія
    :param user: Поточний користувач
    :return: Створений об'єкт Rating
    :raises HTTPException: Якщо пост власний або вже оцінений користувачем
    """
    is_self_post = db.query(Post).filter(and_(Post.id == post_id, Post.user_id == user.id)).first()
    already_voted = db.query(Rating).filter(and_(Rating.post_id == post_id, Rating.user_id == user.id)).first()
    post_exists = db.query(Post).filter(Post.id == post_id).first()

    if is_self_post:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=message.OWN_POST)
    elif already_voted:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=message.VOTE_TWICE)
    elif post_exists:
        new_rate = Rating(
            post_id=post_id,
            rate=rate,
            user_id=user.id
        )
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
        return new_rate


async def edit_rate(rate_id: int, new_rate: int, db: Session, user: User) -> Type[Rating] | None:
    """
    Оновлює існуючий рейтинг поста.

    Можливе редагування:
    - користувачем, який поставив рейтинг,
    - адміністратором або модератором.

    :param rate_id: ID рейтингу
    :param new_rate: Нове значення рейтингу
    :param db: SQLAlchemy сесія
    :param user: Поточний користувач
    :return: Оновлений об'єкт Rating або None, якщо рейтинг не знайдено
    """
    rate = db.query(Rating).filter(Rating.id == rate_id).first()
    if rate and (user.role in [UserRoleEnum.admin, UserRoleEnum.moder] or rate.user_id == user.id):
        rate.rate = new_rate
        db.commit()
    return rate


async def delete_rate(rate_id: int, db: Session, user: User) -> Type[Rating] | None:
    """
    Видаляє рейтинг.

    :param rate_id: ID рейтингу
    :param db: SQLAlchemy сесія
    :param user: Поточний користувач
    :return: Видалений об'єкт Rating або None, якщо рейтинг не знайдено
    """
    rate = db.query(Rating).filter(Rating.id == rate_id).first()
    if rate:
        db.delete(rate)
        db.commit()
    return rate


async def show_ratings(db: Session, user: User) -> list[Type[Rating]]:
    """
    Повертає список усіх рейтингів у системі.

    :param db: SQLAlchemy сесія
    :param user: Поточний користувач (для авторизації)
    :return: Список об'єктів Rating
    """
    all_ratings = db.query(Rating).all()
    return all_ratings


async def show_my_ratings(db: Session, user: User) -> list[Type[Rating]]:
    """
    Повертає всі рейтинги поточного користувача.

    :param db: SQLAlchemy сесія
    :param user: Поточний користувач
    :return: Список об'єктів Rating
    """
    return db.query(Rating).filter(Rating.user_id == user.id).all()


async def user_rate_post(user_id: int, post_id: int, db: Session, user: User) -> Type[Rating] | None:
    """
    Повертає рейтинг, який конкретний користувач поставив певному посту.

    :param user_id: ID користувача
    :param post_id: ID поста
    :param db: SQLAlchemy сесія
    :param user: Поточний користувач
    :return: Об'єкт Rating або None, якщо рейтинг не знайдено
    """
    return db.query(Rating).filter(and_(Rating.post_id == post_id, Rating.user_id == user_id)).first()
