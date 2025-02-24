from fastcrud import FastCRUD

from ..models.user import User, UserCreateInternal, UserUpdate, UserUpdateInternal

CRUDUser = FastCRUD[User, UserCreateInternal, UserUpdate, UserUpdateInternal, None]
crud_users = CRUDUser(User)
