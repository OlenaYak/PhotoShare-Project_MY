"""
comments.py — функції для роботи з коментарями у PhotoShare API.

Містить CRUD-операції та методи для отримання коментарів користувачів.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException
from app.database.models import User, Comment, UserRoleEnum
from app.schemas import CommentBase


async def create_comment(post_id: int, body: CommentBase, db: Session, user: User) -> Comment:
    """
    Створює новий коментар для конкретного посту.

    :param post_id: ID посту, до якого додається коментар
    :param body: Схема CommentBase, що містить текст коментаря
    :param db: SQLAlchemy сесія
    :param user: Користувач, що створює коментар
    :return: Новостворений об'єкт Comment
    """
    new_comment = Comment(
        text=body.text,
        post_id=post_id,
        user_id=user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


async def edit_comment(comment_id: int, body: CommentBase, db: Session, user: User) -> Comment:
    """
    Редагує існуючий коментар. 
    Доступ лише автору або користувачам з роллю admin/moder.

    :param comment_id: ID коментаря
    :param body: Схема CommentBase з новим текстом
    :param db: SQLAlchemy сесія
    :param user: Користувач, що намагається редагувати коментар
    :raises HTTPException: 404 якщо коментар не знайдено
                            403 якщо користувач не автор або не admin/moder
    :return: Оновлений об'єкт Comment
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not available.")
    
    if comment.user_id != user.id and user.role not in [UserRoleEnum.admin, UserRoleEnum.moder]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment.")

    comment.text = body.text
    comment.updated_at = func.now()
    comment.update_status = True
    db.commit()
    db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: Session, user: User) -> Optional[Comment]:
    """
    Видаляє коментар. 
    Доступ лише автору або користувачам з роллю admin/moder.

    :param comment_id: ID коментаря
    :param db: SQLAlchemy сесія
    :param user: Користувач, що намагається видалити коментар
    :return: Видалений об'єкт Comment або None, якщо коментар не знайдено чи недоступний
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment and (user.role in [UserRoleEnum.admin, UserRoleEnum.moder] or comment.user_id == user.id):
        db.delete(comment)
        db.commit()
        return comment
    return None


async def show_single_comment(comment_id: int, db: Session, user: User) -> Optional[Comment]:
    """
    Повертає конкретний коментар. 
    Доступ лише автору або користувачам з роллю admin/moder.

    :param comment_id: ID коментаря
    :param db: SQLAlchemy сесія
    :param user: Користувач, що намагається переглянути коментар
    :return: Об'єкт Comment або None, якщо коментар недоступний
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment and (comment.user_id == user.id or user.role in [UserRoleEnum.admin, UserRoleEnum.moder]):
        return comment
    return None


async def show_user_comments(user_id: int, db: Session) -> List[Comment]:
    """
    Повертає список всіх коментарів конкретного користувача.

    :param user_id: ID користувача
    :param db: SQLAlchemy сесія
    :return: Список об'єктів Comment
    """
    return db.query(Comment).filter(Comment.user_id == user_id).all()


async def show_user_post_comments(user_id: int, post_id: int, db: Session) -> List[Comment]:
    """
    Повертає список коментарів конкретного користувача для певного поста.

    :param user_id: ID користувача
    :param post_id: ID посту
    :param db: SQLAlchemy сесія
    :return: Список об'єктів Comment
    """
    return db.query(Comment).filter(
        and_(Comment.post_id == post_id, Comment.user_id == user_id)
    ).all()
