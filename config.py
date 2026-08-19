import os
from dotenv import load_dotenv

load_dotenv()

# Parlay Configuration
PARLAYS_PER_DAY_MIN = 3
PARLAYS_PER_DAY_MAX = 5
LEGS_PER_PARLAY_MIN = 6
LEGS_PER_PARLAY_MAX = 8

# Schedule Configuration
DELIVERY_HOUR = 9
DELIVERY_MINUTE = 0
DELIVERY_TIMEZONE = "US/Eastern"

# Sports Configuration
SPORTS = ["NFL", "MLB"]
MIN_CONFIDENCE_THRESHOLD = 0.55  # 55% win probability for edge detection
MIN_ODDS_VALUE = -110  # Minimum acceptable odds

# DraftKings Configuration
DRAFTKINGS_BASE_URL = "https://www.draftkings.com"
DRAFTKINGS_USERNAME = os.getenv("DRAFTKINGS_USERNAME")
DRAFTKINGS_PASSWORD = os.getenv("DRAFTKINGS_PASSWORD")

# Data Sources
ESPN_API_KEY = os.getenv("ESPN_API_KEY")
SPORTS_RADAR_API_KEY = os.getenv("SPORTS_RADAR_API_KEY")

# Notification Settings
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
