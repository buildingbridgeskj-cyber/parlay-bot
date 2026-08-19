import requests
import pandas as pd
from datetime import datetime, timedelta

class NFLStatsIntegration:
    """Fetch NFL stats from ESPN and other sources"""
    
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        self.stats_cache = {}
    
    def get_upcoming_games(self, days_ahead=7):
        """Fetch upcoming NFL games"""
        try:
            response = requests.get(f"{self.base_url}/scoreboard")
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                if event['status']['type']['completed'] is False:
                    games.append({
                        'id': event['id'],
                        'date': event['date'],
                        'home_team': event['competitions'][0]['home']['team']['displayName'],
                        'away_team': event['competitions'][0]['away']['team']['displayName'],
                        'home_odds': event['competitions'][0]['home'].get('odds', {}).get('moneyline'),
                        'away_odds': event['competitions'][0]['away'].get('odds', {}).get('moneyline'),
                    })
            return games
        except Exception as e:
            print(f"Error fetching NFL games: {e}")
            return []
    
    def get_team_stats(self, team_id):
        """Fetch team statistics"""
        try:
            response = requests.get(f"{self.base_url}/teams/{team_id}")
            response.raise_for_status()
            data = response.json()
            
            return {
                'team': data['team']['displayName'],
                'wins': data['team']['record'][0]['summary'],
                'stats': data['team'].get('stats', {}),
            }
        except Exception as e:
            print(f"Error fetching team stats: {e}")
            return None
    
    def get_player_props(self, game_id):
        """Fetch player prop opportunities"""
        try:
            response = requests.get(f"{self.base_url}/events/{game_id}")
            response.raise_for_status()
            data = response.json()
            
            props = []
            for competition in data.get('competitions', []):
                for article in competition.get('articles', []):
                    props.append({
                        'title': article.get('description'),
                        'source': article.get('links', [{}])[0].get('href')
                    })
            return props
        except Exception as e:
            print(f"Error fetching player props: {e}")
            return []
    
    def get_injury_reports(self):
        """Fetch NFL injury reports"""
        try:
            response = requests.get(f"{self.base_url}/injuries")
            response.raise_for_status()
            data = response.json()
            
            injuries = []
            for team_data in data.get('results', []):
                injuries.append({
                    'team': team_data['team']['displayName'],
                    'players': team_data.get('injuries', [])
                })
            return injuries
        except Exception as e:
            print(f"Error fetching injury reports: {e}")
            return []
