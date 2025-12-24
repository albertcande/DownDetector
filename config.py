"""
============================================================
DOWN DETECTOR - CONFIGURATION MODULE
============================================================

This module handles loading and validating configuration from
environment variables. All sensitive credentials are loaded
from a .env file which should NEVER be committed to version control.

Usage:
    from config import Config
    config = Config()
    print(config.email_sender)

Author: Your Name
Created: December 2024
============================================================
"""

import os
import sys
from dotenv import load_dotenv


class Config:
    """
    Configuration class that loads and validates all settings
    from environment variables.
    
    Attributes:
        email_sender (str): Gmail address for sending alerts
        email_password (str): Gmail app password
        email_receivers (list): List of recipient email addresses
        slack_webhook_url (str): Slack incoming webhook URL
        check_delay (int): Seconds between checking each site
        loop_delay (int): Seconds between monitoring cycles
    """
    
    def __init__(self):
        """
        Initialize configuration by loading environment variables.
        Validates that all required settings are present.
        """
        # Load environment variables from .env file
        # override=True ensures .env takes precedence over system env vars
        load_dotenv(override=True)
        
        # --- EMAIL CONFIGURATION ---
        self.email_sender = os.getenv("EMAIL_SENDER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        
        # Parse comma-separated email receivers into a list
        receivers_str = os.getenv("EMAIL_RECEIVERS", "")
        self.email_receivers = [
            email.strip() 
            for email in receivers_str.split(",") 
            if email.strip()
        ]
        
        # --- SLACK CONFIGURATION ---
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        
        # --- MONITORING SETTINGS ---
        # Default to 10 seconds between site checks
        self.check_delay = int(os.getenv("CHECK_DELAY_BETWEEN_SITES", "10"))
        # Default to 60 seconds between monitoring cycles
        self.loop_delay = int(os.getenv("LOOP_DELAY", "60"))
        
    def validate(self) -> bool:
        """
        Validate that all required configuration values are present.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            SystemExit: If critical configuration is missing
        """
        errors = []
        
        # Check required email configuration
        if not self.email_sender:
            errors.append("EMAIL_SENDER is not set")
        if not self.email_password:
            errors.append("EMAIL_PASSWORD is not set")
        if not self.email_receivers:
            errors.append("EMAIL_RECEIVERS is not set or empty")
            
        # Slack is optional, but warn if not configured
        if not self.slack_webhook_url:
            print("⚠️  Warning: SLACK_WEBHOOK_URL is not set. Slack alerts disabled.")
            
        # If there are errors, display them and exit
        if errors:
            print("\n❌ Configuration Error!")
            print("=" * 50)
            print("Please check your .env file and ensure all required")
            print("environment variables are set correctly.")
            print("\nMissing or invalid settings:")
            for error in errors:
                print(f"  • {error}")
            print("\nSee .env.example for the required format.")
            print("=" * 50)
            sys.exit(1)
            
        return True
    
    @property
    def slack_enabled(self) -> bool:
        """Check if Slack integration is enabled."""
        return bool(self.slack_webhook_url)
    
    def __repr__(self) -> str:
        """Return a safe string representation (no secrets)."""
        return (
            f"Config("
            f"email_sender='{self.email_sender}', "
            f"receivers={len(self.email_receivers)}, "
            f"slack_enabled={self.slack_enabled})"
        )


# --- MONITORING TARGETS ---
# Define the websites/services to monitor
# Each target has:
#   - name: Human-readable service name
#   - url: Status page URL to check
#   - mode: 'downdetector' or 'generic'
#   - good_keywords: (generic mode only) Keywords indicating operational status

TARGETS = [
    {
        "name": "Internet Archive",
        "url": "https://downdetector.com/status/internetarchive/",
        "mode": "downdetector"
    },
    {
        "name": "Roblox",
        "url": "https://downdetector.com/status/roblox/",
        "mode": "downdetector"
    },
    {
        "name": "OpenAI API",
        "url": "https://status.openai.com/",
        "mode": "generic",
        "good_keywords": ["all systems operational", "operational"]
    }
]
