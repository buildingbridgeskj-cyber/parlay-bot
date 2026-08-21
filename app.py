import json
import math
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("DB_PATH", "parlay_bot.db"))
STARTING_BANKROLL = float(os.getenv("STARTING_BANKROLL", "1000"))
EDGE_THRESHOLD = float(os.getenv("EDGE_THRESHOLD", "0.05"))

app = FastAPI(title="Parlay Bot", version="0.1.0")


class Pick(BaseModel):
    sport: str
    event: str
    market: str
    selection: str
    american_odds: int = Field(default=-110)
    model_probability: float = Field(gt=0, lt=1)
    source: str = "manual"


class BetResult(BaseModel):
    pick_id: int
    result: str = Field(pattern="^(win|loss|push)$")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            sport TEXT NOT NULL,
            event TEXT NOT NULL,
            market TEXT NOT NULL,
            selection TEXT NOT NULL,
            american_odds INTEGER NOT NULL,
            model_probability REAL NOT NULL,
            implied_probability REAL NOT NULL,
            edge REAL NOT NULL,
            recommendation TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open'
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS paper_bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pick_id INTEGER NOT NULL,
            stake REAL NOT NULL,
            result TEXT,
            pnl REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(pick_id) REFERENCES picks(id)
        )""")
        conn.commit()


def implied_probability(american_odds: int) -> float:
    if american_odds < 0:
        return (-american_odds) / ((-american_odds) + 100)
    return 100 / (american_odds + 100)


def decimal_odds(american_odds: int) -> float:
    if american_odds < 0:
        return 1 + 100 / (-american_odds)
    return 1 + american_odds / 100


def expected_value(model_probability: float, american_odds: int) -> float:
    d = decimal_odds(american_odds)
    return model_probability * (d - 1) - (1 - model_probability)


def recommendation(edge: float) -> str:
    if edge >= EDGE_THRESHOLD:
        return "BET"
    if edge >= 0:
        return "WATCH"
    return "PASS"


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "mode": "paper", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/picks")
def list_picks():
    with db() as conn:
        rows = conn.execute("SELECT * FROM picks ORDER BY id DESC LIMIT 100").fetchall()
    return [dict(r) for r in rows]


@app.post("/api/picks")
def create_pick(pick: Pick):
    implied = implied_probability(pick.american_odds)
    edge = pick.model_probability - implied
    rec = recommendation(edge)
    with db() as conn:
        cur = conn.execute(
            """INSERT INTO picks (created_at,sport,event,market,selection,american_odds,
            model_probability,implied_probability,edge,recommendation,source)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (datetime.now(timezone.utc).isoformat(), pick.sport, pick.event, pick.market,
             pick.selection, pick.american_odds, pick.model_probability, implied, edge, rec, pick.source),
        )
        conn.commit()
        return {"id": cur.lastrowid, "implied_probability": implied, "edge": edge, "recommendation": rec}


@app.post("/api/paper-bet")
def paper_bet(result: BetResult):
    with db() as conn:
        pick = conn.execute("SELECT * FROM picks WHERE id=?", (result.pick_id,)).fetchone()
        if not pick:
            raise HTTPException(status_code=404, detail="Pick not found")
        stake = STARTING_BANKROLL * 0.01
        if result.result == "win":
            pnl = stake * (decimal_odds(pick["american_odds"]) - 1)
        elif result.result == "loss":
            pnl = -stake
        else:
            pnl = 0
        conn.execute("INSERT INTO paper_bets (pick_id,stake,result,pnl,created_at) VALUES (?,?,?,?,?)",
                     (result.pick_id, stake, result.result, pnl, datetime.now(timezone.utc).isoformat()))
        conn.execute("UPDATE picks SET status=? WHERE id=?", (result.result, result.pick_id))
        conn.commit()
        return {"pick_id": result.pick_id, "stake": stake, "result": result.result, "pnl": pnl}


@app.get("/api/stats")
def stats():
    with db() as conn:
        row = conn.execute("""SELECT
            COUNT(*) AS bets,
            COALESCE(SUM(CASE WHEN result='win' THEN 1 ELSE 0 END),0) AS wins,
            COALESCE(SUM(CASE WHEN result='loss' THEN 1 ELSE 0 END),0) AS losses,
            COALESCE(SUM(pnl),0) AS pnl
            FROM paper_bets""").fetchone()
    bets = row["bets"] or 0
    wins = row["wins"] or 0
    return {
        "bets": bets,
        "wins": wins,
        "losses": row["losses"] or 0,
        "win_rate": wins / bets if bets else 0,
        "pnl": row["pnl"] or 0,
        "starting_bankroll": STARTING_BANKROLL,
        "bankroll": STARTING_BANKROLL + (row["pnl"] or 0),
    }


HTML = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Parlay Bot</title><style>body{font-family:system-ui;margin:0;background:#0d1117;color:#f0f6fc}main{max-width:1000px;margin:auto;padding:24px}h1{margin-bottom:4px}.muted{color:#8b949e}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px}.pick{margin-top:12px}.bet{font-weight:700}.BET{color:#3fb950}.WATCH{color:#d29922}.PASS{color:#f85149}button{background:#238636;color:white;border:0;border-radius:8px;padding:10px 14px}code{background:#21262d;padding:2px 5px;border-radius:4px}</style></head>
<body><main><h1>Parlay Bot</h1><div class='muted'>Paper-trading mode • no sportsbook account automation</div><div id='stats' class='grid' style='margin-top:20px'></div><h2>Latest model picks</h2><div id='picks'></div><p class='muted'>Enter picks through <code>POST /api/picks</code>. This first version intentionally keeps wager submission manual.</p></main>
<script>async function load(){const s=await (await fetch('/api/stats')).json();document.getElementById('stats').innerHTML=`<div class='card'><b>Bankroll</b><h2>$${s.bankroll.toFixed(2)}</h2></div><div class='card'><b>P/L</b><h2>$${s.pnl.toFixed(2)}</h2></div><div class='card'><b>Bets</b><h2>${s.bets}</h2></div><div class='card'><b>Win rate</b><h2>${(s.win_rate*100).toFixed(1)}%</h2></div>`;const p=await (await fetch('/api/picks')).json();document.getElementById('picks').innerHTML=p.map(x=>`<div class='card pick'><b>${x.sport} — ${x.event}</b><div>${x.market}: <strong>${x.selection}</strong></div><div>Odds ${x.american_odds} • Model ${(x.model_probability*100).toFixed(1)}% • Implied ${(x.implied_probability*100).toFixed(1)}% • Edge ${(x.edge*100).toFixed(1)}%</div><div class='bet ${x.recommendation}'>${x.recommendation}</div></div>`).join('')||'<div class="muted">No picks yet.</div>';}load();setInterval(load,10000)</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTML


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
