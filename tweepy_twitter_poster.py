#!/usr/bin/env python3
"""
Alternative Twitter Posting Component using Tweepy for AI News Automation

This script handles posting tweets to Twitter/X using the Tweepy library,
which often provides more reliable authentication handling.
"""

import os
import json
import logging
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tweepy_twitter_poster')

class TweepyTwitterPoster:
    """Class to handle posting tweets to Twitter/X using Tweepy"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_secret: Optional[str] = None
    ):
        """
        Initialize the TweepyTwitterPoster with API credentials
        
        Args:
            api_key (str, optional): Twitter API key. If not provided, will look for TWITTER_API_KEY env variable.
            api_secret (str, optional): Twitter API secret. If not provided, will look for TWITTER_API_SECRET env variable.
            access_token (str, optional): Twitter access token. If not provided, will look for TWITTER_ACCESS_TOKEN env variable.
            access_secret (str, optional): Twitter access token secret. If not provided, will look for TWITTER_ACCESS_SECRET env variable.
        """
        # Get credentials from parameters or environment variables
        self.api_key = api_key or os.getenv('TWITTER_API_KEY')
        self.api_secret = api_secret or os.getenv('TWITTER_API_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = access_secret or os.getenv('TWITTER_ACCESS_SECRET')
        
        # Check if we have the necessary credentials
        if not (self.api_key and self.api_secret and self.access_token and self.access_secret):
            raise ValueError(
                "Twitter API credentials are required. Set environment variables or pass as parameters:\n"
                "- TWITTER_API_KEY and TWITTER_API_SECRET\n"
                "- TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_SECRET"
            )
        
        # Initialize Tweepy client
        try:
            import tweepy
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret
            )
            logger.info("Tweepy client initialized successfully")
        except ImportError:
            logger.error("Tweepy is required for this script")
            logger.error("Install it with: pip install tweepy")
            raise
    
    def post_tweet(self, text: str) -> dict:
        """
        Post a tweet to Twitter
        
        Args:
            text (str): Tweet text content (max 280 characters)
            
        Returns:
            dict: Response from Twitter API
        """
        # Validate tweet length
        if len(text) > 280:
            logger.warning(f"Tweet exceeds 280 characters ({len(text)}). Truncating...")
            text = text[:277] + "..."
        
        try:
            # Import tweepy here to catch import errors
            import tweepy
            
            # Post the tweet
            logger.info("Posting tweet to Twitter using Tweepy")
            response = self.client.create_tweet(text=text)
            
            # Convert response to dictionary for consistency with original script
            if hasattr(response, 'data'):
                result = {'data': response.data}
                logger.info(f"Tweet posted successfully. Tweet ID: {result.get('data', {}).get('id')}")
                return result
            else:
                logger.info("Tweet posted successfully")
                return {'data': {'id': 'unknown'}}
            
        except tweepy.TweepyException as e:
            logger.error(f"Tweepy error posting tweet: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error posting tweet: {str(e)}")
            raise
    
    def post_from_file(self, filename: str = "tweet_content.txt") -> dict:
        """
        Post a tweet from a file
        
        Args:
            filename (str): Path to file containing tweet text
            
        Returns:
            dict: Response from Twitter API
        """
        try:
            # Read tweet from file
            with open(filename, 'r', encoding='utf-8') as f:
                tweet_text = f.read().strip()
            
            logger.info(f"Read tweet from {filename} ({len(tweet_text)} characters)")
            
            # Post the tweet
            return self.post_tweet(tweet_text)
            
        except FileNotFoundError:
            logger.error(f"Tweet file not found: {filename}")
            raise
            
        except Exception as e:
            logger.error(f"Error posting tweet from file: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    try:
        # Try to import tweepy to check if it's installed
        try:
            import tweepy
        except ImportError:
            print("Tweepy is not installed. Installing now...")
            import subprocess
            subprocess.check_call(["pip", "install", "tweepy"])
            import tweepy
            print("Tweepy installed successfully!")
        
        # Create poster instance
        poster = TweepyTwitterPoster()
        
        # Post from file or directly
        if os.path.exists("tweet_content.txt"):
            result = poster.post_from_file()
            print(f"Tweet posted from file. Tweet ID: {result.get('data', {}).get('id')}")
        else:
            # Example direct tweet
            tweet_text = "This is a test tweet from the AI News Automation system using Tweepy. #AI #TechNews #Testing"
            result = poster.post_tweet(tweet_text)
            print(f"Test tweet posted. Tweet ID: {result.get('data', {}).get('id')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
