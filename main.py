#!/usr/bin/env python3
"""
Parlay Bot - Daily Sports Betting Parlay Generator
Generates 3-5 parlays with 6-8 legs each daily, delivered at 9:00 AM EST
"""

import logging
import time
from datetime import datetime

from config import (
    PARLAYS_PER_DAY_MIN, PARLAYS_PER_DAY_MAX,
    LEGS_PER_PARLAY_MIN, LEGS_PER_PARLAY_MAX,
    DELIVERY_HOUR, DELIVERY_MINUTE, DELIVERY_TIMEZONE,
    MIN_CONFIDENCE_THRESHOLD, NOTIFICATION_EMAIL
)

from data_integrations.nfl_stats import NFLStatsIntegration
from data_integrations.mlb_stats import MLBStatsIntegration
from data_integrations.draftkings_integration import DraftKingsIntegration
from edge_detection.edge_finder import EdgeFinder
from agent.parlay_agent import ParlayAgent
from scheduler.delivery_scheduler import DeliveryScheduler
from notifications.delivery_service import DeliveryService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ParlayBotEngine:
    """Main engine that orchestrates the entire parlay bot system"""
    
    def __init__(self):
        logger.info("Initializing Parlay Bot Engine...")
        
        # Initialize data sources
        self.nfl_stats = NFLStatsIntegration()
        self.mlb_stats = MLBStatsIntegration()
        self.draftkings = DraftKingsIntegration(
            username="your_username",  # From .env
            password="your_password"    # From .env
        )
        
        # Initialize edge detection
        self.edge_finder = EdgeFinder(
            confidence_threshold=MIN_CONFIDENCE_THRESHOLD
        )
        
        # Initialize agent
        config = {
            'PARLAYS_PER_DAY_MIN': PARLAYS_PER_DAY_MIN,
            'PARLAYS_PER_DAY_MAX': PARLAYS_PER_DAY_MAX,
            'LEGS_PER_PARLAY_MIN': LEGS_PER_PARLAY_MIN,
            'LEGS_PER_PARLAY_MAX': LEGS_PER_PARLAY_MAX,
            'MIN_CONFIDENCE_THRESHOLD': MIN_CONFIDENCE_THRESHOLD,
        }
        self.agent = ParlayAgent(config)
        
        # Initialize scheduler and delivery
        self.scheduler = DeliveryScheduler(
            delivery_hour=DELIVERY_HOUR,
            delivery_minute=DELIVERY_MINUTE,
            timezone=DELIVERY_TIMEZONE
        )
        self.delivery_service = DeliveryService(NOTIFICATION_EMAIL)
        
        logger.info("Parlay Bot Engine initialized successfully")
    
    def run_analysis(self):
        """Run the complete parlay analysis and generation"""
        try:
            logger.info("Starting parlay analysis...")
            
            # Step 1: Fetch data
            logger.info("Fetching NFL games...")
            nfl_games = self.nfl_stats.get_upcoming_games()
            logger.info(f"Found {len(nfl_games)} upcoming NFL games")
            
            logger.info("Fetching MLB games...")
            mlb_games = self.mlb_stats.get_upcoming_games()
            logger.info(f"Found {len(mlb_games)} upcoming MLB games")
            
            # Step 2: Authenticate DraftKings
            logger.info("Authenticating DraftKings...")
            self.draftkings.authenticate()
            
            # Step 3: Find edges
            logger.info("Finding NFL edges...")
            nfl_edges = self.edge_finder.find_nfl_edges(
                nfl_games, {}, []
            )
            logger.info(f"Found {len(nfl_edges)} NFL edges")
            
            logger.info("Finding MLB edges...")
            mlb_edges = self.edge_finder.find_mlb_edges(
                mlb_games, {}, {}, []
            )
            logger.info(f"Found {len(mlb_edges)} MLB edges")
            
            # Step 4: Generate parlays
            logger.info("Generating parlays...")
            parlays = self.agent.generate_parlays(nfl_edges, mlb_edges)
            logger.info(f"Generated {len(parlays)} parlays")
            
            # Step 5: Format and deliver
            if parlays:
                report = self.agent.format_parlay_report(parlays)
                logger.info("Report formatted")
                
                # Save report
                self.delivery_service.save_report(report)
                
                # Send email
                self.delivery_service.send_email(report)
                
                return report
            else:
                logger.warning("No parlays generated")
                return None
        
        except Exception as e:
            logger.error(f"Error during analysis: {e}", exc_info=True)
            return None
    
    def start(self):
        """Start the parlay bot with scheduled delivery"""
        try:
            logger.info(f"Starting Parlay Bot - Daily delivery at {DELIVERY_HOUR}:{DELIVERY_MINUTE:02d} {DELIVERY_TIMEZONE}")
            
            # Start scheduler
            self.scheduler.start(self.run_analysis)
            
            logger.info("Parlay Bot is running. Press Ctrl+C to stop.")
            
            # Keep running
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Stopping Parlay Bot...")
            self.scheduler.stop()
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            self.scheduler.stop()
    
    def run_once(self):
        """Run analysis once (useful for testing)"""
        logger.info("Running one-time analysis...")
        return self.run_analysis()


if __name__ == "__main__":
    engine = ParlayBotEngine()
    
    # For testing, run once
    # report = engine.run_once()
    # if report:
    #     print(report)
    
    # For production, start scheduled delivery
    engine.start()
