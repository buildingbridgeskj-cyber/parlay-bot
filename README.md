# Parlay Bot

A sports-analysis and paper-betting service designed for a phone-friendly dashboard and cloud deployment.

## Current status

**Paper mode only.** This repository does not automate sportsbook logins, clicks, wager submissions, or account actions. The dashboard is designed to analyze opportunities and track simulated results while the user makes any real-world wagering decision manually.

## Included in v0.1

- FastAPI web service
- Mobile-friendly dashboard
- Pick ingestion endpoint
- American-odds to implied-probability conversion
- Model probability vs. implied probability edge calculation
- BET / WATCH / PASS recommendation threshold
- SQLite paper-bet ledger
- Bankroll and ROI-style performance statistics
- Docker configuration for Google Cloud deployment
- No secrets committed to the repository

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8080
```

Open `http://localhost:8080`.

## Add a simulated model pick

`POST /api/picks` with JSON such as:

```json
{
  "sport": "NBA",
  "event": "Example Team A vs Example Team B",
  "market": "Moneyline",
  "selection": "Example Team A",
  "american_odds": -110,
  "model_probability": 0.57,
  "source": "model"
}
```

The service calculates the implied probability and model edge. A positive edge is not a guarantee of profit.

## Next build stages

1. Add a licensed/authorized sports-data feed.
2. Add historical data and backtesting.
3. Add player/team feature engineering and model evaluation.
4. Add platform-specific line/market adapters where permitted.
5. Deploy the service to Google Cloud.
6. Add authentication before exposing the dashboard publicly.
7. Add alerts and paper-bet settlement automation.
8. Keep real-money wager submission manual unless an official platform integration explicitly permits automation.

## Security

Do not put sportsbook passwords, API keys, session cookies, or other credentials in GitHub. Use environment variables or Google Cloud Secret Manager when credentials are actually required.
