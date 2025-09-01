"""
PDF Report Generation Tool for CrewAI
-------------------------------------
Creates professional PDF reports with charts and visualizations.
Includes fallback support using matplotlib when ReportLab is unavailable.
"""

import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Any, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import logging
from pathlib import Path

# ================================================================
# Attempt to import ReportLab (preferred library for PDFs)
# Falls back to matplotlib-based PDFs if ReportLab is unavailable
# ================================================================
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, blue, red, green
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
    print("✅ ReportLab loaded successfully")
except ImportError as e:
    print(f"⚠️ ReportLab not available: {e}")
    print("📝 Using matplotlib fallback for PDF generation")

# Force matplotlib to use a non-GUI backend (for server environments)
import matplotlib
matplotlib.use('Agg')

# Setup logging for debugging and status updates
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================================================
# PDFWriterTool Class
# ================================================================
class PDFWriterTool(BaseTool):
    """Professional PDF report generation tool with charts and visualizations."""
    
    # Metadata for CrewAI tool registry
    name: str = "pdf_writer_tool"
    description: str = (
        "Generates professional PDF reports from structured analysis data. "
        "Includes visualizations, charts, and executive summaries."
    )
    
    def __init__(self):
        """Initialize the PDF tool, configure styles, and set up output folders."""
        super().__init__()
        
        # Configure matplotlib & seaborn styles
        try:
            plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        except:
            plt.style.use('default')
        try:
            sns.set_palette("husl")
        except:
            pass  # Ignore if seaborn is not installed
        
        # Ensure output directories exist
        Path("outputs").mkdir(exist_ok=True)
        Path("outputs/reports").mkdir(exist_ok=True)
        Path("outputs/charts").mkdir(exist_ok=True)
        
        logger.info(f"PDFWriterTool initialized. ReportLab available: {REPORTLAB_AVAILABLE}")
    
    # ------------------------------------------------------------
    # Chart Creation Helpers
    # ------------------------------------------------------------
    def _create_sentiment_chart(self, data: Dict, filename: str) -> str:
        """Generate sentiment distribution and trend charts using matplotlib."""
        # (Chart plotting logic here)
        ...
    
    def _create_financial_chart(self, data: Dict, filename: str) -> str:
        """Generate financial sentiment and correlation charts."""
        # (Chart plotting logic here)
        ...
    
    # ------------------------------------------------------------
    # PDF Generation Helpers
    # ------------------------------------------------------------
    def _generate_simple_pdf(self, data: Dict, output_path: str) -> bool:
        """
        Generate a simple, text-based PDF report using matplotlib.
        Fallback when ReportLab is not available.
        """
        ...
    
    def _generate_reportlab_pdf(self, data: Dict, output_path: str) -> bool:
        """
        Generate a full-featured professional PDF report using ReportLab.
        Includes tables, formatted text, and layout control.
        """
        ...
    
    # ------------------------------------------------------------
    # Main Run Method (Entry Point)
    # ------------------------------------------------------------
    def _run(self, data: Dict[str, Any], output_filename: Optional[str] = None) -> str:
        """
        Generate a PDF report from structured sentiment analysis data.

        Args:
            data (Dict): Input data containing summary, users, topics, etc.
            output_filename (str, optional): Custom filename for the report.

        Returns:
            str: Path to the generated PDF report or error message.
        """
        ...
        
# ================================================================
# Pydantic Schema for Input Validation
# ================================================================
class ReportData(BaseModel):
    """Schema for validating structured report input data."""
    summary: Dict[str, Any] = Field(..., description="Overall summary metrics of the analysis.")
    users: Dict[str, Any] = Field(..., description="Detailed data for each user analyzed.")

# Bind validation schema to tool
PDFReportTool = PDFWriterTool()
PDFReportTool.args_schema = ReportData

# ================================================================
# Standalone Test Execution
# ================================================================
if __name__ == '__main__':
    # Mock data to test PDF generation without full pipeline
    mock_data = {
        "summary": {
            "successful_scrapes": 5,
            "total_tweets_collected": 500,
            "success_rate": 0.95,
            "average_tweets_per_user": 100
        },
        "users": {
            "tech_guru_a": {
                "scrape_success": True,
                "tweet_count": 120,
                "user_info": {
                    "display_name": "Tech Guru A",
                    "followers_count": 15000,
                    "following_count": 500,
                    "bio": "Innovator, AI enthusiast, and future-of-tech evangelist."
                },
                "tweets": ["tweet1", "tweet2", "tweet3"]
            },
            "investor_b": {
                "scrape_success": True,
                "tweet_count": 80,
                "user_info": {
                    "display_name": "Investor B",
                    "followers_count": 25000,
                    "following_count": 750,
                    "bio": "Financial markets analyst and crypto investor."
                },
                "tweets": ["tweet_a", "tweet_b"]
            },
            "failed_scrape_c": {
                "scrape_success": False,
                "reason": "Account private"
            }
        }
    }
    
    print("Generating report...")
    result = PDFReportTool.run(data=mock_data)
    print(result)
