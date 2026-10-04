import pytest
from playwright.sync_api import Page


@pytest.fixture(autouse=True)
def reset_app_state(page: Page, base_url: str):
    """Every test starts from a known state, so tests never depend on each other."""
    response = page.request.post(f"{base_url}/api/reset")
    assert response.ok, "could not reset the app before the test"
