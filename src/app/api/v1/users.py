import json

from fastapi import APIRouter, Depends

from ...api.dependencies import get_current_user
from ...core.config import settings

router = APIRouter(prefix="/users", tags=["users"])

# TODO: route to check /me. if new user register in db, else return
# if paid, check payment expiry. if 1 day away from expiry return "will expire in one day"
# if today date > expiry, update db tier to free

# TODO: route for payment ---> update tier to paid if success each month

# TODO: create model for payment -> payment date, expiry date (1 month)

# TODO: route to update template of modality + organ


@router.get("/protected")
async def protected_route(session=Depends(get_current_user)):
    (sesh, email) = session
    print("sesh, email", sesh, email)

    # protected route things here

    pass


@router.get("/get-template", dependencies=[Depends(get_current_user)])
async def get_template(modality: str, organ: str):
    # TODO: check if there is any template entry in the user_id, modality, organ table
    # TODO: if yes pull that and send.
    # TODO ELSE:
    with open(settings.COMMON_TEMPLATE_PATH, "r") as f:
        json_data = json.load(f)

    return {"findings_template": json_data[modality.lower()][organ.lower()]}
