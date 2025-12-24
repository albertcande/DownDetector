"""
============================================================
DOWN DETECTOR - MULTI-SERVICE MONITORING SYSTEM
============================================================

A Python-based monitoring tool that tracks the status of multiple
web services and sends real-time alerts via Email and Slack when
outages or status changes are detected.

Features:
    - Monitor multiple downdetector.com and generic status pages
    - Bypass Cloudflare protection using undetected-chromedriver
    - Send alerts via Email (Gmail SMTP) and Slack webhooks
    - Configurable monitoring intervals
    - Secure credential management via environment variables

Author: Your Name
Created: December 2024
License: MIT
============================================================
"""

import time
import smtplib
import random
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from email.mime.text import MIMEText

# Import configuration from local config module
from config import Config, TARGETS


# ============================================================
# NOTIFICATION SERVICES
# ============================================================

def send_slack_alert(config: Config, site_name: str, status: str, url: str) -> None:
    """
    Send a formatted alert message to Slack via webhook.
    
    This function posts a message to a Slack channel using an
    incoming webhook URL. The message includes the service name,
    current status, and a link to the status page.
    
    Args:
        config: Configuration object containing Slack settings
        site_name: Human-readable name of the monitored service
        status: Current status string (e.g., "OPERATIONAL", "OUTAGE DETECTED")
        url: URL of the status page for reference
        
    Returns:
        None
        
    Note:
        If Slack is not configured (no webhook URL), this function
        returns immediately without sending any notification.
    """
    # Skip if Slack is not configured
    if not config.slack_enabled:
        return

    # Build the Slack message payload using Block Kit formatting
    # See: https://api.slack.com/messaging/composing/layouts
    payload = {
        "text": f"🚨 *Monitor Alert: {site_name}*\n*Status:* {status}\n<{url}|View Status Page>"
    }

    try:
        # Send HTTP POST request to Slack webhook
        response = requests.post(
            config.slack_webhook_url, 
            json=payload,
            timeout=10  # 10 second timeout to prevent hanging
        )
        
        if response.status_code == 200:
            print("   >> Slack alert sent!")
        else:
            print(f"   !! Slack Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        print("   !! Slack Error: Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"   !! Slack Failed: {e}")


def send_email_alert(
    config: Config, 
    site_name: str, 
    status: str, 
    url: str, 
    extra_info: str = ""
) -> None:
    """
    Send an email alert to all configured recipients via Gmail SMTP.
    
    This function composes and sends an email notification containing
    details about a service status change. Uses Gmail's SMTP server
    with SSL encryption on port 465.
    
    Args:
        config: Configuration object containing email settings
        site_name: Human-readable name of the monitored service
        status: Current status string (e.g., "OPERATIONAL", "OUTAGE DETECTED")
        url: URL of the status page for reference
        extra_info: Optional additional details to include in the email body
        
    Returns:
        None
        
    Prerequisites:
        - Gmail account with "Less secure apps" or App Password enabled
        - Valid EMAIL_SENDER and EMAIL_PASSWORD in environment variables
        
    Note:
        For Gmail, you need to generate an App Password:
        https://myaccount.google.com/apppasswords
    """
    # Compose email subject and body
    subject = f"ALERT: {site_name} is {status}"
    body = (
        f"Monitor Alert!\n\n"
        f"Site: {site_name}\n"
        f"New Status: {status}\n"
        f"Link: {url}\n\n"
        f"{extra_info}"
    )

    # Create MIME message object
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config.email_sender
    # Join recipient list into comma-separated string for email header
    msg['To'] = ", ".join(config.email_receivers)

    try:
        # Connect to Gmail SMTP server using SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            # Authenticate with Gmail
            server.login(config.email_sender, config.email_password)
            # Send email to all recipients
            server.send_message(msg)
            
        print(f"   >> Email sent to {len(config.email_receivers)} recipients.")
        
    except smtplib.SMTPAuthenticationError:
        print("   !! Email Failed: Authentication error. Check your credentials.")
    except smtplib.SMTPException as e:
        print(f"   !! Email Failed: SMTP error - {e}")
    except Exception as e:
        print(f"   !! Email Failed: {e}")


# ============================================================
# STATUS CHECKING FUNCTIONS
# ============================================================

def check_downdetector(page_source: str) -> str:
    """
    Parse a DownDetector.com page to determine service status.
    
    DownDetector aggregates user reports to detect outages. This function
    analyzes the page content for specific indicator phrases that reveal
    the current status.
    
    Args:
        page_source: Lowercase HTML source of the DownDetector page
        
    Returns:
        str: One of the following status strings:
            - "OPERATIONAL" - No problems detected
            - "POSSIBLE ISSUES" - Minor or unconfirmed issues
            - "OUTAGE DETECTED" - Confirmed outage based on user reports
            - "SUSPICIOUS / UNKNOWN" - Unable to determine status
            
    Note:
        The page_source should be converted to lowercase before passing
        to this function for case-insensitive matching.
    """
    # Check for indicators in order of severity (most benign first)
    if "indicate no current problems" in page_source:
        return "OPERATIONAL"
    elif "possible problems" in page_source:
        return "POSSIBLE ISSUES"
    elif "indicate problems" in page_source:
        return "OUTAGE DETECTED"
    else:
        # Unable to parse the page - might be blocked or page changed
        return "SUSPICIOUS / UNKNOWN"


def check_generic(page_source: str, good_keywords: list) -> str:
    """
    Check a generic status page for operational keywords.
    
    This function is used for official status pages (like status.openai.com)
    that don't follow the DownDetector format. It searches for positive
    keywords that indicate the service is operational.
    
    Args:
        page_source: Lowercase HTML source of the status page
        good_keywords: List of lowercase strings that indicate operational status
                      (e.g., ["operational", "all systems operational"])
                      
    Returns:
        str: Either "OPERATIONAL" or "POTENTIAL OUTAGE"
        
    Example:
        >>> check_generic("all systems operational today", ["operational"])
        "OPERATIONAL"
    """
    # Search for any of the positive keywords in the page
    for keyword in good_keywords:
        if keyword.lower() in page_source:
            return "OPERATIONAL"
            
    # No positive keywords found - assume potential issues
    return "POTENTIAL OUTAGE"


# ============================================================
# BROWSER SETUP
# ============================================================

def create_browser() -> uc.Chrome:
    """
    Create and configure an undetected Chrome browser instance.
    
    Uses undetected-chromedriver to bypass anti-bot protections like
    Cloudflare. The browser runs in headless mode for server deployment.
    
    Returns:
        uc.Chrome: Configured Chrome WebDriver instance
        
    Configuration:
        - Headless mode (no visible browser window)
        - Standard desktop viewport (1920x1080)
        - Generic user agent to appear as normal browser
        - Disabled sandbox for container compatibility
    """
    options = uc.ChromeOptions()
    
    # Run without visible browser window
    options.add_argument('--headless')
    
    # Required for running in containers and some Linux environments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Set standard desktop viewport size
    options.add_argument('--window-size=1920,1080')
    
    # Use a common user agent to appear as a normal browser
    # This helps avoid detection by anti-bot systems
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/119.0.0.0 Safari/537.36'
    )

    return uc.Chrome(options=options)


# ============================================================
# MAIN MONITORING LOOP
# ============================================================

def start_monitoring() -> None:
    """
    Start the main monitoring loop.
    
    This function initializes the configuration, validates settings,
    creates a browser instance, and continuously monitors all configured
    targets. When a status change is detected, it sends notifications
    via both Email and Slack.
    
    The monitoring loop:
        1. Iterates through all configured TARGETS
        2. Loads each status page using the browser
        3. Parses the status based on the target's mode
        4. Compares with previous status to detect changes
        5. Sends alerts if status has changed
        6. Waits for the configured delay before next cycle
        
    Returns:
        None (runs indefinitely until interrupted)
        
    Keyboard Interrupt:
        Press Ctrl+C to gracefully stop monitoring and close the browser.
    """
    # Load and validate configuration
    config = Config()
    config.validate()
    
    # Initialize state tracking for each monitored URL
    # "initial" means we haven't checked this URL yet
    site_states = {target['url']: "initial" for target in TARGETS}
    
    # Display startup information
    print("=" * 60)
    print("🔍 DOWN DETECTOR - Multi-Service Monitoring System")
    print("=" * 60)
    print(f"📊 Monitoring {len(TARGETS)} targets")
    print(f"📧 Email recipients: {len(config.email_receivers)}")
    print(f"💬 Slack: {'Enabled ✓' if config.slack_enabled else 'Disabled ✗'}")
    print(f"⏱️  Check delay: {config.check_delay}s | Loop delay: {config.loop_delay}s")
    print("=" * 60)
    print("\nPress Ctrl+C to stop monitoring.\n")

    # Create browser instance
    driver = create_browser()

    try:
        # Main monitoring loop - runs indefinitely
        while True:
            # Print cycle header with timestamp
            print(f"\n--- Check Cycle: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")

            # Iterate through each monitoring target
            for target in TARGETS:
                url = target['url']
                name = target['name']
                mode = target['mode']

                # Print progress indicator
                print(f"Checking: {name}...", end=" ", flush=True)

                try:
                    # Navigate to the target URL
                    driver.get(url)
                    
                    # Random delay to appear more human-like
                    # Also allows JavaScript to fully render
                    time.sleep(random.uniform(5, 8))

                    # Get page source in lowercase for case-insensitive matching
                    page_source = driver.page_source.lower()

                    # Check if we're blocked by Cloudflare challenge page
                    if "just a moment" in driver.title.lower():
                        print("⚠️  BLOCKED (Cloudflare). Skipping.")
                        continue

                    # Determine current status based on monitoring mode
                    if mode == "downdetector":
                        # Use DownDetector-specific parsing
                        current_status = check_downdetector(page_source)
                        
                    elif mode == "generic":
                        # Use keyword-based parsing for generic status pages
                        keywords = target.get('good_keywords', ['operational'])
                        current_status = check_generic(page_source, keywords)
                    else:
                        print(f"⚠️  Unknown mode: {mode}")
                        continue

                    # Display current status
                    print(f"[{current_status}]")

                    # Get the previous status for comparison
                    last_status = site_states[url]

                    # Check if status has changed
                    if current_status != last_status:
                        # Only send alerts after initial check
                        # (avoid alerting on first run)
                        if last_status != "initial":
                            print(f"   >>> STATUS CHANGE: {last_status} -> {current_status}")

                            # Send Email notification
                            send_email_alert(config, name, current_status, url)

                            # Send Slack notification
                            send_slack_alert(config, name, current_status, url)

                        # Update stored state
                        site_states[url] = current_status

                except Exception as e:
                    # Log any errors but continue monitoring other targets
                    print(f"❌ Error: {e}")

                # Wait between checking each site to avoid rate limiting
                time.sleep(config.check_delay)

            # Wait before starting next monitoring cycle
            print(f"\n⏳ Waiting {config.loop_delay}s until next cycle...")
            time.sleep(config.loop_delay)

    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        print("\n\n🛑 Monitoring stopped by user.")
        
    finally:
        # Always close the browser, even on error
        print("🧹 Closing browser...")
        driver.quit()
        print("👋 Goodbye!")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    """
    Entry point for the Down Detector monitoring script.
    
    Usage:
        python monitor.py
        
    Prerequisites:
        1. Create a .env file based on .env.example
        2. Fill in your email and Slack credentials
        3. Install dependencies: pip install -r requirements.txt
        4. Ensure Chrome browser is installed
    """
    start_monitoring()
