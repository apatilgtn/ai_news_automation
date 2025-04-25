#!/usr/bin/env python3
"""
Tweet Formatter and Link Validator for AI News Automation

This script improves tweet formatting and validates links before posting.
"""

import re
import json
import logging
import requests
from urllib.parse import urlparse
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tweet_formatter')

class TweetFormatter:
    """Class to format tweets and validate links"""
    
    def __init__(self, max_length=280):
        """Initialize the formatter with Twitter's character limit"""
        self.max_length = max_length
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def format_tweet(self, tweet_text):
        """
        Format a tweet to ensure proper spacing, punctuation, and valid links
        
        Args:
            tweet_text (str): Original tweet text
            
        Returns:
            str: Formatted tweet text
        """
        logger.info(f"Formatting tweet ({len(tweet_text)} characters)")
        
        # Extract links for validation
        links = self._extract_links(tweet_text)
        valid_links = self._validate_links(links)
        
        # Replace invalid links with valid ones
        for i, link in enumerate(links):
            if link in valid_links:
                continue
            if i < len(valid_links):
                tweet_text = tweet_text.replace(link, valid_links[i])
            else:
                # If we don't have a valid replacement, remove the link
                tweet_text = tweet_text.replace(link, "")
        
        # Clean up spacing and formatting
        tweet_text = self._clean_formatting(tweet_text)
        
        # Ensure proper hashtag formatting
        tweet_text = self._format_hashtags(tweet_text)
        
        # Truncate if necessary
        if len(tweet_text) > self.max_length:
            tweet_text = self._smart_truncate(tweet_text)
        
        logger.info(f"Formatted tweet ({len(tweet_text)} characters)")
        return tweet_text
    
    def _extract_links(self, text):
        """Extract all URLs from text"""
        # URL regex pattern
        url_pattern = r'https?://[^\s]+'
        return re.findall(url_pattern, text)
    
    def _validate_links(self, links):
        """
        Validate links and return only working ones
        
        Args:
            links (list): List of URLs to validate
            
        Returns:
            list: List of valid URLs
        """
        valid_links = []
        
        for link in links:
            try:
                # Parse the URL to check if it's well-formed
                parsed_url = urlparse(link)
                if not parsed_url.netloc:
                    logger.warning(f"Invalid URL format: {link}")
                    continue
                
                # Check if the URL is accessible
                response = requests.head(link, headers=self.headers, timeout=5, allow_redirects=True)
                
                # Consider 2xx status codes as valid
                if 200 <= response.status_code < 300:
                    valid_links.append(link)
                    logger.info(f"Valid link: {link}")
                else:
                    logger.warning(f"Invalid link (status {response.status_code}): {link}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error validating link {link}: {str(e)}")
            except Exception as e:
                logger.warning(f"Unexpected error validating link {link}: {str(e)}")
        
        return valid_links
    
    def _clean_formatting(self, text):
        """Clean up spacing and formatting issues"""
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        
        # Remove extra newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Ensure consistent newline format
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _format_hashtags(self, text):
        """Ensure proper hashtag formatting"""
        # Find hashtags that might be improperly formatted
        hashtag_pattern = r'(?<!\S)#([a-zA-Z0-9_]+)'
        hashtags = re.findall(hashtag_pattern, text)
        
        # Ensure hashtags use CamelCase for multi-word tags
        for tag in hashtags:
            if '_' in tag:
                words = tag.split('_')
                camel_case = ''.join(word.capitalize() for word in words)
                text = text.replace(f"#{tag}", f"#{camel_case}")
        
        # Add common AI hashtags if not present
        common_hashtags = ["#AI", "#TechNews", "#ArtificialIntelligence"]
        
        # Check if we have space for more hashtags
        remaining_space = self.max_length - len(text)
        
        if remaining_space > 30:  # Only add if we have enough space
            # Extract existing hashtags
            existing_hashtags = [f"#{tag}" for tag in hashtags]
            
            # Add missing common hashtags
            hashtag_text = ""
            for hashtag in common_hashtags:
                if hashtag not in existing_hashtags and len(hashtag_text) + len(hashtag) + 1 <= remaining_space:
                    hashtag_text += f" {hashtag}"
            
            if hashtag_text:
                text += hashtag_text
        
        return text
    
    def _smart_truncate(self, text):
        """
        Intelligently truncate text to fit within character limit
        
        This preserves important information like links and hashtags
        """
        if len(text) <= self.max_length:
            return text
        
        # Extract links and hashtags
        links = self._extract_links(text)
        hashtag_pattern = r'(?<!\S)#([a-zA-Z0-9_]+)'
        hashtags = re.findall(hashtag_pattern, text)
        
        # Calculate space needed for important elements
        important_elements = links + [f"#{tag}" for tag in hashtags]
        important_text = " ".join(important_elements)
        
        # If just the important elements are too long, prioritize
        if len(important_text) > self.max_length - 20:
            # Prioritize the first link and a few hashtags
            prioritized = []
            remaining_space = self.max_length - 20  # Leave space for some context
            
            # Add first link if possible
            if links and len(links[0]) < remaining_space:
                prioritized.append(links[0])
                remaining_space -= len(links[0]) + 1
            
            # Add hashtags until we run out of space
            for tag in [f"#{t}" for t in hashtags]:
                if len(tag) + 1 <= remaining_space:
                    prioritized.append(tag)
                    remaining_space -= len(tag) + 1
            
            important_text = " ".join(prioritized)
        
        # Get the main content without links and hashtags
        main_content = text
        for item in links + [f"#{tag}" for tag in hashtags]:
            main_content = main_content.replace(item, "")
        
        main_content = self._clean_formatting(main_content)
        
        # Calculate how much of the main content we can keep
        available_space = self.max_length - len(important_text) - 5  # 5 chars for ellipsis and spacing
        
        if available_space > 20:  # Only include main content if we have reasonable space
            truncated_content = main_content[:available_space].strip() + "..."
            return f"{truncated_content} {important_text}"
        else:
            # If we can't fit much content, just use the important elements
            return important_text[:self.max_length]

    def format_tweet_from_file(self, input_file="tweet_content.txt", output_file=None):
        """
        Read tweet from file, format it, and optionally save back to file
        
        Args:
            input_file (str): Path to input file containing tweet text
            output_file (str, optional): Path to save formatted tweet
            
        Returns:
            str: Formatted tweet text
        """
        try:
            # Read tweet from file
            with open(input_file, 'r', encoding='utf-8') as f:
                tweet_text = f.read().strip()
            
            logger.info(f"Read tweet from {input_file} ({len(tweet_text)} characters)")
            
            # Format the tweet
            formatted_tweet = self.format_tweet(tweet_text)
            
            # Save formatted tweet if output file is specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_tweet)
                logger.info(f"Saved formatted tweet to {output_file}")
            else:
                # Otherwise, overwrite the input file
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_tweet)
                logger.info(f"Updated {input_file} with formatted tweet")
            
            return formatted_tweet
            
        except FileNotFoundError:
            logger.error(f"Tweet file not found: {input_file}")
            raise
            
        except Exception as e:
            logger.error(f"Error formatting tweet from file: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    try:
        formatter = TweetFormatter()
        
        # Format tweet from file
        if os.path.exists("tweet_content.txt"):
            formatted_tweet = formatter.format_tweet_from_file()
            print(f"Formatted tweet ({len(formatted_tweet)} characters):")
            print(formatted_tweet)
        else:
            print("tweet_content.txt not found. Creating example tweet...")
            
            # Example tweet with formatting issues
            example_tweet = """Today's AI News:
            1. OpenAI releases new model https://example.com/broken-link
            2. Google    announces AI improvements
            3. Microsoft partners with   AI startups
            
            #AI #machine_learning #tech"""
            
            # Format the example
            formatted = formatter.format_tweet(example_tweet)
            
            # Save to file
            with open("tweet_content.txt", 'w', encoding='utf-8') as f:
                f.write(formatted)
            
            print(f"Created and formatted example tweet ({len(formatted)} characters):")
            print(formatted)
        
    except Exception as e:
        print(f"Error: {str(e)}")
