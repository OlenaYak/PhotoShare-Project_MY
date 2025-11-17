from typing import List
from datetime import datetime
from fastapi import Request, UploadFile
from faker import Faker
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from app.conf.config import init_cloudinary
from app.database.models import Post, Hashtag, User, Comment, UserRoleEnum
from app.schemas import PostUpdate

# Ініціалізація Cloudinary один раз
init_cloudinary()


async def create_post(
    request: Request,
    title: str,
    descr: str,
    hashtags: List[str],
    file: UploadFile,
    db: Session,
    current_user: User
) -> Post:
    public_id = Faker().first_name()
    upload_result = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    url = upload_result.get("secure_url")

    tag_objs = []
    if hashtags:
        tag_objs = get_hashtags([tag.strip() for tag in hashtags[0].split(",")], current_user, db)

    post = Post(
        image_url=url,
        title=title,
        descr=descr,
        created_at=datetime.now(),
        user_id=current_user.id,
        hashtags=tag_objs,
        public_id=public_id,
        done=True
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


async def get_all_posts(skip: int, limit: int, db: Session) -> List[Post]:
    return db.query(Post).offset(skip).limit(limit).all()


async def get_my_posts(skip: int, limit: int, user: User, db: Session) -> List[Post]:
    return db.query(Post).filter(Post.user_id == user.id).offset(skip).limit(limit).all()


async def get_post_by_id(post_id: int, user: User, db: Session) -> Post | None:
    return db.query(Post).filter(and_(Post.user_id == user.id, Post.id == post_id)).first()


async def get_posts_by_title(post_title: str, user: User, db: Session) -> List[Post]:
    return db.query(Post).filter(func.lower(Post.title).like(f'%{post_title.lower()}%')).all()


async def get_posts_by_user_id(user_id: int, db: Session) -> List[Post]:
    return db.query(Post).filter(Post.user_id == user_id).all()


async def get_posts_by_username(user_name: str, db: Session) -> List[Post]: 
    searched_user = db.query(User).filter(func.lower(User.username).like(f'%{user_name.lower()}%')).first()
    if searched_user:
        return db.query(Post).filter(Post.user_id == searched_user.id).all()
    return []


async def get_posts_with_hashtag(hashtag_name: str, db: Session) -> List[Post]: 
    return db.query(Post).join(Post.hashtags).filter(Hashtag.title == hashtag_name).all()


async def get_post_comments(post_id: int, db: Session) -> List[Comment]: 
    return db.query(Comment).filter(Comment.post_id == post_id).all()


def get_hashtags(hashtag_titles: list, user: User, db: Session):
    tags = []
    for tag_title in hashtag_titles:
        tag = db.query(Hashtag).filter(Hashtag.title == tag_title).first()
        if not tag:
            tag = Hashtag(title=tag_title, user_id=user.id)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)
    return tags


async def get_post_by_keyword(keyword: str, db: Session) -> List[Post]:
    return db.query(Post).filter(or_(
        func.lower(Post.title).like(f'%{keyword.lower()}%'),
        func.lower(Post.descr).like(f'%{keyword.lower()}%')
    )).all()


async def update_post(post_id: int, body: PostUpdate, user: User, db: Session) -> Post | None:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post and (user.role == UserRoleEnum.admin or post.user_id == user.id):
        hashtags = []
        if body.hashtags:
            hashtags = get_hashtags(body.hashtags, user, db)
        post.title = body.title
        post.descr = body.descr
        post.hashtags = hashtags
        post.updated_at = datetime.now()
        post.done = True
        db.commit()
    return post


async def remove_post(post_id: int, user: User, db: Session) -> Post | None:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post and (user.role == UserRoleEnum.admin or post.user_id == user.id):
        cloudinary.uploader.destroy(post.public_id)
        db.delete(post)
        db.commit()
    return post
