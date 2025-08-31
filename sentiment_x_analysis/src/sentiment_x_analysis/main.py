#!/usr/bin/env python3
"""
Main execution script for X Creator Sentiment Analysis
Uses CrewAI Flow for orchestrated execution
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
from sentiment_x_analysis.crew import SentimentXAnalysis  

# Load environment variables
load_dotenv()
PROVIDER = os.getenv("PROVIDER", "groq")  # default = groq

if PROVIDER == "openai":
    API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
else:
    API_KEY = os.getenv("GROQ_API_KEY")
    MODEL = os.getenv("MODEL", "llama-3.1-8b-instant")

if not API_KEY or not MODEL:
    raise ValueError(f"Please set {PROVIDER.upper()} API key and MODEL in your .env file")

# Setup timestamped log directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = Path("logs") / f"run_{timestamp}"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "sentiment_analysis.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SentimentAnalysisFlow:
    """Orchestrates the sentiment analysis workflow"""

    def __init__(self):
        # Create directories for outputs
        for directory in ['outputs', 'outputs/json', 'outputs/reports', 'outputs/charts']:
            Path(directory).mkdir(exist_ok=True)
        self.crew_instance = None

    def initialize_crew(self):
        """Initialize the sentiment analysis crew with Groq"""
        logger.info("🚀 Initializing Sentiment Analysis Crew with Groq...")
        try:
            self.crew_instance = SentimentXAnalysis(
                api_key=API_KEY,
                model=MODEL,
                provider=PROVIDER
            )
            logger.info("✅ Crew initialized successfully")
            return {"status": "initialized", "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"❌ Failed to initialize crew: {str(e)}")
            return {"status": "error", "error": str(e)}

    def execute_analysis(self):
        """Run the sentiment analysis"""
        if not self.crew_instance:
            logger.error("Crew is not initialized!")
            return {"status": "error", "error": "Crew not initialized"}

        logger.info("🔄 Running sentiment analysis...")
        try:
            result = self.crew_instance.crew().kickoff()
            results_file = Path(f"outputs/json/analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(results_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"✅ Analysis completed. Results saved to: {results_file}")
            return {"status": "completed", "results": result, "results_file": str(results_file)}
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def generate_summary(self, analysis_result: Dict[str, Any]):
        """Generate summary information"""
        logger.info("📊 Generating summary...")
        try:
            status = analysis_result.get("status")
            if status == "completed":
                results_file = analysis_result.get("results_file")
                logger.info(f"🎉 Analysis completed successfully!")
                logger.info(f"📁 Results file: {results_file}")
            else:
                logger.error(f"❌ Workflow failed: {analysis_result.get('error', 'Unknown error')}")
            return {"final_status": status, "completion_time": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {"final_status": "error", "error": str(e)}


def run_flow():
    """Run the full workflow sequentially"""
    logger.info("🚀 Starting Sentiment Analysis Flow")
    flow = SentimentAnalysisFlow()

    init_result = flow.initialize_crew()
    if init_result.get("status") != "initialized":
        return {"status": "error", "stage": "initialization", "details": init_result}

    analysis_result = flow.execute_analysis()
    summary_result = flow.generate_summary(analysis_result)

    logger.info("🏁 Flow execution finished")
    return {"status": summary_result.get("final_status"), "init_result": init_result,
            "analysis_result": analysis_result, "summary_result": summary_result}


def run_simple():
    """Run analysis in simple mode without full flow"""
    logger.info("⚡ Starting Simple Sentiment Analysis with Groq")
    try:
        crew = SentimentXAnalysis(
            api_key=API_KEY,
            model=MODEL,
            provider=PROVIDER
        )
        result = crew.kickoff_with_inputs({
    "usernames": "elonmusk",  
    "tweet_count": 5,  
    "analysis_focus": "sentiment, financial_tickers, themes"
})
        results_file = Path(f"outputs/json/simple_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"✅ Analysis completed. Results saved to: {results_file}")
        return {"status": "success", "results_file": str(results_file)}
    except Exception as e:
        logger.error(f"❌ Simple analysis failed: {str(e)}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    print("=" * 60)
    print("X CREATOR SENTIMENT ANALYSIS")
    print("=" * 60)

    use_flow = len(sys.argv) > 1 and sys.argv[1] == "--flow"
    if use_flow:
        result = run_flow()
    else:
        result = run_simple()

    print("=" * 60)
    print(f"Final Status: {result.get('status', 'unknown')}")
    print(f"Logs saved at: {log_file}")
    print("=" * 60)
