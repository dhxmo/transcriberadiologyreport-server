from clerk_backend_api import Clerk
from clerk_backend_api.models import ClerkErrors, SDKError
from fastapi import HTTPException, Request, Query

from ..core.config import settings
from ..core.logger import logging

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = settings.DEFAULT_RATE_LIMIT_LIMIT
DEFAULT_PERIOD = settings.DEFAULT_RATE_LIMIT_PERIOD

# Initialize Clerk client with the secret key
clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)


# Function to retrieve the primary email address from a session ID
def get_email_from_session(session_id):
    try:
        # Retrieve the session details
        session = clerk_client.sessions.get(session_id=session_id)
        if not session:
            print(f"No session found for ID: {session_id}")
            return None

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
        # Verify the session with Clerk
        # Note: We're using the synchronous `get` method here. Consider using the async version in production.
        res = clerk_client.sessions.get(session_id=session_id)
        email = get_email_from_session(session_id)

        # Return the session object
        return res, email

    except ClerkErrors as e:
        # Handle Clerk-specific errors
        print(f"Clerk error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    except SDKError as e:
        # Handle general SDK errors
        print(f"SDK error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
