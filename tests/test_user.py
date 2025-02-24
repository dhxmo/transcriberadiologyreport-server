from fastapi.testclient import TestClient
from fastapi import Request

from src.app.api.dependencies import get_current_user
from src.app.main import app

client = TestClient(app)

# Mock data to be returned by the mocked dependency
mock_session = {
    "object": "session",
    "id": "sess_2tTzJX0mQXICirSChJbiZeB2z9W",
    "user_id": "user_2tDHt8UoNtTdFNOm4cz3yXrm72b",
    "client_id": "client_2tDGqsOVnQ7iTTwVYc6ydtTgzFF",
    "status": "active",
    "last_active_at": 1740390780036,
    "expire_at": 1740995580036,
    "abandon_at": 1742982780036,
    "updated_at": 1740390780103,
    "created_at": 1740390780039,
    "actor": None,
    "last_active_organization_id": None,
    "latest_activity": None,
}
mock_email = "test123@gmail.com"


# Define a mock dependency function
async def mock_get_current_user(request: Request, session_id: str):
    return mock_session, mock_email


# Override the dependency with the mock
app.dependency_overrides[get_current_user] = mock_get_current_user


def test_protected_route(client: TestClient) -> None:
    # Simulate a request to the protected route
    response = client.get(
        "/api/v1/protected",
        headers={
            "Authorization": "Bearer mock.token.aF3jj9icxk7Pls3i4Bfkd3zkExRIlfUnZPnRKEleaSBBFUKDyN3LkaFkpS2wXzhwVTHq1YW9Bgy9cUX8WsVTPiv7tybiuuN-p9bh1hPfsDO_f5AaHRjrHB28v8wbq2jTKO1JTpz6PkkU7j71zBTc1PSGtOgzyOZ2qGx33_O0_BngSAJ9NgksMwS1_gOITQ9IkXXFr17JIpJ40X_O2HXr5iaNooR0xGway1txmDI1rpoF9BnGHLs8_gHQOGUD4BofhOumUI91TdKqEHBbkDR6crr0rCQk6MYwLllcAgb96_duN88eYoXqm1yopWn4nl6F2puD9tiF20P4WGbJbJ6xPg"
        },
        params={"session_id": "sess_2tTzJX0mQXICirSChJbiZeB2z9W"},
    )

    # Print response content for debugging
    print(response.json())

    # Assert the response status code and content
    assert response.status_code == 200
