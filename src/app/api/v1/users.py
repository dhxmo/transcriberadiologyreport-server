from fastapi import APIRouter, Depends

from fastapi import APIRouter, Depends

from ...api.dependencies import get_current_user

router = APIRouter(tags=["users"])

# route to create new user as free

# route to update tier to paid if payment success each month


@router.get("/protected")
async def protected_route(session=Depends(get_current_user)):
    (sesh, email) = session

    # protected route things here

    pass
