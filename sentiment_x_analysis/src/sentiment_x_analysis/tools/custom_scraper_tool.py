import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import logging

# Configure logging for monitoring and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------- #
# Data Models for Structured Output
# ----------------------------- #

class TweetData(BaseModel):
    """Schema for individual tweet data."""
    tweet_id: str
    username: str
    text: str
    timestamp: str
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    views: int = 0
    hashtags: List[str] = []
    mentions: List[str] = []
    urls: List[str] = []

class UserData(BaseModel):
    """Schema for user profile data."""
    username: str
    display_name: str
    bio: str
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    verified: bool = False

class ScrapeXToolSchema(BaseModel):
    """Input schema for ScrapeXTool."""
    usernames: List[str] = Field(..., description="List of usernames to scrape (without @)")
    tweet_count: int = Field(5, description="Number of tweets per user to collect")

# ----------------------------- #
# Scraper Tool Implementation
# ----------------------------- #

class ScrapeXTool(BaseTool):
    """
    Enhanced Twitter/X scraper tool.
    
    Features:
    - Collects tweets and user profile data.
    - Generates engagement metrics and metadata.
    - Handles rate limiting via random delays.
    - Provides structured output for downstream agents.
    - Uses sample data generation (can be replaced with real scraping logic).
    """

    name: str = "scrape_x_tool"
    description: str = (
        "Scrapes tweets and user data from X (Twitter) for specified usernames. "
        "Collects comprehensive data including engagement metrics, user profiles, "
        "and tweet metadata. Handles rate limiting and provides structured output."
    )

    args_schema: type[BaseModel] = ScrapeXToolSchema 
    
    def __init__(self):
        """Initialize the scraper tool."""
        super().__init__()
        
    # ----------------------------- #
    # Utility Helpers
    # ----------------------------- #

    def _random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Sleep for a random interval to simulate network delay and avoid rate limits."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    # ----------------------------- #
    # Sample Data Generators
    # ----------------------------- #

    def _generate_sample_tweets(self, username: str, count: int = 50) -> List[TweetData]:
        """
        Generate sample tweet data for a given user.
        Used as a placeholder instead of real scraping.
        """
        logger.info(f"Generating {count} sample tweets for @{username}")
        
        # Simple tweet templates for demonstration
        tweet_templates = [
            "{topic} is the future",
            "Bullish on {topic}",
            "Building with {topic}",
            "{topic} update coming",
            "Love {topic} community"
        ]
        
        # Topic themes mapped to known usernames
        topic_themes = {
            'elonmusk': ['Tesla', 'SpaceX', 'AI', 'Mars', 'sustainable energy', 'neural interfaces'],
            'naval': ['startups', 'investing', 'philosophy', 'wealth creation', 'happiness'],
            'chamath': ['venture capital', 'SPACs', 'technology', 'social media', 'investing'],
            'garyvee': ['marketing', 'entrepreneurship', 'NFTs', 'social media', 'hustle'],
            'balajis': ['crypto', 'decentralization', 'network states', 'technology', 'Bitcoin'],
            'cdixon': ['crypto', 'web3', 'investing', 'technology trends', 'blockchain'],
            'aronvanammers': ['AI', 'machine learning', 'technology', 'automation', 'future'],
            'aantonop': ['Bitcoin', 'cryptocurrency', 'blockchain', 'decentralization', 'privacy'],
            'VitalikButerin': ['Ethereum', 'blockchain', 'crypto economics', 'scalability', 'DeFi'],
            'satyanadella': ['Microsoft', 'cloud computing', 'AI', 'digital transformation', 'leadership']
        }
        
        # Default topics if username not in mapping
        topics = topic_themes.get(username, ['technology', 'innovation', 'business', 'future', 'AI'])
        tweets = []
        
        for i in range(count):
            # Pick random template + topic
            template = random.choice(tweet_templates)
            topic = random.choice(topics)
            text = template.format(topic=topic)
            
            # Simulate engagement metrics
            base_engagement = random.randint(100, 10000)
            likes = base_engagement + random.randint(0, base_engagement * 2)
            retweets = int(likes * random.uniform(0.1, 0.3))
            replies = int(likes * random.uniform(0.05, 0.15))
            views = likes * random.randint(10, 50)
            
            # Generate a pseudo-random timestamp (within last 30 days)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # Extract hashtags/mentions (if present)
            hashtags = [word[1:] for word in text.split() if word.startswith('#')]
            mentions = [word[1:] for word in text.split() if word.startswith('@')]
            
            # Construct tweet object
            tweet = TweetData(
                tweet_id=f"{username}_{i}_{int(timestamp.timestamp())}",
                username=username,
                text=text,
                timestamp=timestamp.isoformat(),
                likes=likes,
                retweets=retweets,
                replies=replies,
                views=views,
                hashtags=hashtags,
                mentions=mentions,
                urls=[]
            )
            tweets.append(tweet)
            
        return tweets
    
    def _generate_sample_user_data(self, username: str) -> UserData:
        """
        Generate sample user profile data.
        If username not predefined, generate random profile stats.
        """
        user_profiles = {
            'elonmusk': {
                'display_name': 'Elon Musk',
                'bio': 'CEO of Tesla, SpaceX, and more. Building the future.',
                'followers_count': 150000000,
                'following_count': 500,
                'tweet_count': 25000,
                'verified': True
            },
            'naval': {
                'display_name': 'Naval',
                'bio': 'Entrepreneur, investor, and philosopher.',
                'followers_count': 2000000,
                'following_count': 100,
                'tweet_count': 15000,
                'verified': True
            },
            'chamath': {
                'display_name': 'Chamath Palihapitiya',
                'bio': 'Venture capitalist and entrepreneur.',
                'followers_count': 1500000,
                'following_count': 200,
                'tweet_count': 12000,
                'verified': True
            },
            'garyvee': {
                'display_name': 'Gary Vaynerchuk',
                'bio': 'Entrepreneur, CEO, investor, and content creator.',
                'followers_count': 3000000,
                'following_count': 300000,
                'tweet_count': 200000,
                'verified': True
            },
            'balajis': {
                'display_name': 'Balaji Srinivasan',
                'bio': 'Entrepreneur, investor, technologist.',
                'followers_count': 800000,
                'following_count': 1000,
                'tweet_count': 20000,
                'verified': True
            }
        }
        
        # Fallback: generate random profile if not in mapping
        profile = user_profiles.get(username, {
            'display_name': username.title(),
            'bio': f'Content creator and thought leader @{username}',
            'followers_count': random.randint(10000, 1000000),
            'following_count': random.randint(100, 5000),
            'tweet_count': random.randint(1000, 50000),
            'verified': random.choice([True, False])
        })
        
        return UserData(username=username, **profile)
    
    # ----------------------------- #
    # Main Execution
    # ----------------------------- #

    def _run(self, usernames: str, tweet_count: int = 5) -> str:
        """
        Main entrypoint for tool execution.
        
        Args:
            usernames (str | list): Usernames to scrape.
            tweet_count (int): Number of tweets per user.
        
        Returns:
            str: JSON string with scraping results and metadata.
        """
        # Initialize session (placeholder for real HTTP requests)
        session = requests.Session()
        session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        })
        try:
            # Normalize input: allow comma-separated str or list
            if isinstance(usernames, str):
                username_list = [u.strip().replace('@', '') for u in usernames.split(',')]
            else:
                username_list = usernames
            
            logger.info(f"Starting scrape for users: {username_list}")
            
            # Initialize result container
            results = {
                'scrape_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'usernames_requested': username_list,
                    'tweets_per_user': tweet_count,
                    'total_users': len(username_list),
                    'scrape_method': 'sample_data_generator'
                },
                'users': {},
                'summary': {}
            }
            
            total_tweets = 0
            successful_scrapes = 0
            
            # Process each username
            for username in username_list:
                try:
                    logger.info(f"Processing user: @{username}")
                    
                    # Generate synthetic user + tweet data
                    user_data = self._generate_sample_user_data(username)
                    tweets = self._generate_sample_tweets(username, tweet_count)
                    
                    # Store structured results
                    results['users'][username] = {
                        'user_info': {
                            'username': user_data.username,
                            'display_name': user_data.display_name,
                            'followers_count': user_data.followers_count
                        },
                        'tweets': [
                            {'text': tweet.text[:50], 'likes': tweet.likes}
                            for tweet in tweets[:10]  # Truncate to 10 tweets
                        ],
                        'tweet_count': min(len(tweets), 10),
                        'scrape_success': True
                    }
                    
                    total_tweets += len(tweets)
                    successful_scrapes += 1
                    
                    # Sleep between users to mimic network delay
                    self._random_delay(1, 3)
                    
                    logger.info(f"Successfully scraped {len(tweets)} tweets for @{username}")
                    
                except Exception as e:
                    # Handle scraping failure gracefully
                    logger.error(f"Error scraping @{username}: {str(e)}")
                    results['users'][username] = {
                        'user_info': None,
                        'tweets': [],
                        'tweet_count': 0,
                        'scrape_success': False,
                        'error': str(e)
                    }
            
            # Add overall summary
            results['summary'] = {
                'total_tweets_collected': total_tweets,
                'successful_scrapes': successful_scrapes,
                'failed_scrapes': len(username_list) - successful_scrapes,
                'success_rate': successful_scrapes / len(username_list) if username_list else 0,
                'average_tweets_per_user': (
                    total_tweets / successful_scrapes if successful_scrapes > 0 else 0
                )
            }
            
            logger.info(f"Scraping completed. Total tweets: {total_tweets}")
            
            # Return results as JSON
            return json.dumps(results, indent=2, default=str)
            
        except Exception as e:
            # Global error handling
            error_msg = f"Error in ScrapeXTool execution: {str(e)}"
            logger.error(error_msg)
            return json.dumps({
                'error': error_msg,
                'timestamp': datetime.now().isoformat(),
                'success': False
            }, indent=2)

# Alias for backwards compatibility
TwitterScraperTool = ScrapeXTool
