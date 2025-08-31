import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv

# Fix import paths - use relative imports
try:
    from .tools.custom_scraper_tool import ScrapeXTool
    from .tools.pdf_write import PDFWriterTool
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from tools.custom_scraper_tool import ScrapeXTool
    from tools.pdf_write import PDFWriterTool

import json
from datetime import datetime
import yaml
from pathlib import Path

def load_config():
    config_dir = Path(__file__).parent / "config"
    
    with open(config_dir / "agents.yaml", 'r') as f:
        agents_config = yaml.safe_load(f)
    
    with open(config_dir / "tasks.yaml", 'r') as f:
        tasks_config = yaml.safe_load(f)
    
    return agents_config, tasks_config

agents_config, tasks_config = load_config()

# Load environment variables
load_dotenv()

provider = os.getenv("PROVIDER", "groq") # default = groq 
if provider == "openai": 
    API_KEY = os.getenv("OPENAI_API_KEY") 
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini") 
else: 
    API_KEY = os.getenv("GROQ_API_KEY") 
    MODEL = os.getenv("MODEL", "llama-3.1-8b-instant") 

if not API_KEY or not MODEL: 
    raise ValueError(f"Please set {provider.upper()} API key and MODEL in your .env file")

@CrewBase
class SentimentXAnalysis():
    """Enhanced SentimentXAnalysis crew with proper tool integration"""

    agents: List[BaseAgent]
    tasks: List[Task]
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        self.provider = provider or os.getenv("PROVIDER", "groq")

        if self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:  # groq default
            self.api_key = api_key or os.getenv("GROQ_API_KEY")
            self.model = model or os.getenv("MODEL", "llama-3.1-8b-instant")

        # fail fast if no API key
        if not self.api_key:
            raise ValueError(f"{self.provider.upper()} API key not found in environment")

        # initialize agents & tasks
        self.agents = [
            self.x_data_collector(),
            self.sentiment_analyzer(),
            self.output_structurer(),
            self.report_generator()
        ]
        self.tasks = [
            self.scrape_tweets_task(),
            self.analyze_sentiment_task(),
            self.structure_output_task(),
            self.generate_report_task()
        ]

    # Target usernames for analysis
    TARGET_USERNAMES = [
        "elonmusk", "naval", "chamath", "garyvee", "balajis",
        "cdixon", "aronvanammers", "aantonop", "VitalikButerin", "satyanadella"
    ]

    @agent
    def x_data_collector(self) -> Agent:
        """Data collection agent with scraping capabilities"""
        try:
            scrape_tool = ScrapeXTool()
            return Agent(
                config=agents_config['x_data_collector'],
                verbose=True,
                tools=[scrape_tool],
                max_execution_time=600,
                max_iter=3
            )
        except Exception as e:
            print(f"Warning: Could not initialize ScrapeXTool: {e}")
            return Agent(
                config=agents_config['x_data_collector'],
                verbose=True,
                tools=[],  # No tools if initialization fails
                max_execution_time=600,
                max_iter=3
            )

    @agent
    def sentiment_analyzer(self) -> Agent:
        """Sentiment analysis agent with LLM capabilities"""
        return Agent(
            config=agents_config['sentiment_analyzer'],
            verbose=True,
            max_execution_time=300,
            max_iter=2
        )

    @agent
    def output_structurer(self) -> Agent:
        """Output structuring and organization agent"""
        return Agent(
            config=agents_config['output_structurer'],
            verbose=True,
            max_execution_time=180,
            max_iter=2
        )

    @agent
    def report_generator(self) -> Agent:
        """Report generation agent with PDF capabilities"""
        try:
            pdf_tool = PDFWriterTool()
            return Agent(
                config=agents_config['report_generator'],
                verbose=True,
                tools=[pdf_tool],
                max_execution_time=240,
                max_iter=2
            )
        except Exception as e:
            print(f"Warning: Could not initialize PDFWriterTool: {e}")
            return Agent(
                config=agents_config['report_generator'],
                verbose=True,
                tools=[],  # No tools if initialization fails
                max_execution_time=240,
                max_iter=2
            )

    @task
    def scrape_tweets_task(self) -> Task:
        """Scrape tweets from selected X/Twitter creators."""
        return Task(
            config=tasks_config.get('scrape_tweets_task', {}),
            agent=self.x_data_collector(),  # Your agent for scraping
            expected_output="""
                Structured JSON containing:
                - Tweet text & timestamp
                - Engagement metrics (likes, retweets, replies, views)
                - User profile info (followers, following, bio)
                - Tweet metadata (hashtags, mentions, URLs)
            """
        )

    @task
    def analyze_sentiment_task(self) -> Task:
        """Perform sentiment analysis on collected tweets."""
        return Task(
            config=tasks_config.get('analyze_sentiment_task', {}),
            agent=self.sentiment_analyzer(),  # Your sentiment analysis agent
            context=[self.scrape_tweets_task()],
            expected_output="Detailed sentiment analysis for all collected tweets"
        )

    @task
    def structure_output_task(self) -> Task:
        """Structure the final output for reporting."""
        return Task(
            config=tasks_config.get('structure_output_task', {}),
            agent=self.output_structurer(),  # Use existing output_structurer agent
            context=[
                self.scrape_tweets_task(),
                self.analyze_sentiment_task()
            ],
            expected_output="Final JSON/CSV/PDF report ready for export"
        )

    @task
    def generate_report_task(self) -> Task:
        """Generate PDF report."""
        return Task(
            config=tasks_config.get('generate_report_task', {}),
            agent=self.report_generator(),  # Use existing report_generator agent
            context=[
                self.scrape_tweets_task(),
                self.analyze_sentiment_task(),
                self.structure_output_task()
            ],
            expected_output="Professional PDF report with visualizations and insights"
        )


    @crew
    def crew(self) -> Crew:
        """Enhanced CrewAI crew with proper task dependencies"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Enable memory for better context retention
        )
    
    def kickoff_with_inputs(self, inputs: dict = None):
        """Kickoff crew with optional inputs"""
        if inputs is None:
            inputs = {
                "usernames": "elonmusk",
                "tweet_count": 5,
                "analysis_focus": "sentiment, financial_tickers, themes"
            }
        
        return self.crew().kickoff(inputs=inputs)
    
    def get_target_usernames(self):
        """Get the list of target usernames"""
        return self.TARGET_USERNAMES 