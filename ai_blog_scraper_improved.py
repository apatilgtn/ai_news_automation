#!/usr/bin/env python3
"""
Improved AI Company Blog Scraper for AI News Automation

This script scrapes the official blogs and news pages of major AI companies
to get the latest news and announcements directly from the source.
Includes improved selectors and more robust error handling.
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import random
import os
from datetime import datetime, timedelta
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_blog_scraper_improved')

class AIBlogScraperImproved:
    """Class to handle scraping AI company blogs and news pages with improved robustness"""
    
    def __init__(self):
        """Initialize the scraper with common headers and settings"""
        # Use a more browser-like user agent to avoid being blocked
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
        # Define the company blogs to scrape with their specific selectors
        # Updated selectors based on current website structures
        self.blogs = [
            {
                "name": "OpenAI",
                "url": "https://openai.com/blog",
                "article_selector": "a[href^='/blog/']",
                "title_selector": "h2, h3",
                "date_selector": "time",
                "description_selector": "p",
                "base_url": "https://openai.com",
                "use_rss": False,
                "rss_url": ""
            },
            {
                "name": "Microsoft AI",
                "url": "https://blogs.microsoft.com/ai/",
                "article_selector": "article.post",
                "title_selector": "h3.entry-title a",
                "date_selector": "time.entry-date",
                "description_selector": "div.entry-summary p",
                "base_url": "",
                "use_rss": True,
                "rss_url": "https://blogs.microsoft.com/ai/feed/"
            },
            {
                "name": "Google AI",
                "url": "https://ai.googleblog.com/",
                "article_selector": "div.post",
                "title_selector": "h2.title a",
                "date_selector": "div.published",
                "description_selector": "div.post-body",
                "base_url": "",
                "use_rss": True,
                "rss_url": "http://ai.googleblog.com/feeds/posts/default"
            },
            {
                "name": "Anthropic",
                "url": "https://www.anthropic.com/news",
                "article_selector": "a[href^='/news/']",
                "title_selector": "h3",
                "date_selector": "time",
                "description_selector": "p",
                "base_url": "https://www.anthropic.com",
                "use_rss": False,
                "rss_url": ""
            },
            {
                "name": "Hugging Face",
                "url": "https://huggingface.co/blog",
                "article_selector": "a.group",
                "title_selector": "p.font-bold",
                "date_selector": "p.text-sm",
                "description_selector": "p:not(.font-bold):not(.text-sm)",
                "base_url": "https://huggingface.co",
                "use_rss": False,
                "rss_url": ""
            },
            {
                "name": "Meta AI",
                "url": "https://ai.meta.com/blog/",
                "article_selector": "div.blog-card",
                "title_selector": "h3",
                "date_selector": "div.blog-card__date",
                "description_selector": "p.blog-card__description",
                "base_url": "https://ai.meta.com",
                "use_rss": True,
                "rss_url": "https://ai.meta.com/blog/rss/"
            }
        ]
    
    def scrape_all_blogs(self, days_back=7, max_articles_per_blog=3):
        """
        Scrape all configured AI company blogs
        
        Args:
            days_back (int): Only include articles published within this many days
            max_articles_per_blog (int): Maximum number of articles to include per blog
            
        Returns:
            list: List of article dictionaries
        """
        all_articles = []
        
        # Get current date for filtering recent articles
        current_date = datetime.now()
        cutoff_date = current_date - timedelta(days=days_back)
        
        for blog in self.blogs:
            logger.info(f"Scraping {blog['name']} blog at {blog['url']}")
            
            try:
                # Add a random delay to avoid overloading servers
                time.sleep(random.uniform(2, 5))
                
                # Try RSS feed first if available
                if blog["use_rss"] and blog["rss_url"]:
                    articles = self._scrape_rss_feed(blog, max_articles_per_blog)
                    if articles:
                        all_articles.extend(articles)
                        logger.info(f"Added {len(articles)} articles from {blog['name']} RSS feed")
                        continue
                
                # Fall back to HTML scraping if RSS fails or isn't available
                # Use a session with cookies and referrer to appear more like a browser
                session = requests.Session()
                session.headers.update(self.headers)
                session.headers.update({"Referer": "https://www.google.com/"})
                
                # Fetch the blog page
                response = session.get(blog["url"], timeout=15)
                response.raise_for_status()  # Raise exception for HTTP errors
                
                # Parse the HTML
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Find all article elements
                article_elements = soup.select(blog["article_selector"])
                logger.info(f"Found {len(article_elements)} article elements on {blog['name']} blog")
                
                # Process each article
                blog_articles = []
                for article_elem in article_elements:
                    try:
                        # Extract article details
                        article_data = self._extract_article_data(article_elem, blog)
                        
                        if article_data:
                            blog_articles.append(article_data)
                            
                            # Stop if we've reached the maximum number of articles for this blog
                            if len(blog_articles) >= max_articles_per_blog:
                                break
                    except Exception as e:
                        logger.error(f"Error processing article from {blog['name']}: {str(e)}")
                
                # Add articles from this blog to the overall list
                all_articles.extend(blog_articles)
                logger.info(f"Added {len(blog_articles)} articles from {blog['name']}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching {blog['name']} blog: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error scraping {blog['name']} blog: {str(e)}")
        
        logger.info(f"Scraped a total of {len(all_articles)} articles from all blogs")
        return all_articles
    
    def _scrape_rss_feed(self, blog, max_articles):
        """
        Scrape articles from an RSS feed
        
        Args:
            blog: Blog configuration dictionary
            max_articles: Maximum number of articles to retrieve
            
        Returns:
            list: List of article dictionaries
        """
        try:
            import feedparser
            
            logger.info(f"Attempting to fetch RSS feed for {blog['name']} from {blog['rss_url']}")
            feed = feedparser.parse(blog['rss_url'])
            
            if not feed.entries:
                logger.warning(f"No entries found in RSS feed for {blog['name']}")
                return []
            
            articles = []
            for entry in feed.entries[:max_articles]:
                try:
                    title = entry.title
                    url = entry.link
                    
                    # Try to get published date
                    if hasattr(entry, 'published'):
                        date_str = entry.published
                    elif hasattr(entry, 'updated'):
                        date_str = entry.updated
                    else:
                        date_str = datetime.now().strftime("%Y-%m-%d")
                    
                    # Try to get description
                    if hasattr(entry, 'summary'):
                        description = entry.summary
                    elif hasattr(entry, 'description'):
                        description = entry.description
                    else:
                        description = f"Latest from {blog['name']}: {title}"
                    
                    # Clean up HTML from description
                    if description:
                        soup = BeautifulSoup(description, 'html.parser')
                        description = soup.get_text()
                    
                    article_data = {
                        "source": {"name": blog["name"]},
                        "title": title,
                        "url": url,
                        "publishedAt": date_str,
                        "description": description
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    logger.error(f"Error processing RSS entry for {blog['name']}: {str(e)}")
            
            logger.info(f"Retrieved {len(articles)} articles from {blog['name']} RSS feed")
            return articles
            
        except ImportError:
            logger.warning("feedparser library not installed. Install with: pip install feedparser")
            return []
        except Exception as e:
            logger.error(f"Error fetching RSS feed for {blog['name']}: {str(e)}")
            return []
    
    def _extract_article_data(self, article_elem, blog):
        """
        Extract article data from an article element
        
        Args:
            article_elem: BeautifulSoup element for the article
            blog: Blog configuration dictionary
            
        Returns:
            dict: Article data or None if extraction failed
        """
        # Extract title
        if blog["title_selector"]:
            title_elem = article_elem.select_one(blog["title_selector"])
            title = title_elem.text.strip() if title_elem else None
        else:
            title = article_elem.text.strip()
        
        if not title:
            return None
        
        # Extract URL
        if article_elem.name == 'a':
            url = article_elem.get("href", "")
        else:
            url_elem = article_elem.select_one("a")
            url = url_elem.get("href", "") if url_elem else ""
        
        # Handle relative URLs
        if url and not url.startswith(("http://", "https://")):
            url = urljoin(blog["base_url"] if blog["base_url"] else blog["url"], url)
        
        if not url:
            return None
        
        # Extract date
        date_str = None
        if blog["date_selector"]:
            date_elem = article_elem.select_one(blog["date_selector"])
            date_str = date_elem.text.strip() if date_elem else None
        
        # Extract description
        description = None
        if blog["description_selector"]:
            desc_elem = article_elem.select_one(blog["description_selector"])
            description = desc_elem.text.strip() if desc_elem else None
        
        # If no description found, try to fetch it from the article page
        if not description and url:
            try:
                description = self._fetch_description_from_article(url)
            except Exception as e:
                logger.warning(f"Could not fetch description from article URL: {str(e)}")
        
        # Format as a news article
        article_data = {
            "source": {"name": blog["name"]},
            "title": title,
            "url": url,
            "publishedAt": date_str or datetime.now().strftime("%Y-%m-%d"),
            "description": description or f"Latest from {blog['name']}: {title}"
        }
        
        return article_data
    
    def _fetch_description_from_article(self, url):
        """
        Fetch the description from an article page
        
        Args:
            url: URL of the article
            
        Returns:
            str: Article description or None
        """
        # Add a small delay to avoid overloading servers
        time.sleep(random.uniform(1, 2))
        
        # Use a session with cookies and referrer to appear more like a browser
        session = requests.Session()
        session.headers.update(self.headers)
        session.headers.update({"Referer": "https://www.google.com/"})
        
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Try meta description first
        meta_desc = soup.select_one("meta[name='description']")
        if meta_desc and meta_desc.get("content"):
            return meta_desc.get("content")
        
        # Try first paragraph
        first_p = soup.select_one("article p, .article p, .post p, .content p")
        if first_p:
            return first_p.text.strip()
        
        return None
    
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
    
    def merge_with_newsapi_results(self, scraped_articles, newsapi_file="newsapi_articles.json"):
        """
        Merge scraped articles with NewsAPI results
        
        Args:
            scraped_articles (list): List of scraped article dictionaries
            newsapi_file (str): Path to NewsAPI results file
            
        Returns:
            list: Combined list of articles
        """
        try:
            # Load NewsAPI articles if file exists
            if os.path.exists(newsapi_file):
                with open(newsapi_file, 'r', encoding='utf-8') as f:
                    newsapi_articles = json.load(f)
                
                # Combine the articles
                combined_articles = scraped_articles + newsapi_articles
                
                # Remove duplicates based on URL
                seen_urls = set()
                unique_articles = []
                
                for article in combined_articles:
                    url = article.get("url")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        unique_articles.append(article)
                
                logger.info(f"Combined {len(scraped_articles)} scraped articles with {len(newsapi_articles)} NewsAPI articles, resulting in {len(unique_articles)} unique articles")
                return unique_articles
            else:
                logger.info(f"NewsAPI file {newsapi_file} not found, using only scraped articles")
                return scraped_articles
        except Exception as e:
            logger.error(f"Error merging articles: {str(e)}")
            return scraped_articles


# Example usage
if __name__ == "__main__":
    try:
        import os
        
        # Check for feedparser
        try:
            import feedparser
            logger.info("feedparser is installed, RSS feeds will be used when available")
        except ImportError:
            logger.warning("feedparser is not installed. Install with: pip install feedparser")
            logger.warning("RSS feeds will not be used, falling back to HTML scraping")
        
        # Create scraper instance
        scraper = AIBlogScraperImproved()
        
        # Scrape all blogs
        articles = scraper.scrape_all_blogs(days_back=7, max_articles_per_blog=3)
        
        # Save scraped articles to a separate file
        scraper.save_articles_to_file(articles, "scraped_ai_news.json")
        
        # Optionally merge with NewsAPI results
        if os.path.exists("latest_ai_news.json"):
            # Rename the existing file to preserve NewsAPI results
            os.rename("latest_ai_news.json", "newsapi_articles.json")
            
            # Merge the results
            combined_articles = scraper.merge_with_newsapi_results(articles)
            
            # Save combined results
            scraper.save_articles_to_file(combined_articles)
        else:
            # Just use the scraped articles
            scraper.save_articles_to_file(articles)
        
        # Print summary
        print(f"\nRetrieved {len(articles)} articles from AI company blogs")
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article.get('title')}")
            print(f"   Source: {article.get('source', {}).get('name')}")
            print(f"   URL: {article.get('url')}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
