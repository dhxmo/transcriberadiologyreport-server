from fastcrud import FastCRUD

from ..models.token_blacklist import (
    TokenBlacklist,
    TokenBlacklistCreate,
    TokenBlacklistUpdate, TokenBlacklistCreateInternal, TokenBlacklistUpdateInternal,
)

CRUDTokenBlacklist = FastCRUD[
    TokenBlacklist,
    TokenBlacklistCreate,
    TokenBlacklistCreateInternal,
    TokenBlacklistUpdate,
    TokenBlacklistUpdateInternal,
    None,
]
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
