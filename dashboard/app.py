import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import streamlit as st
from streamlit_folium import st_folium
from dashboard.utils.data_fetcher import data_fetcher
from dashboard.utils.chart_builder import chart_builder
from dashboard.components.hotspot_map import build_nigeria_map

st.set_page_config(page_title="Nigeria Political Pulse", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")

if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Dashboard"

MENU_ITEMS = ["Dashboard", "Sentiment", "Topics", "Regions", "Trends", "Pipeline", "Settings", "Help"]

st.markdown("""
<style>
    body { font-family: 'Inter', 'Roboto', sans-serif; margin: 0; background-color: #F5F6FA; }
    .main .block-container {
        padding-top: 1.5rem !important; padding-bottom: 1rem !important;
        padding-left: 2rem !important; padding-right: 2rem !important;
        max-width: 1200px !important;
    }
    section[data-testid="stSidebar"] { background-color: #1E1E2F !important; padding: 12px 20px !important; min-width: 240px !important; }
    .sidebar-title { color: #FFFFFF; font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; padding: 0 16px; }
    section[data-testid="stSidebar"] .stButton button {
        background: transparent !important; color: rgba(255,255,255,0.7) !important;
        border: none !important; border-radius: 6px !important; font-weight: 400 !important;
        text-align: left !important; padding: 6px 16px !important; font-size: 0.85rem !important;
        width: 100% !important; margin-bottom: 2px !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,0.08) !important; color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .active-menu button { background: #007BFF !important; color: #FFFFFF !important; font-weight: 500 !important; }
    section[data-testid="stSidebar"] .active-menu button:hover { background: #007BFF !important; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .header h1 { font-size: 1.6rem; font-weight: 700; color: #1D1D1F; margin: 0; }
    .header span { font-size: 0.85rem; color: #86868B; }
    .metrics { display: flex; gap: 20px; margin-bottom: 20px; }
    .metric-card {
        background: #FFFFFF; border-radius: 10px; padding: 20px; flex: 1;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-card h3 { margin: 0; font-size: 14px; color: #555; font-weight: 500; }
    .metric-card .value { font-size: 24px; font-weight: 700; margin: 10px 0; color: #1D1D1F; }
    .positive { color: #28A745; font-size: 0.85rem; }
    .negative { color: #DC3545; font-size: 0.85rem; }
    .chart-section {
        background: #FFFFFF; border-radius: 10px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .chart-section h3 { font-size: 1rem; font-weight: 600; color: #1D1D1F; margin: 0 0 16px 0; }
    .status-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-bottom: 10px; }
    .status-badge.online { background: rgba(40,167,69,0.15); color: #28A745; }
    .status-badge.offline { background: rgba(220,53,69,0.15); color: #DC3545; }
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
    section[data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div { background: rgba(255,255,255,0.1) !important; border: none !important; border-radius: 6px !important; color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .stSlider label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
    section[data-testid="stSidebar"] div[data-testid="stThumbValue"] { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .stButton button:has(div.run-pipeline) { background: #007BFF !important; color: #FFFFFF !important; font-weight: 600 !important; }
    div[data-testid="column"] { padding: 0 0.75rem !important; }
    .element-container { margin-bottom: 0.75rem !important; }
    hr { margin: 20px 0 !important; opacity: 0.5; }
    div[data-testid="stExpander"] { background: #FFFFFF !important; border-radius: 10px !important; border: 1px solid #E5E5EA !important; margin-bottom: 0.5rem !important; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
    .stAlert { background: #F5F6FA !important; border: none !important; border-radius: 10px !important; color: #555 !important; }
    h2 { font-size: 1rem !important; font-weight: 600 !important; color: #1D1D1F !important; margin-top: 1.5rem !important; margin-bottom: 1rem !important; }
</style>
""", unsafe_allow_html=True)

def render_header():
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    page_icons = {"Dashboard": "📊", "Sentiment": "💭", "Topics": "🏷️", "Regions": "🗺️", "Trends": "📈", "Pipeline": "⚙️", "Settings": "🔧", "Help": "ℹ️"}
    icon = page_icons.get(st.session_state.active_menu, "📊")
    st.markdown(f"""
    <div class="header">
        <h1>{icon} {st.session_state.active_menu}</h1>
        <span>{today_str} | Nigeria Political Pulse</span>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🇳🇬 Nigeria Pulse</div>', unsafe_allow_html=True)

        for item in MENU_ITEMS:
            active_class = "active-menu" if item == st.session_state.active_menu else ""
            st.markdown(f'<div class="{active_class}">', unsafe_allow_html=True)
            if st.button(item, key=f"menu_{item}"):
                st.session_state.active_menu = item
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)

        api_healthy = data_fetcher.check_api_health()
        badge_class = "online" if api_healthy else "offline"
        badge_text = "● API Online" if api_healthy else "● API Offline"
        st.markdown(f'<div class="status-badge {badge_class}">{badge_text}</div>', unsafe_allow_html=True)

        topic_filter = st.selectbox("Filter by Topic", ["All Topics", "economy", "election", "security", "governance", "fuel_subsidy"])
        source_filter = st.selectbox("Filter by Source", ["All Sources", "X", "Nairaland", "NewsComment"])

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)

        max_posts = st.slider("Max Posts Per Source", min_value=10, max_value=100, value=50, step=10)
        if st.button("▶ Run Pipeline", use_container_width=True):
            with st.spinner("Running pipeline... This may take a few minutes"):
                result = data_fetcher.trigger_pipeline(max_posts=max_posts)
                if result.get("status") == "success":
                    st.success("Pipeline completed!")
                    st.rerun()
                else:
                    st.error(f"Pipeline failed: {result.get('message', 'Unknown error')}")

    return topic_filter, source_filter

def render_key_metrics(summary_data):
    total = summary_data.get("total_posts", 0)
    polarity = summary_data.get("polarity", {})
    emotions = summary_data.get("emotions", {})
    pos_pct = polarity.get("positive_percent", 0)
    neg_pct = polarity.get("negative_percent", 0)
    pos_count = polarity.get("Positive", 0)
    neg_count = polarity.get("Negative", 0)
    anger = emotions.get("Anger", 0)
    hope = emotions.get("Hope", 0)

    st.markdown(f"""
    <div class="metrics">
        <div class="metric-card">
            <h3>Total Posts</h3>
            <div class="value">{total}</div>
            <div class="positive">● Live</div>
        </div>
        <div class="metric-card">
            <h3>Positive</h3>
            <div class="value">{pos_pct}%</div>
            <div class="positive">+{pos_count} posts</div>
        </div>
        <div class="metric-card">
            <h3>Negative</h3>
            <div class="value">{neg_pct}%</div>
            <div class="negative">-{neg_count} posts</div>
        </div>
        <div class="metric-card">
            <h3>Anger / Hope</h3>
            <div class="value">{anger} / {hope}</div>
            <div>Emotional intensity</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_charts(summary_data, trends_data):
    polarity = summary_data.get("polarity", {})
    emotions = summary_data.get("emotions", {})
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-section"><h3>Sentiment Polarity</h3>', unsafe_allow_html=True)
        fig = chart_builder.build_polarity_donut(
            positive=polarity.get("Positive", 0),
            negative=polarity.get("Negative", 0),
            neutral=polarity.get("Neutral", 0),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-section"><h3>Emotional Tone</h3>', unsafe_allow_html=True)
        fig = chart_builder.build_emotion_bar(
            hope=emotions.get("Hope", 0), anger=emotions.get("Anger", 0),
            apathy=emotions.get("Apathy", 0), excitement=emotions.get("Excitement", 0),
            mixed=emotions.get("Mixed", 0),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-section"><h3>Sentiment Trends Over Time</h3>', unsafe_allow_html=True)
    trend_list = trends_data.get("data", [])
    fig = chart_builder.build_trend_line(trend_list)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_map(hotspot_data, height=500):
    st.markdown(f'<div class="chart-section"><h3>Nigeria Political Hotspot Map</h3>', unsafe_allow_html=True)
    if not hotspot_data:
        st.info("No geographic data available yet.")
    else:
        nigeria_map = build_nigeria_map(hotspot_data)
        st_folium(nigeria_map, width=None, height=height, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_topics_chart(topics_data):
    st.markdown('<div class="chart-section"><h3>Top Political Topics</h3>', unsafe_allow_html=True)
    if not topics_data:
        st.info("No topic data available yet.")
    else:
        fig = chart_builder.build_topic_bar(topics_data)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_source_chart():
    st.markdown('<div class="chart-section"><h3>Posts by Source</h3>', unsafe_allow_html=True)
    sources = {"X": {"total": 8, "positive": 2, "negative": 4, "neutral": 2},
               "Nairaland": {"total": 10, "positive": 3, "negative": 5, "neutral": 2},
               "NewsComment": {"total": 7, "positive": 2, "negative": 3, "neutral": 2}}
    fig = chart_builder.build_source_pie(sources)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_recent_posts(posts_data, limit=10):
    st.markdown('<div class="chart-section"><h3>Recent Posts</h3>', unsafe_allow_html=True)
    if not posts_data:
        st.info("No posts available yet.")
    else:
        for post in posts_data[:limit]:
            polarity = post.get("polarity", "Neutral")
            emotion = post.get("emotional_tone", "Mixed")
            label = f"[{post.get('source', 'Unknown')}] [{post.get('location', 'Unknown')}] - {post.get('topic', 'General')}"
            with st.expander(label):
                st.write(post.get("content", "")[:300])
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.caption(f"Polarity: **{polarity}**")
                with c2:
                    st.caption(f"Target: **{post.get('target_of_sentiment', 'General')}**")
                with c3:
                    st.caption(f"Confidence: **{post.get('confidence_score', 0):.0%}**")
                if post.get("sarcasm_detected"):
                    st.warning("⚠️ Sarcasm detected")
                if post.get("explanation"):
                    st.info(f"💡 {post.get('explanation')}")
    st.markdown('</div>', unsafe_allow_html=True)

def page_dashboard(summary_data, trends_data, hotspot_data, topics_data, recent_posts):
    has_data = summary_data.get("total_posts", 0) > 0
    if not has_data:
        st.warning("⚠️ No data available yet. Click **Run Pipeline** in the sidebar.")
    render_key_metrics(summary_data)
    render_charts(summary_data, trends_data)
    col1, col2 = st.columns([3, 2])
    with col1:
        render_map(hotspot_data)
    with col2:
        render_topics_chart(topics_data)
    render_recent_posts(recent_posts)

def page_sentiment(summary_data, trends_data, recent_posts):
    render_key_metrics(summary_data)
    col1, col2 = st.columns(2)
    with col1:
        polarity = summary_data.get("polarity", {})
        st.markdown('<div class="chart-section"><h3>Sentiment Polarity</h3>', unsafe_allow_html=True)
        fig = chart_builder.build_polarity_donut(
            positive=polarity.get("Positive", 0),
            negative=polarity.get("Negative", 0),
            neutral=polarity.get("Neutral", 0),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        render_source_chart()
    emotions = summary_data.get("emotions", {})
    st.markdown('<div class="chart-section"><h3>Emotional Tone Distribution</h3>', unsafe_allow_html=True)
    fig = chart_builder.build_emotion_bar(
        hope=emotions.get("Hope", 0), anger=emotions.get("Anger", 0),
        apathy=emotions.get("Apathy", 0), excitement=emotions.get("Excitement", 0),
        mixed=emotions.get("Mixed", 0),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    render_recent_posts(recent_posts, limit=15)

def page_topics(topics_data, recent_posts, topic_filter):
    render_topics_chart(topics_data)
    filtered = [p for p in recent_posts if topic_filter == "All Topics" or p.get("topic") == topic_filter]
    st.markdown(f'<div class="chart-section"><h3>Posts about {topic_filter if topic_filter != "All Topics" else "All Topics"}</h3>', unsafe_allow_html=True)
    if filtered:
        for post in filtered[:10]:
            with st.expander(f"[{post.get('source', 'Unknown')}] - {post.get('content', '')[:80]}..."):
                st.write(post.get("content", "")[:500])
                c1, c2 = st.columns(2)
                with c1:
                    st.caption(f"Polarity: **{post.get('polarity', 'Neutral')}**")
                with c2:
                    st.caption(f"Emotion: **{post.get('emotional_tone', 'Mixed')}**")
    else:
        st.info("No posts match this topic.")
    st.markdown('</div>', unsafe_allow_html=True)

def page_regions(hotspot_data, recent_posts):
    col1, col2 = st.columns([3, 2])
    with col1:
        render_map(hotspot_data, height=600)
    with col2:
        st.markdown('<div class="chart-section"><h3>Regional Breakdown</h3>', unsafe_allow_html=True)
        if hotspot_data:
            for loc in sorted(hotspot_data, key=lambda x: -x.get("mention_count", 0))[:8]:
                st.markdown(f"""
                <div style="padding:8px 0;border-bottom:1px solid #E5E5EA;">
                    <strong>{loc.get('location', 'Unknown')}</strong><br>
                    <span style="font-size:0.8rem;color:#86868B;">
                        {loc.get('mention_count', 0)} mentions · Sentiment: {loc.get('dominant_sentiment', 'Neutral')}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    region_posts = [p for p in recent_posts if p.get("location") != "Unknown"]
    render_recent_posts(region_posts, limit=8)

def page_trends(trends_data, summary_data):
    st.markdown('<div class="chart-section"><h3>Sentiment Trends (Last 24h)</h3>', unsafe_allow_html=True)
    trend_list = trends_data.get("data", [])
    fig = chart_builder.build_trend_line(trend_list)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-section"><h3>Trending Hashtags</h3>', unsafe_allow_html=True)
        hashtags = data_fetcher.get_trending_hashtags().get("data", [])
        if hashtags:
            for h in hashtags:
                st.markdown(f"**{h.get('hashtag', '')}** — {h.get('count', 0)} mentions")
        else:
            st.info("No hashtag data.")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-section"><h3>Source Distribution</h3>', unsafe_allow_html=True)
        sources = {"X": {"total": 8}, "Nairaland": {"total": 10}, "NewsComment": {"total": 7}}
        fig = chart_builder.build_source_pie(sources)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    if trend_list:
        st.markdown('<div class="chart-section"><h3>Trend Data Table</h3>', unsafe_allow_html=True)
        st.dataframe(trend_list[-12:], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

def page_pipeline():
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    st.markdown("### Pipeline Controls")
    st.info("Run the pipeline to collect and analyze political discourse from Nigerian sources.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Scout Agent** — Scrapes Twitter/X, Nairaland, and news comments")
    with col2:
        st.markdown("**Interpreter Agent** — Analyzes sentiment via Claude 3.5 with cultural context")
    with col3:
        st.markdown("**Aggregator Agent** — Synthesizes metrics for the dashboard")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-section"><h3>Agent Status</h3>', unsafe_allow_html=True)
    st.markdown("""
    | Agent | Status | Last Run |
    |-------|--------|----------|
    | Orchestrator | ✅ Ready | N/A |
    | Scout Agent | ✅ Ready | N/A |
    | Interpreter Agent | ✅ Ready | N/A |
    | Aggregator Agent | ✅ Ready | N/A |
    """)
    st.markdown('</div>', unsafe_allow_html=True)

def page_settings():
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    st.markdown("### About")
    st.markdown("**Nigeria Political Pulse** — Real-time sentiment analysis of Nigerian political discourse.")
    st.markdown("")
    st.markdown("**Built with:** Python, FastAPI, Streamlit, MongoDB, Claude 3.5 Sonnet, Plotly, Folium")
    st.markdown("")
    st.markdown("**Features:**")
    st.markdown("- Cultural intelligence for Nigerian Pidgin, Yoruba, Igbo, Hausa")
    st.markdown("- Sarcasm detection for Nigerian political discourse")
    st.markdown("- Geographic hotspot mapping across 30+ Nigerian cities")
    st.markdown("- Multi-agent AI system (Scout → Interpreter → Aggregator)")
    st.markdown('</div>', unsafe_allow_html=True)
    api_ok = data_fetcher.check_api_health()
    st.markdown('<div class="chart-section"><h3>System Status</h3>', unsafe_allow_html=True)
    st.markdown(f"**API Backend:** {'✅ Online' if api_ok else '❌ Offline'}")
    st.markdown(f"**Data Source:** {'API + Mock Fallback' if api_ok else 'Mock Data Only'}")
    st.markdown(f"**Version:** 1.0.0")
    st.markdown('</div>', unsafe_allow_html=True)

def page_help():
    st.markdown('<div class="chart-section">', unsafe_allow_html=True)
    st.markdown("### How to Use")
    st.markdown("1. **Select a menu item** on the left to navigate between views")
    st.markdown("2. **Filter** by topic or source in the sidebar")
    st.markdown("3. Click **Run Pipeline** to collect and analyze real data")
    st.markdown("")
    st.markdown("### Views")
    st.markdown("| Page | Description |")
    st.markdown("|------|-------------|")
    st.markdown("| **Dashboard** | Overview with key metrics, charts, map, and recent posts |")
    st.markdown("| **Sentiment** | Deep dive into sentiment polarity and emotional tone |")
    st.markdown("| **Topics** | Topic analysis with filtered post view |")
    st.markdown("| **Regions** | Geographic map and regional breakdown |")
    st.markdown("| **Trends** | Sentiment trends over time and hashtag tracking |")
    st.markdown("| **Pipeline** | Pipeline controls and agent status |")
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    render_header()
    topic_filter, source_filter = render_sidebar()

    topic_param = None if topic_filter == "All Topics" else topic_filter
    source_param = None if source_filter == "All Sources" else source_filter

    with st.spinner("Loading data..."):
        summary_data = data_fetcher.get_sentiment_summary(topic=topic_param)
        trends_data = data_fetcher.get_trends(hours=24)
        hotspots_response = data_fetcher.get_regional_hotspots()
        topics_response = data_fetcher.get_topics()
        recent_response = data_fetcher.get_recent_posts(limit=50, source=source_param)

    hotspot_data = hotspots_response.get("data", [])
    topics_data = topics_response.get("data", [])
    recent_posts = recent_response.get("data", [])

    page = st.session_state.active_menu
    if page == "Dashboard":
        page_dashboard(summary_data, trends_data, hotspot_data, topics_data, recent_posts)
    elif page == "Sentiment":
        page_sentiment(summary_data, trends_data, recent_posts)
    elif page == "Topics":
        page_topics(topics_data, recent_posts, topic_filter)
    elif page == "Regions":
        page_regions(hotspot_data, recent_posts)
    elif page == "Trends":
        page_trends(trends_data, summary_data)
    elif page == "Pipeline":
        page_pipeline()
    elif page == "Settings":
        page_settings()
    elif page == "Help":
        page_help()

    st.markdown("---")
    st.caption("🇳🇬 Nigeria Political Pulse | Powered by Claude 3.5 Sonnet | Real-time Nigerian Political Intelligence")

if __name__ == "__main__":
    main()
