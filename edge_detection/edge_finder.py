import numpy as np
import pandas as pd
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdgeFinder:
    """Identify +EV (positive expected value) betting opportunities"""
    
    def __init__(self, confidence_threshold=0.55, min_odds=-110):
        self.confidence_threshold = confidence_threshold
        self.min_odds = min_odds
    
    def calculate_win_probability(self, historical_data, current_stats):
        """Calculate win probability using statistical models"""
        try:
            # Simple Bayesian approach
            # Can be enhanced with more sophisticated ML models
            
            weighted_stats = current_stats.copy()
            recent_form = historical_data['recent_performance'].mean()
            season_avg = historical_data['season_average'].mean()
            
            # Weighted average: 60% recent, 40% season average
            predicted_outcome = (recent_form * 0.6) + (season_avg * 0.4)
            
            return predicted_outcome
        except Exception as e:
            logger.error(f"Error calculating win probability: {e}")
            return 0.5
    
    def calculate_ev(self, win_probability, decimal_odds):
        """Calculate Expected Value (EV) of a bet"""
        try:
            # EV = (Probability of Win * Decimal Odds) - 1
            ev = (win_probability * decimal_odds) - 1
            ev_percentage = ev * 100
            
            return {
                'ev': ev,
                'ev_percentage': ev_percentage,
                'is_positive': ev > 0
            }
        except Exception as e:
            logger.error(f"Error calculating EV: {e}")
            return None
    
    def american_to_decimal(self, american_odds):
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def find_nfl_edges(self, games, team_stats, odds_data):
        """Identify +EV opportunities in NFL games"""
        edges = []
        
        try:
            for game in games:
                home_team = game['home_team']
                away_team = game['away_team']
                
                # Get stats for both teams
                home_stats = team_stats.get(home_team, {})
                away_stats = team_stats.get(away_team, {})
                
                # Calculate home team win probability
                home_prob = self.calculate_win_probability(home_stats, {})
                
                # Get odds
                home_odds = self.american_to_decimal(game.get('home_odds', -110))
                
                # Calculate EV
                ev_result = self.calculate_ev(home_prob, home_odds)
                
                if ev_result and ev_result['is_positive']:
                    edges.append({
                        'sport': 'NFL',
                        'type': 'moneyline',
                        'event': f"{away_team} @ {home_team}",
                        'pick': home_team,
                        'win_probability': home_prob,
                        'decimal_odds': home_odds,
                        'ev_percentage': ev_result['ev_percentage'],
                        'confidence': home_prob
                    })
            
            # Sort by EV percentage
            edges = sorted(edges, key=lambda x: x['ev_percentage'], reverse=True)
            return edges
        except Exception as e:
            logger.error(f"Error finding NFL edges: {e}")
            return []
    
    def find_mlb_edges(self, games, pitcher_stats, team_stats, odds_data):
        """Identify +EV opportunities in MLB games"""
        edges = []
        
        try:
            for game in games:
                home_team = game['home_team']
                away_team = game['away_team']
                home_pitcher = game.get('home_pitcher')
                away_pitcher = game.get('away_pitcher')
                
                # Get pitcher stats
                home_pitcher_stats = pitcher_stats.get(home_pitcher, {})
                away_pitcher_stats = pitcher_stats.get(away_pitcher, {})
                
                # Calculate home team win probability based on pitcher performance
                home_prob = self.calculate_win_probability(home_pitcher_stats, {})
                
                # Get odds
                home_odds = self.american_to_decimal(game.get('home_odds', -110))
                
                # Calculate EV
                ev_result = self.calculate_ev(home_prob, home_odds)
                
                if ev_result and ev_result['is_positive']:
                    edges.append({
                        'sport': 'MLB',
                        'type': 'moneyline',
                        'event': f"{away_team} @ {home_team}",
                        'home_pitcher': home_pitcher,
                        'away_pitcher': away_pitcher,
                        'pick': home_team,
                        'win_probability': home_prob,
                        'decimal_odds': home_odds,
                        'ev_percentage': ev_result['ev_percentage'],
                        'confidence': home_prob
                    })
            
            # Sort by EV percentage
            edges = sorted(edges, key=lambda x: x['ev_percentage'], reverse=True)
            return edges
        except Exception as e:
            logger.error(f"Error finding MLB edges: {e}")
            return []
