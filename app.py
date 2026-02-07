import os
import urllib.parse
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Very simple state for v1 (single spectator session)
LATEST = {"text": ""}

# Static + template
app.mount("/static", StaticFiles(directory="static"), name="static")

def read_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/")
def root():
    # Standby page (same as /standby)
    html = read_template("templates/standby.html")
    return HTMLResponse(html)

@app.get("/standby")
def standby():
    html = read_template("templates/standby.html")
    return HTMLResponse(html)

@app.get("/latest")
def latest():
    return LATEST

@app.post("/push")
async def push(payload: dict):
    """
    Called by performer script.
    Body: {"text": "flower"}
    """
    text = (payload.get("text") or "").strip()
    if text:
        # Keep it simple: just store latest
        LATEST["text"] = text
    return {"ok": True, "text": LATEST["text"]}

@app.get("/search")
def search():
    text = (LATEST.get("text") or "").strip()

    # Consume-on-read
    LATEST["text"] = ""

    if not text:
        return RedirectResponse("https://www.google.com")

    q = urllib.parse.quote_plus(text)
    inner = f"https://www.google.com/search?tbm=isch&q={q}"
    redirect = f"https://www.google.com/url?q={urllib.parse.quote_plus(inner)}"
    return RedirectResponse(redirect)


@app.post("/reset")
async def reset():
    """
    Optional utility: clear latest word between shows.
    """
    LATEST["text"] = ""
    return {"ok": True}
