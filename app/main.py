"""LLM CTF — application FastAPI servant l'API REST et l'interface web.

La progression du joueur est conservée en mémoire, indexée par un cookie de
session (mono-instance, suffisant pour un CTF local).
"""
import os
import secrets

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core import registry, llm

app = FastAPI(title="LLM CTF — OWASP Top 10")

BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Progression en mémoire : { session_id: set(challenge_id résolus) }
SOLVED: dict[str, set] = {}
COOKIE = "ctf_session"


def _session_id(request: Request) -> str:
    sid = request.cookies.get(COOKIE)
    if not sid or sid not in SOLVED:
        sid = sid or secrets.token_hex(16)
        SOLVED.setdefault(sid, set())
    return sid


def _solved(sid: str) -> set:
    return SOLVED.setdefault(sid, set())


def _attach_cookie(response, sid: str):
    response.set_cookie(COOKIE, sid, httponly=True, samesite="lax")
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    sid = _session_id(request)
    solved = _solved(sid)
    challenges = registry.all_challenges()
    resp = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "challenges": challenges,
            "solved": solved,
            "total": len(challenges),
            "done": len(solved),
        },
    )
    return _attach_cookie(resp, sid)


@app.get("/challenge/{cid}", response_class=HTMLResponse)
async def challenge_page(request: Request, cid: str):
    sid = _session_id(request)
    chal = registry.get(cid)
    if not chal:
        return RedirectResponse("/")
    resp = templates.TemplateResponse(
        "challenge.html",
        {
            "request": request,
            "c": chal,
            "is_solved": cid in _solved(sid),
        },
    )
    return _attach_cookie(resp, sid)


@app.post("/api/challenge/{cid}/chat")
async def challenge_chat(request: Request, cid: str):
    sid = _session_id(request)
    chal = registry.get(cid)
    if not chal:
        return JSONResponse({"error": "challenge inconnu"}, status_code=404)

    body = await request.json()
    user_input = (body.get("message") or "").strip()
    if not user_input:
        return JSONResponse({"error": "message vide"}, status_code=400)

    try:
        result = await chal.respond(user_input)
    except Exception as exc:  # erreur LLM / réseau
        return JSONResponse(
            {"error": f"Le modèle n'a pas répondu : {exc}"}, status_code=502
        )

    out = {"reply": result["reply"], "objective_met": result["objective_met"]}
    if result["objective_met"]:
        out["flag"] = chal.flag  # révélé uniquement quand l'objectif est atteint
    resp = JSONResponse(out)
    return _attach_cookie(resp, sid)


@app.post("/api/submit")
async def submit_flag(request: Request, flag: str = Form(...)):
    sid = _session_id(request)
    owner = registry.flag_owner(flag)
    if owner:
        _solved(sid).add(owner)
        resp = JSONResponse({"correct": True, "challenge": owner})
    else:
        resp = JSONResponse({"correct": False})
    return _attach_cookie(resp, sid)


@app.get("/api/health")
async def health():
    """Vérifie que l'app et le LLM répondent."""
    try:
        reply = await llm.chat(
            [{"role": "user", "content": "Réponds uniquement: OK"}], max_tokens=5
        )
        return {"app": "ok", "llm": "ok", "sample": reply.strip()}
    except Exception as exc:
        return JSONResponse({"app": "ok", "llm": "ko", "error": str(exc)}, status_code=503)
