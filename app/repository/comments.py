from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException
from app.database.models import User, Comment, UserRoleEnum
from app.schemas import CommentBase


async def create_comment(post_id: int, body: CommentBase, db: Session, user: User) -> Comment:
    """
    Створює новий коментар для поста.
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
    Редагує коментар. Тільки автор або admin/moderator можуть редагувати.
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
    Видаляє коментар. Тільки автор або admin/moderator можуть видаляти.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment and (user.role in [UserRoleEnum.admin, UserRoleEnum.moder] or comment.user_id == user.id):
        db.delete(comment)
        db.commit()
        return comment
    return None


async def show_single_comment(comment_id: int, db: Session, user: User) -> Optional[Comment]:
    """
    Повертає конкретний коментар. Доступ лише автору або admin/moderator.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment and (comment.user_id == user.id or user.role in [UserRoleEnum.admin, UserRoleEnum.moder]):
        return comment
    return None


async def show_user_comments(user_id: int, db: Session) -> List[Comment]:
    """
    Повертає список всіх коментарів конкретного користувача.
    """
    return db.query(Comment).filter(Comment.user_id == user_id).all()


async def show_user_post_comments(user_id: int, post_id: int, db: Session) -> List[Comment]:
    """
    Повертає список коментарів конкретного користувача для певного поста.
    """
    return db.query(Comment).filter(
        and_(Comment.post_id == post_id, Comment.user_id == user_id)
    ).all()
