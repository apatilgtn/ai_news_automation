"""
Environment Variable Loader for AI News Automation

This script loads environment variables from a .env file and checks
if all required variables are set.
"""

from dotenv import load_dotenv
import os

def load_env():
    """
    Load environment variables from .env file
    
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    # Load variables from .env file
    load_dotenv()
    
    # Check if required variables are set
    required_vars = [
        'NEWSAPI_KEY',
        'ANTHROPIC_API_KEY',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_SECRET'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    return True

if __name__ == "__main__":
    if load_env():
        print("All required environment variables are set!")
    else:
        print("Please set all required environment variables in your .env file")
