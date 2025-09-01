import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

# Import tools (scraper + PDF writer) with fallback for relative imports
try:
    from .tools.custom_scraper_tool import ScrapeXTool
    from .tools.pdf_write import PDFWriterTool
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from tools.custom_scraper_tool import ScrapeXTool
    from tools.pdf_write import PDFWriterTool


# ----------------------------
# Load agent & task definitions from YAML configs
# ----------------------------
def load_config():
    config_dir = Path(__file__).parent / "config"
    with open(config_dir / "agents.yaml", "r") as f:
        agents_config = yaml.safe_load(f)
    with open(config_dir / "tasks.yaml", "r") as f:
        tasks_config = yaml.safe_load(f)
    return agents_config, tasks_config


agents_config, tasks_config = load_config()

# ----------------------------
# Environment setup
# ----------------------------
load_dotenv()
provider = os.getenv("PROVIDER", "groq")  # default = groq

if provider == "openai":
    API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
else:
    API_KEY = os.getenv("GROQ_API_KEY")
    MODEL = os.getenv("MODEL", "llama-3.1-8b-instant")

if not API_KEY or not MODEL:
    raise ValueError(f"Please set {provider.upper()} API key and MODEL in your .env file")


# ----------------------------
# Crew Definition
# ----------------------------
@CrewBase
class SentimentXAnalysis:
    """CrewAI setup for sentiment analysis on X/Twitter data"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        """Initialize crew with correct provider, API key, and model"""
        self.provider = provider or os.getenv("PROVIDER", "groq")

        if self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:  # default to Groq
            self.api_key = api_key or os.getenv("GROQ_API_KEY")
            self.model = model or os.getenv("MODEL", "llama-3.1-8b-instant")

        # Fail fast if no API key is available
        if not self.api_key:
            raise ValueError(f"{self.provider.upper()} API key not found in environment")

        # Initialize crew components
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

    # Example default creators for analysis
    TARGET_USERNAMES = [
        "elonmusk", "naval", "chamath", "garyvee", "balajis",
        "cdixon", "aronvanammers", "aantonop", "VitalikButerin", "satyanadella"
    ]

    # ----------------------------
    # Agents
    # ----------------------------
    @agent
    def x_data_collector(self) -> Agent:
        """Collects tweets and metadata via custom scraper"""
        try:
            scrape_tool = ScrapeXTool()
            return Agent(
                config=agents_config["x_data_collector"],
                verbose=True,
                tools=[scrape_tool],
                max_execution_time=600,
                max_iter=3,
            )
        except Exception as e:
            print(f"Warning: Could not initialize ScrapeXTool: {e}")
            return Agent(
                config=agents_config["x_data_collector"],
                verbose=True,
                tools=[],  # fallback: no tools if scraper fails
                max_execution_time=600,
                max_iter=3,
            )

    @agent
    def sentiment_analyzer(self) -> Agent:
        """Analyzes sentiment in scraped tweets"""
        return Agent(
            config=agents_config["sentiment_analyzer"],
            verbose=True,
            max_execution_time=300,
            max_iter=2,
        )

    @agent
    def output_structurer(self) -> Agent:
        """Organizes raw results into structured formats"""
        return Agent(
            config=agents_config["output_structurer"],
            verbose=True,
            max_execution_time=180,
            max_iter=2,
        )

    @agent
    def report_generator(self) -> Agent:
        """Generates PDF reports using ReportLab"""
        try:
            pdf_tool = PDFWriterTool()
            return Agent(
                config=agents_config["report_generator"],
                verbose=True,
                tools=[pdf_tool],
                max_execution_time=240,
                max_iter=2,
            )
        except Exception as e:
            print(f"Warning: Could not initialize PDFWriterTool: {e}")
            return Agent(
                config=agents_config["report_generator"],
                verbose=True,
                tools=[],  # fallback if PDF writer fails
                max_execution_time=240,
                max_iter=2,
            )

    # ----------------------------
    # Tasks
    # ----------------------------
    @task
    def scrape_tweets_task(self) -> Task:
        """Task: Scrape tweets from target usernames"""
        return Task(
            config=tasks_config.get("scrape_tweets_task", {}),
            agent=self.x_data_collector(),
            expected_output="""
                JSON with:
                - Tweet text & timestamp
                - Engagement metrics (likes, retweets, replies, views)
                - User profile info (followers, following, bio)
                - Metadata (hashtags, mentions, URLs)
            """,
        )

    @task
    def analyze_sentiment_task(self) -> Task:
        """Task: Perform sentiment analysis on collected tweets"""
        return Task(
            config=tasks_config.get("analyze_sentiment_task", {}),
            agent=self.sentiment_analyzer(),
            context=[self.scrape_tweets_task()],
            expected_output="Detailed sentiment analysis results",
        )

    @task
    def structure_output_task(self) -> Task:
        """Task: Structure final output for reporting"""
        return Task(
            config=tasks_config.get("structure_output_task", {}),
            agent=self.output_structurer(),
            context=[
                self.scrape_tweets_task(),
                self.analyze_sentiment_task(),
            ],
            expected_output="Final JSON/CSV/PDF report ready for export",
        )

    @task
    def generate_report_task(self) -> Task:
        """Task: Generate professional PDF report"""
        return Task(
            config=tasks_config.get("generate_report_task", {}),
            agent=self.report_generator(),
            context=[
                self.scrape_tweets_task(),
                self.analyze_sentiment_task(),
                self.structure_output_task(),
            ],
            expected_output="Polished PDF report with visualizations and insights",
        )

    # ----------------------------
    # Crew Orchestration
    # ----------------------------
    @crew
    def crew(self) -> Crew:
        """Define the full sequential workflow"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # can be enabled for context retention
        )

    def kickoff_with_inputs(self, inputs: dict = None):
        """Run workflow with optional input overrides"""
        if inputs is None:
            inputs = {
                "usernames": "elonmusk",
                "tweet_count": 5,
                "analysis_focus": "sentiment, financial_tickers, themes",
            }
        return self.crew().kickoff(inputs=inputs)

    def get_target_usernames(self):
        """Return default list of target usernames"""
        return self.TARGET_USERNAMES
