import logging
from datetime import datetime
from itertools import combinations
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParlayAgent:
    """Main agent that generates parlay recommendations"""
    
    def __init__(self, config):
        self.config = config
        self.min_parlays = config['PARLAYS_PER_DAY_MIN']
        self.max_parlays = config['PARLAYS_PER_DAY_MAX']
        self.min_legs = config['LEGS_PER_PARLAY_MIN']
        self.max_legs = config['LEGS_PER_PARLAY_MAX']
        self.confidence_threshold = config['MIN_CONFIDENCE_THRESHOLD']
    
    def generate_parlays(self, nfl_edges, mlb_edges):
        """Generate 3-5 parlays with 6-8 legs each"""
        try:
            # Combine all edges
            all_edges = nfl_edges + mlb_edges
            
            # Filter by confidence threshold
            qualified_edges = [
                edge for edge in all_edges 
                if edge['confidence'] >= self.confidence_threshold
            ]
            
            if len(qualified_edges) < self.min_legs:
                logger.warning(f"Not enough qualified edges ({len(qualified_edges)}) to build parlays")
                return []
            
            parlays = []
            num_parlays = random.randint(self.min_parlays, self.max_parlays)
            
            for parlay_idx in range(num_parlays):
                # Randomly select 6-8 legs per parlay
                num_legs = random.randint(self.min_legs, self.max_legs)
                
                # Ensure we don't pick the same team twice
                available_edges = self._filter_conflicting_picks(qualified_edges)
                
                if len(available_edges) >= num_legs:
                    selected_legs = random.sample(available_edges, num_legs)
                    
                    parlay = {
                        'parlay_id': f"parlay_{parlay_idx + 1}",
                        'created_at': datetime.now().isoformat(),
                        'num_legs': len(selected_legs),
                        'legs': selected_legs,
                        'parlay_odds': self._calculate_parlay_odds(selected_legs),
                        'total_ev': sum([leg['ev_percentage'] for leg in selected_legs]),
                        'avg_confidence': sum([leg['confidence'] for leg in selected_legs]) / len(selected_legs)
                    }
                    
                    parlays.append(parlay)
            
            # Sort by average confidence
            parlays = sorted(parlays, key=lambda x: x['avg_confidence'], reverse=True)
            
            logger.info(f"Generated {len(parlays)} parlays")
            return parlays
        except Exception as e:
            logger.error(f"Error generating parlays: {e}")
            return []
    
    def _filter_conflicting_picks(self, edges):
        """Remove conflicting picks (same team in same game)"""
        seen_events = set()
        filtered = []
        
        for edge in sorted(edges, key=lambda x: x['confidence'], reverse=True):
            event = edge['event']
            if event not in seen_events:
                filtered.append(edge)
                seen_events.add(event)
        
        return filtered
    
    def _calculate_parlay_odds(self, legs):
        """Calculate combined parlay odds"""
        try:
            parlay_odds = 1.0
            for leg in legs:
                parlay_odds *= leg['decimal_odds']
            return parlay_odds
        except Exception as e:
            logger.error(f"Error calculating parlay odds: {e}")
            return 0
    
    def format_parlay_report(self, parlays):
        """Format parlays for delivery"""
        try:
            report = f"\n{'='*80}\n"
            report += f"PARLAY BOT RECOMMENDATIONS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"{'='*80}\n\n"
            
            for parlay in parlays:
                report += f"📊 {parlay['parlay_id'].upper()}\n"
                report += f"   Legs: {parlay['num_legs']} | Odds: {parlay['parlay_odds']:.2f} | EV: {parlay['total_ev']:.2f}%\n"
                report += f"   Confidence: {parlay['avg_confidence']*100:.1f}%\n\n"
                
                for idx, leg in enumerate(parlay['legs'], 1):
                    report += f"   Leg {idx}: {leg['pick']} ({leg['sport']})\n"
                    report += f"      Odds: {leg['decimal_odds']:.2f} | Win%: {leg['confidence']*100:.1f}%\n"
                
                report += f"\n"
            
            report += f"{'='*80}\n"
            return report
        except Exception as e:
            logger.error(f"Error formatting report: {e}")
            return ""
