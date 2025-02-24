from fastcrud import FastCRUD

from ..models.rate_limit import (
    RateLimit,
    RateLimitCreateInternal,
    RateLimitDelete,
    RateLimitUpdate,
    RateLimitUpdateInternal,
    RateLimitCreate,
)

CRUDRateLimit = FastCRUD[
    RateLimit,
    RateLimitCreate,
    RateLimitCreateInternal,
    RateLimitUpdate,
    RateLimitUpdateInternal,
    RateLimitDelete,
]
crud_rate_limits = CRUDRateLimit(RateLimit)
