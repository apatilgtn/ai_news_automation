# AI News Automation System

## Project Overview
This repository contains a comprehensive AI news automation system that fetches the latest AI/tech news, processes it using Claude AI, and posts it to Twitter/X. The system includes multiple components with several enhancements for reliability and quality.

## Core Components

### 1. News Fetching Component (`news_fetcher.py`)
- Uses NewsAPI to fetch the latest AI and tech news articles
- Implements custom queries focused on AI topics (ChatGPT, Claude, OpenAI, Microsoft AI, Kubernetes, DevOps)
- Filters articles for relevance and recency
- Saves articles to JSON for processing

### 2. AI Company Blog Scraper (`ai_blog_scraper.py` and `ai_blog_scraper_improved.py`)
- Directly scrapes news from official AI company blogs:
  - OpenAI
  - Microsoft AI
  - Google AI
  - Anthropic (Claude)
  - Hugging Face
  - Meta AI
- Enhanced version includes RSS feed support for more reliable data
- Implements robust error handling and retry mechanisms
- Merges results with NewsAPI data for comprehensive coverage

### 3. Claude AI Processing Component (`claude_processor.py`)
- Uses Anthropic's Claude API to analyze and summarize news articles
- Selects the most important and interesting AI news stories
- Formats content into engaging tweets with appropriate hashtags
- Handles API authentication and error cases

### 4. Tweet Formatting and Link Validation (`tweet_formatter.py`)
- Validates all links to ensure they're working before posting
- Improves tweet formatting with proper spacing and punctuation
- Formats hashtags consistently (using CamelCase for multi-word tags)
- Intelligently truncates tweets to stay within character limits while preserving important information

### 5. Twitter Posting Component (`twitter_poster.py` and `tweepy_twitter_poster.py`)
- Handles posting to Twitter/X using the Twitter API v2
- Implements OAuth authentication
- Alternative implementation using Tweepy for more reliable authentication
- Includes error handling and logging

### 6. Automation Scripts
- `run_automation.py`: Original automation script combining core components
- `run_with_blog_scraper.py`: Enhanced script adding blog scraping
- `enhanced_run_automation.py`: Script with improved blog scraper
- `final_ai_news_automation.py`: Complete solution with all enhancements

## Technical Details

### Dependencies
- Python 3.x
- Required packages:
  - requests: For API calls and HTTP requests
  - beautifulsoup4 (bs4): For web scraping
  - anthropic: For Claude API access
  - tweepy: For Twitter API access
  - feedparser: For RSS feed handling

### API Requirements
- NewsAPI key: For fetching news articles
- Anthropic API key: For accessing Claude
- Twitter API credentials: API key/secret and access token/secret with Read and Write permissions

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-news-automation.git
cd ai-news-automation

# Install dependencies
pip install requests beautifulsoup4 anthropic tweepy feedparser python-dotenv

# Set up environment variables
# Create a .env file with your API keys
```

### Configuration
Create a `.env` file with the following variables:
```
# News API
NEWSAPI_KEY=your_newsapi_key

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Twitter API
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
```

## Usage

### Running the Complete Automation
```bash
python final_ai_news_automation.py
```

### Running Individual Components
```bash
# Fetch news articles
python news_fetcher.py

# Scrape AI company blogs
python ai_blog_scraper_improved.py

# Process news with Claude
python claude_processor.py

# Format and validate tweets
python tweet_formatter.py

# Post to Twitter
python tweepy_twitter_poster.py
```

## Future Enhancements
1. **Sentiment Analysis**: Add sentiment analysis to focus on positive AI news
2. **Image Generation**: Generate images for tweets using AI image generation
3. **Multi-platform Posting**: Extend to post on LinkedIn, Mastodon, and other platforms
4. **Interactive Feedback**: Analyze engagement metrics to improve content selection
5. **Custom News Categories**: Allow configuration of specific AI topics to focus on
6. **Scheduled Posting**: Implement time-based scheduling for optimal posting times
7. **Thread Support**: Create Twitter threads for more detailed news summaries
8. **Content Curation**: Add human-in-the-loop approval before posting

## Troubleshooting
- **API Authentication Issues**: Ensure all API keys are correctly set in the .env file
- **Twitter Posting Errors**: Verify Twitter Developer App has "Read and Write" permissions
- **Web Scraping Failures**: Some websites may block scraping; the system will fall back to NewsAPI
- **Character Limit Warnings**: The tweet formatter will automatically handle truncation

## License
This project is available under the MIT License.
