#!/usr/bin/env python3
"""
Twitter Posting Component for AI News Automation

This script handles posting tweets to Twitter/X using the Twitter API v2.
It manages authentication, tweet creation, and error handling.
"""

import os
import json
import logging
import requests
import time
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('twitter_poster')

class TwitterPoster:
    """Class to handle posting tweets to Twitter/X"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_secret: Optional[str] = None,
        bearer_token: Optional[str] = None
    ):
        """
        Initialize the TwitterPoster with API credentials
        
        Args:
            api_key (str, optional): Twitter API key. If not provided, will look for TWITTER_API_KEY env variable.
            api_secret (str, optional): Twitter API secret. If not provided, will look for TWITTER_API_SECRET env variable.
            access_token (str, optional): Twitter access token. If not provided, will look for TWITTER_ACCESS_TOKEN env variable.
            access_secret (str, optional): Twitter access token secret. If not provided, will look for TWITTER_ACCESS_SECRET env variable.
            bearer_token (str, optional): Twitter bearer token. If not provided, will look for TWITTER_BEARER_TOKEN env variable.
        """
        # Get credentials from parameters or environment variables
        self.api_key = api_key or os.getenv('TWITTER_API_KEY')
        self.api_secret = api_secret or os.getenv('TWITTER_API_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = access_secret or os.getenv('TWITTER_ACCESS_SECRET')
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        
        # Check if we have the necessary credentials
        if not (self.bearer_token or (self.api_key and self.api_secret and self.access_token and self.access_secret)):
            raise ValueError(
                "Twitter API credentials are required. Set environment variables or pass as parameters:\n"
                "- TWITTER_API_KEY and TWITTER_API_SECRET\n"
                "- TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_SECRET\n"
                "- Or TWITTER_BEARER_TOKEN for app-only authentication"
            )
        
        # API endpoints
        self.base_url = "https://api.twitter.com/2"
        self.tweet_endpoint = f"{self.base_url}/tweets"
    
    def post_tweet(self, text: str) -> Dict[str, Any]:
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
        
        # Prepare the request payload
        payload = {"text": text}
        
        # Set up headers with OAuth 1.0a
        headers = self._get_auth_headers()
        
        try:
            # Make the API request
            logger.info("Posting tweet to Twitter")
            response = requests.post(
                self.tweet_endpoint,
                headers=headers,
                json=payload
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            logger.info(f"Tweet posted successfully. Tweet ID: {result.get('data', {}).get('id')}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error posting tweet: {e}")
            if response.status_code == 429:
                logger.error("Rate limit exceeded. Consider implementing retry logic with exponential backoff.")
            try:
                error_data = response.json()
                logger.error(f"Twitter API error: {json.dumps(error_data, indent=2)}")
            except:
                logger.error(f"Response content: {response.text}")
            raise
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error posting tweet: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error posting tweet: {e}")
            raise
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for Twitter API
        
        Returns:
            dict: Headers with authentication
        """
        # If we have a bearer token, use it (app-only auth)
        if self.bearer_token:
            return {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
        
        # Otherwise, use OAuth 1.0a
        try:
            # Import OAuth1 from requests_oauthlib
            from requests_oauthlib import OAuth1
            
            # Create OAuth1 session
            auth = OAuth1(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_secret
            )
            
            # Get the headers from the auth object
            # This is a bit of a hack, but it works
            req = requests.Request('POST', self.tweet_endpoint)
            prepped = req.prepare()
            auth(prepped)
            
            # Extract and return the headers
            headers = dict(prepped.headers)
            headers["Content-Type"] = "application/json"
            return headers
            
        except ImportError:
            logger.error("requests_oauthlib is required for OAuth1 authentication")
            logger.error("Install it with: pip install requests_oauthlib")
            raise
    
    def post_from_file(self, filename: str = "tweet_content.txt") -> Dict[str, Any]:
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
            logger.error(f"Error posting tweet from file: {e}")
            raise


# Example usage
if __name__ == "__main__":
    try:
        # Create poster instance
        poster = TwitterPoster()
        
        # Post from file or directly
        if os.path.exists("tweet_content.txt"):
            result = poster.post_from_file()
            print(f"Tweet posted from file. Tweet ID: {result.get('data', {}).get('id')}")
        else:
            # Example direct tweet
            tweet_text = "This is a test tweet from the AI News Automation system. #AI #TechNews #Testing"
            result = poster.post_tweet(tweet_text)
            print(f"Test tweet posted. Tweet ID: {result.get('data', {}).get('id')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
