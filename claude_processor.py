#!/usr/bin/env python3
"""
AI Processing Component with Anthropic's Claude for AI News Automation

This script processes news articles using Anthropic's Claude API to:
1. Select the top 3 most relevant and important tech/AI news stories
2. Format them into a concise, engaging tweet format
3. Return the formatted content ready for posting to Twitter
"""

import os
import json
import logging
import anthropic
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('claude_processor')

class ClaudeProcessor:
    """Class to handle AI processing of news articles using Anthropic's Claude"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ClaudeProcessor with API credentials
        
        Args:
            api_key (str, optional): Anthropic API key. If not provided, will look for ANTHROPIC_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass as parameter.")
        
        # Initialize the Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"  # Using the most capable model, adjust as needed
    
    def select_top_news(self, articles: List[Dict[str, Any]], count: int = 3) -> List[Dict[str, Any]]:
        """
        Use Claude to select the top most important and relevant tech/AI news stories
        
        Args:
            articles (list): List of news article dictionaries
            count (int): Number of top articles to select (default: 3)
            
        Returns:
            list: List of selected article dictionaries
        """
        if not articles:
            logger.warning("No articles provided for selection")
            return []
        
        # Prepare article data for Claude
        article_data = []
        for i, article in enumerate(articles, 1):
            article_info = {
                "id": i,
                "title": article.get("title", "No title"),
                "source": article.get("source", {}).get("name", "Unknown source"),
                "description": article.get("description", "No description"),
                "url": article.get("url", ""),
                "publishedAt": article.get("publishedAt", "")
            }
            article_data.append(article_info)
        
        # Create the prompt for Claude
        prompt = self._create_selection_prompt(article_data, count)
        
        try:
            # Call Claude API
            logger.info(f"Asking Claude to select top {count} articles from {len(articles)} total articles")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.2,  # Low temperature for more deterministic responses
                system="You are an expert tech and AI news curator with deep knowledge of the field. Your task is to select the most important and relevant tech/AI news stories.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the selected article IDs from Claude's response
            selected_ids = self._parse_selected_article_ids(response.content[0].text, count)
            
            # Map IDs back to original articles
            selected_articles = []
            for article_id in selected_ids:
                if 1 <= article_id <= len(articles):
                    selected_articles.append(articles[article_id - 1])
                else:
                    logger.warning(f"Invalid article ID {article_id} returned by Claude")
            
            logger.info(f"Claude selected {len(selected_articles)} articles")
            return selected_articles
            
        except Exception as e:
            logger.error(f"Error calling Claude API for article selection: {str(e)}")
            # Fallback: return the first 'count' articles if Claude fails
            logger.info(f"Falling back to selecting first {count} articles")
            return articles[:count]
    
    def format_tweet(self, articles: List[Dict[str, Any]]) -> str:
        """
        Use Claude to format selected articles into a tweet
        
        Args:
            articles (list): List of selected article dictionaries
            
        Returns:
            str: Formatted tweet text
        """
        if not articles:
            logger.warning("No articles provided for tweet formatting")
            return "No tech/AI news to share today. Stay tuned for updates tomorrow! #AI #TechNews"
        
        # Prepare article data for Claude
        article_data = []
        for i, article in enumerate(articles, 1):
            article_info = {
                "id": i,
                "title": article.get("title", "No title"),
                "source": article.get("source", {}).get("name", "Unknown source"),
                "description": article.get("description", "No description"),
                "url": article.get("url", ""),
                "publishedAt": article.get("publishedAt", "")
            }
            article_data.append(article_info)
        
        # Create the prompt for Claude
        prompt = self._create_tweet_prompt(article_data)
        
        try:
            # Call Claude API
            logger.info(f"Asking Claude to format {len(articles)} articles into a tweet")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,  # Higher temperature for more creative responses
                system="You are an expert at creating engaging, informative tweets about tech and AI news. Your tweets are concise, accurate, and drive engagement.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the tweet text from Claude's response
            tweet_text = self._parse_tweet_text(response.content[0].text)
            
            logger.info(f"Claude generated tweet text ({len(tweet_text)} characters)")
            return tweet_text
            
        except Exception as e:
            logger.error(f"Error calling Claude API for tweet formatting: {str(e)}")
            # Fallback: create a simple tweet if Claude fails
            return self._create_fallback_tweet(articles)
    
    def _create_selection_prompt(self, article_data: List[Dict[str, Any]], count: int) -> str:
        """Create a prompt for Claude to select the top articles"""
        articles_text = "\n\n".join([
            f"Article {article['id']}:\n"
            f"Title: {article['title']}\n"
            f"Source: {article['source']}\n"
            f"Published: {article['publishedAt']}\n"
            f"Description: {article['description']}\n"
            f"URL: {article['url']}"
            for article in article_data
        ])
        
        prompt = f"""I have a list of {len(article_data)} tech and AI news articles. Please select the {count} most important and relevant articles based on:

1. Significance to the tech/AI industry
2. Novelty and innovation factor
3. Potential impact on the field
4. Credibility of the source
5. Recency and timeliness

Here are the articles:

{articles_text}

Please respond with ONLY the article IDs of your top {count} selections in this exact format:
SELECTED_ARTICLES: [id1, id2, id3]

For example:
SELECTED_ARTICLES: [4, 12, 7]"""
        
        return prompt
    
    def _parse_selected_article_ids(self, response_text: str, expected_count: int) -> List[int]:
        """Parse Claude's response to extract the selected article IDs"""
        try:
            # Look for the SELECTED_ARTICLES pattern
            if "SELECTED_ARTICLES:" in response_text:
                # Extract the part after SELECTED_ARTICLES:
                selection_part = response_text.split("SELECTED_ARTICLES:")[1].strip()
                # Extract the list part
                list_part = selection_part.split("]")[0] + "]"
                # Convert to Python list
                selected_ids = json.loads(list_part.replace("[", "[").replace("]", "]"))
                return selected_ids
            
            # Fallback: try to find numbers in the response
            import re
            numbers = re.findall(r'\d+', response_text)
            selected_ids = [int(num) for num in numbers[:expected_count]]
            return selected_ids
            
        except Exception as e:
            logger.error(f"Error parsing selected article IDs: {str(e)}")
            # Return sequential IDs as fallback
            return list(range(1, expected_count + 1))
    
    def _create_tweet_prompt(self, article_data: List[Dict[str, Any]]) -> str:
        """Create a prompt for Claude to format articles into a tweet"""
        articles_text = "\n\n".join([
            f"Article {article['id']}:\n"
            f"Title: {article['title']}\n"
            f"Source: {article['source']}\n"
            f"URL: {article['url']}\n"
            f"Description: {article['description']}"
            for article in article_data
        ])
        
        prompt = f"""I have selected {len(article_data)} important tech/AI news articles. Please create an engaging tweet that:

1. Briefly mentions all {len(article_data)} stories
2. Includes the URLs for each article
3. Uses appropriate hashtags (#AI, #TechNews, etc.)
4. Stays within Twitter's 280 character limit
5. Is engaging and informative

Here are the articles:

{articles_text}

Please respond with ONLY the tweet text in this exact format:
TWEET_TEXT: [Your formatted tweet here]"""
        
        return prompt
    
    def _parse_tweet_text(self, response_text: str) -> str:
        """Parse Claude's response to extract the tweet text"""
        try:
            # Look for the TWEET_TEXT pattern
            if "TWEET_TEXT:" in response_text:
                # Extract the part after TWEET_TEXT:
                tweet_part = response_text.split("TWEET_TEXT:")[1].strip()
                # If there are any other markers after the tweet, remove them
                if "\n\n" in tweet_part:
                    tweet_part = tweet_part.split("\n\n")[0]
                return tweet_part
            
            # If no marker found, return the whole response (limited to 280 chars)
            return response_text[:280]
            
        except Exception as e:
            logger.error(f"Error parsing tweet text: {str(e)}")
            return "Error generating tweet. Please check the news sources directly."
    
    def _create_fallback_tweet(self, articles: List[Dict[str, Any]]) -> str:
        """Create a simple tweet as fallback if Claude API fails"""
        tweet_parts = ["Today's top tech/AI news:"]
        
        for i, article in enumerate(articles[:3], 1):
            title = article.get("title", "Interesting tech news")
            url = article.get("url", "")
            # Truncate title if needed
            if len(title) > 70:
                title = title[:67] + "..."
            tweet_parts.append(f"{i}. {title} {url}")
        
        tweet_parts.append("#AI #TechNews #Innovation")
        
        # Join and ensure within character limit
        tweet = "\n\n".join(tweet_parts)
        if len(tweet) > 280:
            # Simplify if too long
            simple_tweet = "Today's top tech/AI news:\n\n"
            for i, article in enumerate(articles[:3], 1):
                url = article.get("url", "")
                simple_tweet += f"{i}. {url}\n"
            simple_tweet += "#AI #TechNews"
            return simple_tweet[:280]
        
        return tweet

    def process_news(self, input_file: str = "latest_ai_news.json", output_file: str = "tweet_content.txt") -> str:
        """
        Complete process: load articles, select top news, format tweet, and save
        
        Args:
            input_file (str): Path to JSON file with news articles
            output_file (str): Path to save the formatted tweet
            
        Returns:
            str: Formatted tweet text
        """
        try:
            # Load articles from file
            with open(input_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            logger.info(f"Loaded {len(articles)} articles from {input_file}")
            
            # Select top articles
            selected_articles = self.select_top_news(articles)
            
            # Format tweet
            tweet_text = self.format_tweet(selected_articles)
            
            # Save tweet to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(tweet_text)
            
            logger.info(f"Saved tweet to {output_file}")
            
            return tweet_text
            
        except Exception as e:
            logger.error(f"Error in process_news: {str(e)}")
            return ""


# Example usage
if __name__ == "__main__":
    try:
        # Create processor instance
        processor = ClaudeProcessor()
        
        # Process news and generate tweet
        tweet = processor.process_news()
        
        # Print the generated tweet
        print("\nGenerated Tweet:")
        print("-" * 40)
        print(tweet)
        print("-" * 40)
        print(f"Character count: {len(tweet)}/280")
        
    except Exception as e:
        print(f"Error: {str(e)}")
