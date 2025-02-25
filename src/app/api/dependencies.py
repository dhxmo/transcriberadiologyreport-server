import asyncio

import jwt
from clerk_backend_api import Clerk
from clerk_backend_api.models import ClerkErrors, SDKError
from fastapi import HTTPException, Request, Query, WebSocket, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from ..core.config import settings
from ..core.logger import logging

logger = logging.getLogger(__name__)


# Function to retrieve the primary email address from a session ID
def get_email_from_session(clerk_client, session):
    try:
        # Extract the user ID from the session
        user_id = session.user_id

        # Fetch the user details
        user = clerk_client.users.get(user_id=user_id)
        if not user:
            print(f"No user found for ID: {user_id}")
            return None

        # Access the primary email address
        primary_email_id = user.primary_email_address_id
        if not primary_email_id:
            print(f"No primary email address set for user ID: {user_id}")
            return None

        # Find the email address object that matches the primary email ID
        primary_email = next(
            (
                email.email_address
                for email in user.email_addresses
                if email.id == primary_email_id
            ),
            None,
        )

        if primary_email:
            return primary_email
        else:
            print(f"Primary email address not found for user ID: {user_id}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# TODO: if new user create entry in db


# Dependency function to get the current authenticated user
async def get_current_user(request: Request, session_id: str = Query(...)):
    # Get the session token from the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    # Expected format: 'Bearer <session_token>'
    if not auth_header.startswith("Bearer "):
        print("Invalid authorization header format. Expected 'Bearer <session_token>'")
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )

    try:
        with Clerk(bearer_auth=settings.CLERK_SECRET_KEY) as clerk_client:
            # Verify the session with Clerk
            loop = asyncio.get_event_loop()
            session = await loop.run_in_executor(
                None, lambda: clerk_client.sessions.get(session_id=session_id)
            )
            email = await loop.run_in_executor(
                None,
                lambda: get_email_from_session(
                    clerk_client=clerk_client, session=session
                ),
            )

            return session, email
    except ClerkErrors as e:
        # Handle Clerk-specific errors
        print(f"Clerk error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    except SDKError as e:
        # Handle general SDK errors
        print(f"SDK error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def ws_get_current_user(websocket: WebSocket, session_id: str = Query(...)):
    if not session_id:
        await websocket.close(code=1008)
        raise HTTPException(status_code=401, detail="Session ID missing")

    try:
        with Clerk(
            bearer_auth=settings.CLERK_SECRET_KEY, debug_logger=logger
        ) as clerk_client:
            # Verify the session with Clerk
            loop = asyncio.get_event_loop()
            session = await loop.run_in_executor(
                None, lambda: clerk_client.sessions.get(session_id=session_id)
            )
            email = await loop.run_in_executor(
                None,
                lambda: get_email_from_session(
                    clerk_client=clerk_client, session=session
                ),
            )
            return email
    except ClerkErrors as e:
        # Handle Clerk-specific errors
        print(f"Clerk error: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    except SDKError as e:
        # Handle general SDK errors
        print(f"SDK error: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Internal server error"
        )
