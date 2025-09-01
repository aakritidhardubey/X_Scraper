# X_Scraper - Sentiment Analysis on X (Twitter)

[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CrewAI](https://img.shields.io/badge/CrewAI-Powered-orange.svg)](https://crewai.com/)

## 📖 Overview

X_Scraper is a powerful sentiment analysis tool built using **CrewAI**, **LiteLLM**, and **Python**. It scrapes posts from X (Twitter), analyzes them using state-of-the-art LLMs (Groq/OpenAI), and provides comprehensive insights into sentiment trends and public opinion.

## ⚙️ Features

- 🔍 **Smart Scraping**: Extract posts from X (Twitter) based on keywords, hashtags, or user handles
- 🤖 **AI-Powered Analysis**: Leverages advanced LLMs (Groq Llama / OpenAI GPT models) for accurate sentiment analysis
- 📊 **Sentiment Classification**: Categorizes content into **Positive**, **Negative**, or **Neutral** sentiments
- 🛠️ **Modular Architecture**: Clean, maintainable code structure with separated tools and workflows
- ⚡ **Fast Processing**: Optimized for high-throughput sentiment analysis
- 📈 **Detailed Insights**: Provides percentage breakdowns and trend analysis

## 🏗️ Project Structure

```
X_Scraper/
├── sentiment_x_analysis/
│   └── src/
│       └── sentiment_x_analysis/
│           ├── crew.py          # CrewAI workflow (agents, tasks, flows)
│           ├── main.py          # Entry point (runs Crew + model provider config)
│           ├── tools/           # Helper scripts and utilities
│           └── __init__.py      # Package initialization
├── .env                         # Environment variables (API keys & configs)
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- API keys for Groq and/or OpenAI

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aakritidhardubey/X_Scraper.git
   cd X_Scraper
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory and add your API keys:
   ```env
   # Model Configuration
   MODEL=groq/llama-3.1-8b-instant
   
   # API Keys
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   
   # OpenAI Model (optional)
   OPENAI_MODEL=gpt-3.5-turbo
   ```

### Running the Application

```bash
cd sentiment_x_analysis/src/sentiment_x_analysis
python main.py
```

## 📊 Sample Output

```
🔍 Analyzing sentiment for keyword: "AI"

📈 Sentiment Analysis Results:
┌─────────────────┬─────────┬───────────┐
│ Sentiment       │ Count   │ Percentage│
├─────────────────┼─────────┼───────────┤
│ 😊 Positive     │   65    │   65.0%   │
│ 😐 Neutral      │   20    │   20.0%   │
│ 😞 Negative     │   15    │   15.0%   │
└─────────────────┴─────────┴───────────┘

✨ Key Insights:
• Overwhelmingly positive sentiment towards AI discussions
• Most negative sentiment relates to job displacement concerns
• Neutral posts primarily focus on technical specifications
```

## 🛠️ Configuration

### Supported Models

- **Groq Models**: `groq/llama-3.1-8b-instant`, `groq/llama-3.3-70b-versatile`
- **OpenAI Models**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MODEL` | Primary model for sentiment analysis | ✅ |
| `GROQ_API_KEY` | Groq API key for Llama models | ⚠️ |
| `OPENAI_API_KEY` | OpenAI API key for GPT models | ⚠️ |
| `OPENAI_MODEL` | Specific OpenAI model to use | ❌ |

*Note: At least one API key (Groq or OpenAI) is required*

## 🧪 Usage Examples

```python
# Example: Analyze sentiment for multiple keywords
keywords = ["AI", "machine learning", "automation"]
for keyword in keywords:
    results = analyze_sentiment(keyword)
    print(f"Results for '{keyword}': {results}")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📋 Roadmap

- [ ] **Dashboard Integration**: Streamlit/Gradio web interface
- [ ] **Database Storage**: PostgreSQL/MongoDB integration for result persistence
- [ ] **Multi-language Support**: Sentiment analysis in multiple languages
- [ ] **Real-time Monitoring**: Live sentiment tracking and alerts
- [ ] **Advanced Analytics**: Trend analysis and predictive insights
- [ ] **Export Features**: CSV, JSON, and PDF report generation
- [ ] **Rate Limiting**: Intelligent API usage optimization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👩‍💻 Author

**Aakriti Dhar Dubey**
- GitHub: [@aakritidhardubey](https://github.com/aakritidhardubey)
- LinkedIn: [Connect with me](https://linkedin.com/in/aakritidhardubey)

## 🙏 Acknowledgments

- [CrewAI](https://crewai.com/) for the multi-agent framework
- [LiteLLM](https://litellm.ai/) for unified LLM API access
- [Groq](https://groq.com/) for lightning-fast inference
- [OpenAI](https://openai.com/) for powerful language models

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the [Issues](https://github.com/aakritidhardubey/X_Scraper/issues) page
2. Create a new issue with detailed information
3. Reach out via email or LinkedIn

---

⭐ **If you found this project helpful, please give it a star!** ⭐
