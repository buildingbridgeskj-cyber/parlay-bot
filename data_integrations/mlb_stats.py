import requests
import pandas as pd
from datetime import datetime, timedelta

class MLBStatsIntegration:
    """Fetch MLB stats from MLB.com and other sources"""
    
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
        self.stats_cache = {}
    
    def get_upcoming_games(self, days_ahead=7):
        """Fetch upcoming MLB games"""
        try:
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)
            
            response = requests.get(
                f"{self.base_url}/schedule",
                params={'startDate': str(today), 'endDate': str(end_date)}
            )
            response.raise_for_status()
            games = response.json()
            
            upcoming = []
            for game in games:
                if game['status'] == 'Scheduled':
                    upcoming.append({
                        'id': game['gameId'],
                        'date': game['gameDateTime'],
                        'home_team': game['teams']['home']['team']['name'],
                        'away_team': game['teams']['away']['team']['name'],
                        'home_pitcher': game['teams']['home'].get('pitchers', [{}])[0].get('fullName'),
                        'away_pitcher': game['teams']['away'].get('pitchers', [{}])[0].get('fullName'),
                    })
            return upcoming
        except Exception as e:
            print(f"Error fetching MLB games: {e}")
            return []
    
    def get_pitcher_stats(self, pitcher_id):
        """Fetch detailed pitcher statistics"""
        try:
            response = requests.get(f"{self.base_url}/people/{pitcher_id}")
            response.raise_for_status()
            data = response.json()
            
            return {
                'name': data['people'][0]['fullName'],
                'era': data['people'][0].get('stats', [{}])[0].get('stats', {}).get('era'),
                'wins': data['people'][0].get('stats', [{}])[0].get('stats', {}).get('wins'),
                'strikeouts': data['people'][0].get('stats', [{}])[0].get('stats', {}).get('strikeOuts'),
                'innings_pitched': data['people'][0].get('stats', [{}])[0].get('stats', {}).get('inningsPitched'),
            }
        except Exception as e:
            print(f"Error fetching pitcher stats: {e}")
            return None
    
    def get_team_stats(self, team_id):
        """Fetch team statistics"""
        try:
            response = requests.get(f"{self.base_url}/teams/{team_id}")
            response.raise_for_status()
            data = response.json()
            
            return {
                'team': data['teams'][0]['name'],
                'record': data['teams'][0].get('record'),
                'run_differential': data['teams'][0].get('runDifferential'),
            }
        except Exception as e:
            print(f"Error fetching MLB team stats: {e}")
            return None
    
    def get_player_stats(self, player_id):
        """Fetch individual player statistics"""
        try:
            response = requests.get(f"{self.base_url}/people/{player_id}")
            response.raise_for_status()
            data = response.json()
            
            stats = data['people'][0].get('stats', [])
            return {
                'name': data['people'][0]['fullName'],
                'position': data['people'][0].get('primaryPosition', {}).get('name'),
                'batting': stats[0].get('stats') if len(stats) > 0 else {},
            }
        except Exception as e:
            print(f"Error fetching player stats: {e}")
            return None
