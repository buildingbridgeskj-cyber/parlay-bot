# Parlay Bot 🎯

An AI-powered sports betting parlay generator that delivers 3-5 daily parlays with 6-8 legs each at **9:00 AM EST**.

## Features

✅ **Daily Parlay Generation** - Automatically generates 3-5 optimized parlays daily
✅ **Multi-Sport Support** - Analyzes NFL and MLB games
✅ **Advanced Edge Detection** - Identifies +EV (positive expected value) opportunities
✅ **DraftKings Integration** - Real-time odds and line shopping
✅ **Scheduled Delivery** - 9:00 AM EST daily delivery via email
✅ **Statistical Analysis** - Uses pitcher stats, team stats, and performance metrics
✅ **Injury Report Integration** - Accounts for team injuries and roster changes

## Project Structure

```
parlay-bot/
├── config.py                          # Configuration and environment variables
├── main.py                            # Main entry point
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
│
├── data_integrations/
│   ├── nfl_stats.py                   # NFL data from ESPN API
│   ├── mlb_stats.py                   # MLB data from MLB.com API
│   └── draftkings_integration.py      # DraftKings odds and authentication
│
├── edge_detection/
│   └── edge_finder.py                 # +EV opportunity detection
│
├── agent/
│   └── parlay_agent.py                # Parlay generation logic
│
├── scheduler/
│   └── delivery_scheduler.py           # 9:00 AM EST scheduling
│
├── notifications/
│   └── delivery_service.py            # Email delivery service
│
└── reports/                           # Generated parlay reports
```

## Setup

### 1. Clone Repository
```bash
git clone https://github.com/buildingbridgeskj-cyber/parlay-bot.git
cd parlay-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials:
# - DraftKings username/password
# - API keys for ESPN, Sports Radar
# - Notification email
```

### 4. Run Bot
```bash
# Test mode (runs once)
python main.py

# Or uncomment in main.py for scheduled delivery
# engine.start()  # Runs daily at 9:00 AM EST
```

## Configuration

Edit `config.py` to customize:
- **Parlays per day**: 3-5 (default)
- **Legs per parlay**: 6-8 (default)
- **Confidence threshold**: 55% (default)
- **Delivery time**: 9:00 AM EST (default)
- **Sports**: NFL, MLB (customizable)

## Data Sources

- **NFL Stats**: ESPN API
- **MLB Stats**: MLB.com Statsapi
- **DraftKings Odds**: Official DraftKings API (with auth)
- **Advanced Stats**: Team performance, pitcher stats, injury reports

## Edge Detection Algorithm

The bot identifies +EV opportunities using:
1. **Win Probability** - Calculated from historical performance and current stats
2. **Decimal Odds** - Converted from American odds via DraftKings
3. **EV Calculation** - `(Win Probability × Decimal Odds) - 1`
4. **Parlay Assembly** - Selects 6-8 high-confidence legs to maximize combined EV

## Output

Daily reports include:
- 3-5 parlays with 6-8 legs each
- Win probabilities per leg
- Decimal odds and potential payouts
- Overall parlay EV percentage
- Confidence ratings

Example:
```
================================================================================
PARLAY BOT RECOMMENDATIONS - 2026-08-19 09:00:00
================================================================================

📊 PARLAY_1
   Legs: 7 | Odds: 45.23 | EV: 12.3%
   Confidence: 67.2%

   Leg 1: Kansas City Chiefs (NFL)
      Odds: 1.91 | Win%: 65.0%
   
   Leg 2: New York Mets (MLB)
      Odds: 1.75 | Win%: 62.5%
   
   ...

================================================================================
```

## Delivery

Parlay recommendations are delivered via:
- 📧 Email at 9:00 AM EST daily
- 💾 Saved reports in `/reports/` directory
- 📱 SMS notifications (optional, requires Twilio)

## Dependencies

- `requests` - HTTP client for APIs
- `beautifulsoup4` - Web scraping (DraftKings)
- `pandas` - Data analysis
- `numpy` - Numerical computing
- `scipy` - Statistical functions
- `scikit-learn` - ML models (future enhancement)
- `apscheduler` - Scheduled tasks
- `python-dotenv` - Environment variables

## Future Enhancements

- [ ] Machine Learning model for win probability
- [ ] Kelly Criterion for optimal bet sizing
- [ ] More sportsbooks (FanDuel, BetMGM, etc.)
- [ ] Parlay tracking and ROI analysis
- [ ] Web dashboard for monitoring
- [ ] Advanced injury report integration
- [ ] Weather impact analysis
- [ ] Team strength of schedule factors

## Disclaimer

This tool is for educational purposes. Sports betting involves risk. Always gamble responsibly.

## License

MIT
