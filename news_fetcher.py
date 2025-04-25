#!/usr/bin/env python3
"""
News Fetcher Component for AI News Automation

This script fetches the latest tech and AI news articles using the NewsAPI.
It handles authentication, request formatting, error handling, and filtering
to ensure relevant content is retrieved.
"""

import os
import requests
import json
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('news_fetcher')

class NewsFetcher:
    """Class to handle fetching news from NewsAPI"""
    
    def __init__(self, api_key=None):
        """
        Initialize the NewsFetcher with API credentials
        
        Args:
            api_key (str, optional): NewsAPI key. If not provided, will look for NEWSAPI_KEY env variable.
        """
        self.api_key = api_key or os.getenv('NEWSAPI_KEY')
        if not self.api_key:
            raise ValueError("NewsAPI key is required. Set NEWSAPI_KEY environment variable or pass as parameter.")
        
        self.base_url = "https://newsapi.org/v2"
        self.headers = {
            "X-Api-Key": self.api_key,
            "User-Agent": "AINewsAutomation/1.0"
        }
    
    def fetch_tech_ai_news(self, days=1, max_articles=20):
        """
        Fetch recent tech and AI news articles
        
        Args:
            days (int): How many days back to search for news
            max_articles (int): Maximum number of articles to retrieve
            
        Returns:
            list: List of news article dictionaries
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for API
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        # Define search queries for tech and AI news
        queries = [
            "artificial intelligence",
            "machine learning",
            "AI technology",
            "neural networks",
            "deep learning",
            "large language models",
            "generative AI",
            "ChatGPT OR GPT-4",
            "Claude AI OR Anthropic",
            "OpenAI",
            "Microsoft AI OR Microsoft Copilot",
            "Kubernetes AI",
            "DevOps AI"
        ]
        
        all_articles = []
        
        # Make requests for each query
        for query in queries:
            try:
                logger.info(f"Fetching news for query: {query}")
                
                # Construct the API endpoint for everything search
                endpoint = f"{self.base_url}/everything"
                
                # Set up parameters
                params = {
                    "q": query,
                    "from": from_date,
                    "to": to_date,
                    "language": "en",
                    "sortBy": "relevancy",
                    "pageSize": max_articles // len(queries) + 5  # Request a few extra per query
                }
                
                # Make the request
                response = requests.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()  # Raise exception for HTTP errors
                
                # Parse the response
                data = response.json()
                
                if data.get("status") == "ok":
                    # Add articles to our collection
                    articles = data.get("articles", [])
                    logger.info(f"Retrieved {len(articles)} articles for query: {query}")
                    all_articles.extend(articles)
                else:
                    logger.error(f"API returned error: {data.get('message', 'Unknown error')}")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
            except json.JSONDecodeError:
                logger.error("Failed to parse API response")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
        
        # Remove duplicates (based on URL)
        unique_articles = self._remove_duplicates(all_articles)
        
        # Filter for relevance and limit to max_articles
        filtered_articles = self._filter_relevant_articles(unique_articles)
        limited_articles = filtered_articles[:max_articles]
        
        logger.info(f"Final article count after filtering: {len(limited_articles)}")
        return limited_articles
    
    def _remove_duplicates(self, articles):
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
    
    def _filter_relevant_articles(self, articles):
        """
        Filter articles for relevance to tech and AI
        
        This is a simple keyword-based filter. In a production system,
        you might want to use more sophisticated NLP techniques.
        """
        relevant_keywords = [
            "chatgpt", "gpt-4", "gpt-5", "claude", "anthropic", 
    "openai", "microsoft ai", "copilot", "kubernetes", 
    "devops", "llm", "large language model"
        ]
        
        filtered_articles = []
        
        for article in articles:
            title = article.get("title", "").lower()
            description = article.get("description", "").lower()
            content = article.get("content", "").lower()
            
            # Check if any relevant keywords are in the title, description, or content
            is_relevant = any(
                keyword in title or keyword in description or keyword in content
                for keyword in relevant_keywords
            )
            
            if is_relevant:
                filtered_articles.append(article)
        
        return filtered_articles
    
    def save_articles_to_file(self, articles, filename="latest_ai_news.json"):
        """
        Save fetched articles to a JSON file
        
        Args:
            articles (list): List of article dictionaries
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(articles)} articles to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save articles: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    try:
        # Create fetcher instance
        fetcher = NewsFetcher()
        
        # Fetch news
        articles = fetcher.fetch_tech_ai_news(days=1, max_articles=20)
        
        # Save to file
        fetcher.save_articles_to_file(articles)
        
        # Print summary
        print(f"Retrieved {len(articles)} tech/AI news articles")
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article.get('title')}")
            print(f"   Source: {article.get('source', {}).get('name')}")
            print(f"   Published: {article.get('publishedAt')}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

