# Notes for Claude Code

## What this project is
A small FastAPI app (`app.py`) with a room control page, tested end to end with Playwright for Python (pytest-playwright).

## How to run
- Start the app: `uvicorn app:app --port 8000`
- Run the tests in another terminal: `pytest`
- Watch the browser: `pytest --headed --slowmo 500`
- Open a failure trace: `playwright show-trace test-results/<test folder>/trace.zip`

## Rules for writing Playwright tests
- Find elements the way a user would: `get_by_role`, `get_by_label`, `get_by_text`. Use `get_by_test_id` only when there is no accessible name. Never use CSS classes or XPath.
- Use `expect(...)` assertions, which wait automatically. Never use `time.sleep` or `wait_for_timeout`.
- Check the real outcome, not just the message on screen. After an action, confirm the state through the API with `page.request`.
- Every happy path test needs a matching failure test. A test that can't fail proves nothing.
- One behavior per test, with a name that says what it proves.
- Tests must not depend on each other. The autouse fixture in `tests/conftest.py` resets the app before every test.
- Never change `app.py` to make a test pass. If the app looks wrong, say so and stop.
