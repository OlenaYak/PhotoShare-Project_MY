from typing import List

from fastapi import Depends, HTTPException, status, Request

from app.database.models import User, UserRoleEnum
from app.services.auth import auth_service


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(auth_service.get_current_user)):
        """
        Перевіряє, чи має користувач одну з дозволених ролей.
        Використовується як Depends у FastAPI маршрутах.
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation forbidden"
            )
        return True