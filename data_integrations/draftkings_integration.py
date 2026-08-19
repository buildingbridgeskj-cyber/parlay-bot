import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DraftKingsIntegration:
    """Integration with DraftKings for odds and line shopping"""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://www.draftkings.com"
        self.authenticated = False
    
    def authenticate(self):
        """Authenticate with DraftKings"""
        try:
            login_url = f"{self.base_url}/api/v4/login"
            payload = {
                'email': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, json=payload)
            response.raise_for_status()
            
            self.authenticated = True
            logger.info("Successfully authenticated with DraftKings")
            return True
        except Exception as e:
            logger.error(f"DraftKings authentication failed: {e}")
            return False
    
    def get_available_sportsbooks(self):
        """Get list of available sportsbooks and odds"""
        try:
            response = self.session.get(f"{self.base_url}/api/v4/sportsbooks")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching sportsbooks: {e}")
            return []
    
    def get_nfl_odds(self):
        """Fetch current NFL odds from DraftKings"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v4/eventgroup/88808",  # NFL event group ID
            )
            response.raise_for_status()
            data = response.json()
            
            odds = []
            for event in data.get('events', []):
                odds.append({
                    'event_id': event['eventId'],
                    'name': event['name'],
                    'sport': 'NFL',
                    'odds': event.get('odds', [])
                })
            return odds
        except Exception as e:
            logger.error(f"Error fetching NFL odds: {e}")
            return []
    
    def get_mlb_odds(self):
        """Fetch current MLB odds from DraftKings"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v4/eventgroup/88052",  # MLB event group ID
            )
            response.raise_for_status()
            data = response.json()
            
            odds = []
            for event in data.get('events', []):
                odds.append({
                    'event_id': event['eventId'],
                    'name': event['name'],
                    'sport': 'MLB',
                    'odds': event.get('odds', [])
                })
            return odds
        except Exception as e:
            logger.error(f"Error fetching MLB odds: {e}")
            return []
    
    def get_parlay_odds(self, selections):
        """Calculate parlay odds for selected legs"""
        try:
            # DraftKings parlay calculation
            parlay_odds = 1.0
            for selection in selections:
                parlay_odds *= selection['odds']
            
            return {
                'legs': len(selections),
                'parlay_odds': parlay_odds,
                'implied_probability': 1 / parlay_odds,
                'potential_payout': parlay_odds * 100  # Assuming $100 bet
            }
        except Exception as e:
            logger.error(f"Error calculating parlay odds: {e}")
            return None
