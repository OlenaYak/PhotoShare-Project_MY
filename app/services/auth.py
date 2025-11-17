import pickle
from typing import Optional

import redis.asyncio as aioredis
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database.connect_db import get_db
from app.repository import users as repository_users
from app.conf.config import settings
from app.conf.messages import FAIL_EMAIL_VERIFICATION, INVALID_SCOPE, NOT_VALIDATE_CREDENTIALS
from app.database.models import User
from app.conf.messages import INVALID_TOKEN

security = HTTPBearer()

class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def __init__(self):
        self.redis_cache = aioredis.from_url(settings.redis_url, decode_responses=False)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({
            "iat": datetime.utcnow(),
            "exp": expire,
            "scope": "access_token"
        })
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({
            "iat": datetime.utcnow(),
            "exp": expire,
            "scope": "refresh_token"
        })
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=3)
        to_encode.update({
            "iat": datetime.utcnow(),
            "exp": expire,
            "scope": "email_token"
        })
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get('scope') != 'refresh_token':
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_SCOPE)
            return payload.get('sub')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_VALIDATE_CREDENTIALS)

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NOT_VALIDATE_CREDENTIALS
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get('scope') != 'access_token':
                raise credentials_exception
            email = payload.get("sub")
            if not email:
                raise credentials_exception

            # Перевірка чорного списку
            black_list_token = await repository_users.find_blacklisted_token(token, db)
            if black_list_token:
                raise credentials_exception

            # Отримання користувача з кешу Redis
            user_data = await self.redis_cache.get(f"user:{email}")
            if user_data:
                user = pickle.loads(user_data)
            else:
                user = await repository_users.get_user_by_email(email, db)
                if not user:
                    raise credentials_exception
                await self.redis_cache.set(f"user:{email}", pickle.dumps(user), ex=900)

            return user

        except JWTError:
            raise credentials_exception

            # Отримання користувача з кешу Redis
            user_data = await self.redis_cache.get(f"user:{email}")
            if user_data:
                user = pickle.loads(user_data)
            else:
                user = await repository_users.get_user_by_email(email, db)
                if not user:
                    raise credentials_exception
                await self.redis_cache.set(f"user:{email}", pickle.dumps(user), ex=900)

            return user

        except JWTError:
            raise credentials_exception

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get('scope') != 'email_token':
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_SCOPE)
            return payload.get("sub")
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=FAIL_EMAIL_VERIFICATION
            )


auth_service = Auth()
