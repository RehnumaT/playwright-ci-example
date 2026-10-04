# Playwright CI/CD example with Claude Code

A small room control web app, a Playwright test suite in Python, and a GitHub Actions pipeline that runs the tests on every pull request. When a test fails, the pipeline saves the evidence and asks Claude Code to triage the failure.

## 1. Run it on your Mac

```bash
cd playwright-ci-example
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

# Terminal 1: start the app
uvicorn app:app --port 8000

# Terminal 2: run the tests (activate .venv here too)
pytest                              # 5 passed
pytest --headed --slowmo 500        # watch the browser click through each test
```

Open http://127.0.0.1:8000/rooms/room-12 to see the page yourself. Room 7 has a microphone that is broken on purpose.

## 2. See what a failure looks like

Change `"Room muted"` in `test_mute_room_updates_the_page` to `"Room mutted"` and run `pytest` again. Then open the evidence Playwright saved:

```bash
ls test-results/
playwright show-trace test-results/<test folder>/trace.zip
```

The trace shows every step, the page at each moment, network calls, and console logs. It's the fastest way to tell a product bug from a test bug. Change the text back when you're done.

## 3. Use Claude Code locally

`CLAUDE.md` holds the rules Claude Code follows in this repo: user facing locators, no sleeps, check the real outcome, and never change the app to make a test pass.

**Write tests with Claude Code.** Start `claude` in the project folder and try:

> Write a Playwright test for muting room-7 that proves mic-7-1 still gets muted even though mic-7-2 fails. Follow CLAUDE.md. Run pytest and fix only the test until it passes.

**Review what it writes before you commit.** Check for the mistakes AI tools commonly make in tests:
- brittle locators such as CSS classes or nth-child
- methods that don't exist in Playwright
- fixed waits instead of `expect(...)`
- weak assertions that would pass even if the feature were broken

**Run it headless, the way CI does:**

```bash
claude -p "Run pytest and explain any failures. Do not edit files." --allowedTools "Bash(pytest *),Read"
```

## 4. Run it in GitHub Actions

Push this folder to a GitHub repo. `.github/workflows/e2e.yml` runs on every pull request and every push to `main`:

1. Checks out the code and installs Python and the dependencies
2. Installs the Chromium browser for Playwright
3. Starts the app and waits until `/health` answers
4. Runs the Playwright tests and writes a JUnit report
5. **If anything fails:** uploads the traces, screenshots, and app log as a downloadable artifact
6. **If anything fails:** runs Claude Code to classify each failure and suggest a fix, in the workflow log

The Claude Code step needs a key. The easy way is to run `/install-github-app` inside Claude Code in this repo. Or add a repository secret called `ANTHROPIC_API_KEY` yourself under **Settings, Secrets and variables, Actions**. Without the secret, the tests still run; only the triage step fails.

To see the full loop, open a pull request with the typo from step 2. The tests go red, the artifact appears on the run page, and Claude Code's triage report shows in the log.

## How to talk about it

"My Playwright suite runs in GitHub Actions on every pull request. Every test starts from a known state, uses user facing locators and auto waiting assertions, and checks the real outcome through the API, not just the message on screen. When a test fails, the pipeline keeps the trace and screenshot, and a Claude Code step classifies the failure as a product bug, test bug, flaky timing, or environment problem, so triage starts with evidence instead of a rerun."
