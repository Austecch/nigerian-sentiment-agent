# 🇳🇬 Nigeria Political Sentiment Agent

Real-time sentiment analysis of Nigerian political discourse using AI agents, Claude 3.5, and interactive data visualization.

## 📋 Project Overview

This project is a **multi-agent AI system** that monitors, analyzes, and visualizes sentiment in Nigerian political discussions across social media and news platforms. It combines web scraping, cultural intelligence, and LLM analysis to decode the complex landscape of Nigerian political discourse.

### What It Does

1. **Scrapes** political content from:
   - Twitter/X (using Apify)
   - Nairaland forum
   - Nigerian news sites (Punch, Vanguard, ThisDay, Premium Times)

2. **Filters & Cleans**:
   - Bot detection
   - Deduplication
   - Campaign message identification
   - Geographic location detection

3. **Analyzes with Cultural Intelligence**:
   - Sentiment analysis using Claude 3.5 Sonnet
   - Nigerian Pidgin, Yoruba, Igbo, Hausa language detection
   - Sarcasm detection (very common in Nigerian discourse)
   - Cultural lexicon with 100+ Nigerian political terms

4. **Visualizes** through:
   - Interactive Streamlit dashboard
   - Sentiment trends over time
   - Geographic hotspot mapping
   - Topic analysis
   - Real-time metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                    │
│         (Coordinates all agents sequentially)          │
└──────────┬──────────┬──────────┬───────────────┘
           │          │          │
           ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ SCOUT  │ │INTERP. │ │AGGREG. │
    │ AGENT  │ │ AGENT  │ │ AGENT  │
    └────────┘ └────────┘ └────────┘
         │              │
         ▼              ▼
    ┌────────┐    ┌────────┐
    │ Scrapers│    │ Claude  │
    │ Twitter  │    │ 3.5     │
    │ Nairaland│    │ Cultural│
    │ News    │    │ Lexicon │
    └────────┘    └────────┘
         │              │
         └──────┬───────┘
                ▼
         ┌────────────────┐
         │    MongoDB    │
         │  (Raw &      │
         │ Interpreted) │
         └────────────────┘
                │
                ▼
         ┌────────────────┐
         │  FastAPI     │
         │  (REST API)  │
         └────────┬───────┘
                   │
                   ▼
         ┌────────────────┐
         │  Streamlit   │
         │  Dashboard  │
         └────────────────┘
```

## ✅ What Has Been Done

### Core Infrastructure
- ✅ **Multi-Agent System** - Scout, Interpreter, Aggregator agents
- ✅ **FastAPI Backend** - RESTful API with endpoints for sentiment, topics, regions, trends
- ✅ **Streamlit Dashboard** - Interactive web interface
- ✅ **MongoDB Integration** - Data persistence for raw and interpreted posts

### Data Collection
- ✅ **Twitter/X Scraper** - Using Apify Twitter scraper
- ✅ **Nairaland Scraper** - Political discussions from Nigeria's largest forum
- ✅ **News Scraper** - Comments from major Nigerian news sites
- ✅ **Geo Filter** - Detects 30+ Nigerian cities/states in posts

### Intelligence Layer
- ✅ **Cultural Lexicon** - 100+ Nigerian political terms with meanings
- ✅ **Sarcasm Detector** - Rule-based + lexicon approach
- ✅ **Language Detector** - English, Pidgin, Yoruba, Igbo, Hausa
- ✅ **Claude 3.5 Integration** - For cultural interpretation of posts

### Filters & Processing
- ✅ **Bot Detector** - Identifies automated/coordinated posts
- ✅ **Deduplication** - Removes exact and near-duplicate posts
- ✅ **Campaign Filter** - Flags political campaign messaging
- ✅ **Rate Limiting** - API protection with SlowAPI

### Dashboard & Visualization
- ✅ **Apple-Style UI** - Modern minimalist design with system fonts
- ✅ **Sentiment Charts** - Polarity donut, emotion bar, trend lines
- ✅ **Geographic Map** - Interactive Folium map with Nigerian hotspots
- ✅ **Topic Analysis** - Bar charts of political topics
- ✅ **Recent Posts** - Expandable post list with sentiment/emotion/sarcasm
- ✅ **Real-time Metrics** - Total posts, positive/negative %, anger/hope counts
- ✅ **Colored Cards** - Gradient backgrounds with hover effects
- ✅ **Hero Header** - Green gradient section with project title

## 🚧 What's Left to Do

### High Priority
- ❌ **Fix Typos in `mongodb_client.py`** - `inserted_id` typos (lines 55, 67, 81)
- ❌ **Fix `cultural_lexicon.py:24`** - Missing `as f` in file open
- ❌ **Populate `lexicon_data.json`** - Add actual Nigerian political terms
- ❌ **Implement `pinecone_client.py`** - Vector search (currently empty)
- ❌ **Implement `queries.py`** - Database query helpers (currently empty)

### Medium Priority
- ❌ **Add Tests** - Complete `test_api.py`, `test_agents.py`, etc.
- ❌ **Fix Deployment Configs** - Railway, Docker Compose, Dockerfile need testing
- ❌ **Add Authentication** - API key auth exists but needs JWT implementation
- ❌ **Error Handling** - Improve error messages and user feedback

### Low Priority
- ❌ **Add More News Sources** - Guardian Nigeria, Daily Trust, etc.
- ❌ **Sentiment Over Time** - More granular time buckets
- ❌ **Export Functionality** - PDF/CSV export of analysis
- ❌ **User Accounts** - Multi-user support with saved searches
- ❌ **Mobile Optimization** - Responsive design improvements

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB instance
- Apify API key
- Anthropic API key

### Installation

```bash
# Clone the repository
cd C:\Users\HP\Desktop\nigerian-sentiment-agent

# Create .env file with your API keys
# ANTHROPIC_API_KEY=your_key
# APIFY_API_KEY=your_key
# MONGODB_CONNECTION_STRING=your_connection_string
# PINECONE_API_KEY=your_key

# Install dependencies
pip install -r requirements.txt

# Start MongoDB (if not running)
# MongoDB should be running on localhost:27017

# Start FastAPI backend
.\venv\Scripts\python -m uvicorn api.main:app --reload --port 8000

# Start Streamlit dashboard (in new terminal)
.\venv\Scripts\streamlit run dashboard/app.py
```

### Access Points
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### Run Pipeline
1. Open the Streamlit dashboard
2. Click "Run Pipeline" in the sidebar
3. Wait for data collection and analysis (may take 2-5 minutes)
4. View results in the dashboard

## 📁 Project Structure

```
nigerian-sentiment-agent/
├── agents/                 # Multi-agent system
│   ├── orchestrator.py    # Master coordinator
│   ├── scout_agent.py     # Data collection
│   ├── interpreter_agent.py # Claude analysis
│   └── aggregator_agent.py  # Metrics synthesis
├── api/                   # FastAPI backend
│   ├── main.py            # API entry point
│   ├── routes/            # API endpoints
│   ├── schemas.py         # Pydantic models
│   └── middleware/         # Auth, rate limiting
├── dashboard/             # Streamlit frontend
│   ├── app.py             # Main dashboard
│   ├── components/         # UI components
│   └── utils/             # Chart builders, data fetchers
├── scrapers/              # Data collection
│   ├── twitter_scraper.py
│   ├── nairaland_scraper.py
│   └── news_scraper.py
├── filters/               # Data cleaning
│   ├── bot_detector.py
│   ├── deduplication.py
│   └── campaign_filter.py
├── intelligence/          # AI analysis
│   ├── cultural_lexicon.py
│   ├── sarcasm_detector.py
│   ├── language_detector.py
│   └── system_prompts.py
├── database/              # Data persistence
│   ├── mongodb_client.py
│   ├── models.py
│   ├── queries.py        # (empty - needs implementation)
│   └── pinecone_client.py # (empty - needs implementation)
├── tests/                 # Test suite
├── deployment/            # Docker, Railway configs
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Key Features

### Cultural Intelligence
- Understands Nigerian Pidgin: "Wahala", "Sapa", "Japa", "Emilokan"
- Detects code-mixing: English-Yoruba, English-Igbo, English-Hausa
- Recognizes political slogans: "Obidient", "Structure", "Stomach infrastructure"
- Identifies sarcasm: "E go better" (after listing failures)

### Sentiment Analysis
- **Polarity**: Positive, Negative, Neutral
- **Emotional Tone**: Hope, Anger, Apathy, Excitement, Mixed
- **Target**: Policy, Personality, Economy, Party, Governance, Security
- **Sarcasm Detection**: Critical for Nigerian political discourse

### Geographic Intelligence
- 30+ Nigerian cities/states recognized
- Hotspot mapping with Folium
- Regional sentiment breakdown
- Location-based filtering

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/pipeline/run` | POST | Trigger full pipeline |
| `/api/sentiment/recent` | GET | Recent sentiment posts |
| `/api/sentiment/summary` | GET | Aggregated sentiment |
| `/api/sentiment/by-source` | GET | Sentiment by source |
| `/api/topics/` | GET | All topics |
| `/api/topics/{topic}` | GET | Topic details |
| `/api/regions/hotspots` | GET | Geographic hotspots |
| `/api/regions/{location}` | GET | Location sentiment |
| `/api/trends/` | GET | Sentiment trends |
| `/api/trends/hashtags` | GET | Trending hashtags |

## 🤝 Contributing

This is a personal research project. Feel free to fork and adapt for your own sentiment analysis needs.

## 📄 License

MIT License - Feel free to use this project for research or commercial purposes.

## 📧 Contact

For questions or collaborations related to Nigerian political sentiment analysis, feel free to reach out!

---

**Built with**: Python, FastAPI, Streamlit, MongoDB, Claude 3.5 Sonnet, Plotly, Folium

**Inspired by**: The need to understand Nigerian political discourse beyond surface-level sentiment, considering the country's unique linguistic and cultural context.
