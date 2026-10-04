"""A small room control web app. It is the system under test for the Playwright suite.

Run it:   uvicorn app:app --port 8000
Open:     http://127.0.0.1:8000/rooms/room-12
"""
from __future__ import annotations

import copy
import html

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

# room-7 has a microphone that ignores commands on purpose, so tests can cover the failure path.
INITIAL_ROOMS = {
    "room-12": {
        "name": "Room 12",
        "devices": [
            {"device_id": "mic-12-1", "kind": "microphone", "muted": False, "responds": True},
            {"device_id": "mic-12-2", "kind": "microphone", "muted": False, "responds": True},
            {"device_id": "cam-12-1", "kind": "camera", "muted": False, "responds": True},
        ],
    },
    "room-7": {
        "name": "Room 7",
        "devices": [
            {"device_id": "mic-7-1", "kind": "microphone", "muted": False, "responds": True},
            {"device_id": "mic-7-2", "kind": "microphone", "muted": False, "responds": False},
        ],
    },
}

rooms = copy.deepcopy(INITIAL_ROOMS)
app = FastAPI(title="Room control")


def _room(room_id: str) -> dict:
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"unknown room {room_id}")
    return rooms[room_id]


def _public(device: dict) -> dict:
    return {k: v for k, v in device.items() if k != "responds"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/reset")
def reset() -> dict:
    """Put every room back to its starting state. Tests call this before each test."""
    global rooms
    rooms = copy.deepcopy(INITIAL_ROOMS)
    return {"status": "reset"}


@app.get("/api/rooms/{room_id}/devices")
def list_devices(room_id: str) -> list:
    return [_public(d) for d in _room(room_id)["devices"]]


@app.post("/api/rooms/{room_id}/mute")
def mute_room(room_id: str):
    mics = [d for d in _room(room_id)["devices"] if d["kind"] == "microphone"]
    for mic in mics:
        if mic["responds"]:
            mic["muted"] = True
    # Verify the real state, not just that the command was sent.
    not_muted = [m["device_id"] for m in mics if not m["muted"]]
    if not_muted:
        return JSONResponse(status_code=502, content={"status": "failed", "not_muted": not_muted})
    return {"status": "muted"}


PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 40px; }}
  table {{ border-collapse: collapse; margin: 16px 0; }}
  td, th {{ border: 1px solid #ccc; padding: 6px 12px; text-align: left; }}
  #status {{ color: #0a7a3a; }} #error {{ color: #b00020; }}
</style></head>
<body>
  <h1>{title}</h1>
  <table>
    <thead><tr><th>Device</th><th>Type</th><th>State</th></tr></thead>
    <tbody id="devices">{rows}</tbody>
  </table>
  <button id="mute">Mute room</button>
  <p id="status" role="status"></p>
  <p id="error" role="alert"></p>
<script>
  const roomId = {room_id_json};
  const row = d => `<tr data-testid="device-row"><td>${{d.device_id}}</td><td>${{d.kind}}</td>` +
                   `<td>${{d.muted ? "Muted" : "Live"}}</td></tr>`;
  async function refresh() {{
    const devices = await (await fetch(`/api/rooms/${{roomId}}/devices`)).json();
    document.getElementById("devices").innerHTML = devices.map(row).join("");
  }}
  document.getElementById("mute").addEventListener("click", async () => {{
    const status = document.getElementById("status");
    const error = document.getElementById("error");
    status.textContent = ""; error.textContent = "";
    const response = await fetch(`/api/rooms/${{roomId}}/mute`, {{ method: "POST" }});
    const body = await response.json();
    if (response.ok) {{
      status.textContent = "Room muted";
    }} else {{
      error.textContent = `Mute failed: ${{body.not_muted.join(", ")}} did not mute`;
    }}
    await refresh();
  }});
</script>
</body></html>"""


@app.get("/rooms/{room_id}", response_class=HTMLResponse)
def room_page(room_id: str) -> str:
    room = _room(room_id)
    rows = "".join(
        f'<tr data-testid="device-row"><td>{html.escape(d["device_id"])}</td>'
        f'<td>{html.escape(d["kind"])}</td><td>{"Muted" if d["muted"] else "Live"}</td></tr>'
        for d in room["devices"]
    )
    return PAGE.format(title=html.escape(room["name"]), rows=rows, room_id_json=f'"{room_id}"')
