#!/usr/bin/env python3
"""
Final Enhanced AI News Automation Script

This script combines all components including:
- News fetching from NewsAPI
- Blog scraping from AI company websites
- Claude processing for content generation
- Tweet formatting and link validation
- Twitter posting with proper error handling
"""

import os
import sys
import logging
import json
import time
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_news_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('final_ai_news_automation')

def run_final_automation():
    """Run the complete AI news automation process with all enhancements"""
    start_time = time.time()
    logger.info("Starting Final Enhanced AI News Automation process")
    
    try:
        # Step 1a: Fetch news from NewsAPI
        logger.info("Step 1a: Fetching news articles from NewsAPI")
        from news_fetcher import NewsFetcher
        fetcher = NewsFetcher()
        articles = fetcher.fetch_tech_ai_news(days=1, max_articles=10)
        fetcher.save_articles_to_file(articles, "newsapi_articles.json")
        logger.info(f"Fetched {len(articles)} articles from NewsAPI")
        
        # Step 1b: Scrape news from AI company blogs with improved scraper
        logger.info("Step 1b: Scraping news from AI company blogs with improved scraper")
        try:
            # Try to import the improved scraper first
            from ai_blog_scraper_improved import AIBlogScraperImproved
            scraper = AIBlogScraperImproved()
            logger.info("Using improved blog scraper with RSS support")
        except ImportError:
            # Fall back to original scraper if improved version not available
            from ai_blog_scraper import AIBlogScraper
            scraper = AIBlogScraper()
            logger.info("Using original blog scraper")
        
        scraped_articles = scraper.scrape_all_blogs(days_back=3, max_articles_per_blog=2)
        logger.info(f"Scraped {len(scraped_articles)} articles from AI company blogs")
        
        # Combine the results
        combined_articles = articles + scraped_articles
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in combined_articles:
            url = article.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        # Save the combined results
        with open("latest_ai_news.json", 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, indent=2, ensure_ascii=False)
        logger.info(f"Combined {len(articles)} NewsAPI articles with {len(scraped_articles)} scraped articles, resulting in {len(unique_articles)} unique articles")
        
        # Step 2: Process with Claude
        logger.info("Step 2: Processing articles with Claude")
        from claude_processor import ClaudeProcessor
        processor = ClaudeProcessor()
        tweet_text = processor.process_news()
        logger.info(f"Generated tweet ({len(tweet_text)} characters)")
        
        # Step 2b: Format and validate tweet
        logger.info("Step 2b: Formatting tweet and validating links")
        from tweet_formatter import TweetFormatter
        formatter = TweetFormatter()
        formatted_tweet = formatter.format_tweet_from_file()
        logger.info(f"Formatted tweet ({len(formatted_tweet)} characters)")
        
        # Step 3: Post to Twitter
        logger.info("Step 3: Posting to Twitter")
        try:
            # Try using Tweepy implementation first
            from tweepy_twitter_poster import TweepyTwitterPoster
            poster = TweepyTwitterPoster()
            result = poster.post_from_file()
            tweet_id = result.get('data', {}).get('id')
            logger.info(f"Posted tweet successfully using Tweepy. Tweet ID: {tweet_id}")
        except Exception as e:
            logger.warning(f"Error using Tweepy poster: {str(e)}. Falling back to original implementation.")
            # Fall back to original implementation
            from twitter_poster import TwitterPoster
            poster = TwitterPoster()
            result = poster.post_from_file()
            tweet_id = result.get('data', {}).get('id')
            logger.info(f"Posted tweet successfully using original implementation. Tweet ID: {tweet_id}")
        
        # Record successful run
        with open("last_successful_run.txt", "w") as f:
            f.write(f"Last successful run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tweet ID: {tweet_id}\n")
            f.write(f"Tweet content: {formatted_tweet}\n")
            f.write(f"Sources: NewsAPI ({len(articles)} articles) and AI company blogs ({len(scraped_articles)} articles)\n")
        
        elapsed_time = time.time() - start_time
        logger.info(f"Final Enhanced AI News Automation completed successfully in {elapsed_time:.2f} seconds")
        return True
        
    except Exception as e:
        logger.error(f"Error in Final Enhanced AI News Automation: {str(e)}")
        # Record error
        with open("error_log.txt", "a") as f:
            f.write(f"Error on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {str(e)}\n")
        return False

if __name__ == "__main__":
    # Check for required libraries
    missing_libraries = []
    
    try:
        import requests
    except ImportError:
        missing_libraries.append("requests")
    
    try:
        import bs4
    except ImportError:
        missing_libraries.append("beautifulsoup4")
    
    try:
        import anthropic
    except ImportError:
        missing_libraries.append("anthropic")
    
    try:
        import tweepy
    except ImportError:
        missing_libraries.append("tweepy")
    
    try:
        import feedparser
    except ImportError:
        print("Warning: feedparser library not installed. For better results with RSS feeds, install it with:")
        print("pip install feedparser")
    
    if missing_libraries:
        print(f"Error: Missing required libraries: {', '.join(missing_libraries)}")
        print("Please install them with:")
        print(f"pip install {' '.join(missing_libraries)}")
        sys.exit(1)
    
    # Run the automation
    run_final_automation()
