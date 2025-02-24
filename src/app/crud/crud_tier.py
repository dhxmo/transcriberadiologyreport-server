from fastcrud import FastCRUD

from ..models.tier import (
    Tier,
    TierCreateInternal,
    TierDelete,
    TierUpdate,
    TierUpdateInternal,
    TierCreate,
)

CRUDTier = FastCRUD[
    Tier, TierCreate, TierCreateInternal, TierUpdate, TierUpdateInternal, TierDelete
]
crud_tiers = CRUDTier(Tier)
