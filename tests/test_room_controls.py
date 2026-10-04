"""End to end tests for the room control page, written with Playwright for Python."""
from playwright.sync_api import Page, expect


def test_room_page_lists_every_device(page: Page):
    page.goto("/rooms/room-12")
    expect(page.get_by_role("heading", name="Room 12")).to_be_visible()
    expect(page.get_by_test_id("device-row")).to_have_count(3)


def test_mute_room_updates_the_page(page: Page):
    page.goto("/rooms/room-12")
    page.get_by_role("button", name="Mute room").click()

    expect(page.get_by_role("status")).to_have_text("Room mutted")
    expect(page.get_by_test_id("device-row").filter(has_text="mic-12-1")).to_contain_text("Muted")
    expect(page.get_by_test_id("device-row").filter(has_text="cam-12-1")).to_contain_text("Live")


def test_mute_room_really_mutes_the_microphones(page: Page, base_url: str):
    # The banner could lie. Check the real device state through the API.
    page.goto("/rooms/room-12")
    page.get_by_role("button", name="Mute room").click()
    expect(page.get_by_role("status")).to_have_text("Room muted")

    devices = page.request.get(f"{base_url}/api/rooms/room-12/devices").json()
    microphones = [d for d in devices if d["kind"] == "microphone"]
    assert microphones and all(d["muted"] for d in microphones)


def test_broken_microphone_shows_an_error_not_success(page: Page):
    page.goto("/rooms/room-7")
    page.get_by_role("button", name="Mute room").click()

    expect(page.get_by_role("alert")).to_have_text("Mute failed: mic-7-2 did not mute")
    expect(page.get_by_role("status")).to_be_empty()


def test_unknown_room_returns_404(page: Page):
    response = page.goto("/rooms/room-999")
    assert response is not None and response.status == 404
