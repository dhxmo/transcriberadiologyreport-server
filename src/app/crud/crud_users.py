from fastcrud import FastCRUD

from ..models.user import (
    User,
    UserCreateInternal,
    UserDelete,
    UserUpdate,
    UserUpdateInternal,
    UserTierUpdate,
)

CRUDUser = FastCRUD[
    User, UserCreateInternal, UserUpdate, UserUpdateInternal, UserDelete, UserTierUpdate
]
crud_users = CRUDUser(User)
