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
    st.session_state.active_menu = "Report"

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
    .menu-item {
        padding: 6px 16px; border-radius: 6px; cursor: pointer; margin-bottom: 2px;
        color: rgba(255,255,255,0.7); font-size: 0.85rem;
    }
    .menu-item:hover { background-color: rgba(255,255,255,0.08); color: #FFFFFF; }
    .menu-item.active { background-color: #007BFF; color: #FFFFFF; font-weight: 500; }

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

    .upgrade-card {
        background: #007BFF; color: #FFFFFF; border-radius: 10px; padding: 20px; text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .upgrade-card h3 { color: #FFFFFF !important; font-size: 1.1rem; font-weight: 600; margin: 0 0 8px 0; }
    .upgrade-card p { color: rgba(255,255,255,0.85); font-size: 0.85rem; margin: 0 0 12px 0; }

    .status-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-bottom: 10px; }
    .status-badge.online { background: rgba(40,167,69,0.15); color: #28A745; }
    .status-badge.offline { background: rgba(220,53,69,0.15); color: #DC3545; }

    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
    section[data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div { background: rgba(255,255,255,0.1) !important; border: none !important; border-radius: 6px !important; color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .stSlider label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
    section[data-testid="stSidebar"] div[data-testid="stThumbValue"] { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .stButton button { background: #007BFF !important; color: #FFFFFF !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; }

    div[data-testid="column"] { padding: 0 0.75rem !important; }
    .element-container { margin-bottom: 0.75rem !important; }
    hr { margin: 20px 0 !important; opacity: 0.5; }
    div[data-testid="stExpander"] { background: #FFFFFF !important; border-radius: 10px !important; border: 1px solid #E5E5EA !important; margin-bottom: 0.5rem !important; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
    footer { color: #86868B !important; font-size: 0.85rem !important; text-align: center; padding: 2rem 0 !important; border-top: 1px solid #E5E5EA; }
    .stAlert { background: #F5F6FA !important; border: none !important; border-radius: 10px !important; color: #555 !important; }
    h2 { font-size: 1rem !important; font-weight: 600 !important; color: #1D1D1F !important; margin-top: 1.5rem !important; margin-bottom: 1rem !important; }
    .st-emotion-cache-1egp0jz p { font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

def render_header():
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    st.markdown(f"""
    <div class="header">
        <h1>Nigeria Political Pulse</h1>
        <span>{today_str} | Real-time Political Intelligence</span>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Nigeria Pulse</div>', unsafe_allow_html=True)
        for item in MENU_ITEMS:
            active_class = "active" if item == st.session_state.active_menu else ""
            st.markdown(f'<div class="menu-item {active_class}">{item}</div>', unsafe_allow_html=True)

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)

        api_healthy = data_fetcher.check_api_health()
        badge_class = "online" if api_healthy else "offline"
        badge_text = "● Online" if api_healthy else "● Offline"
        st.markdown(f'<div class="status-badge {badge_class}">{badge_text}</div>', unsafe_allow_html=True)

        topic_filter = st.selectbox("Filter by Topic", ["All Topics", "economy", "election", "security", "governance", "fuel_subsidy"])
        source_filter = st.selectbox("Filter by Source", ["All Sources", "X", "Nairaland", "NewsComment"])

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)

        max_posts = st.slider("Max Posts Per Source", min_value=10, max_value=100, value=50, step=10)
        if st.button("Run Pipeline", use_container_width=True):
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
        st.markdown('<div class="chart-section"><h3>Emotional Tone Distribution</h3>', unsafe_allow_html=True)
        fig = chart_builder.build_emotion_bar(
            hope=emotions.get("Hope", 0),
            anger=emotions.get("Anger", 0),
            apathy=emotions.get("Apathy", 0),
            excitement=emotions.get("Excitement", 0),
            mixed=emotions.get("Mixed", 0),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-section"><h3>Sentiment Trends Over Time</h3>', unsafe_allow_html=True)
    trend_list = trends_data.get("data", [])
    fig = chart_builder.build_trend_line(trend_list)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_map(hotspot_data):
    st.markdown('<div class="chart-section"><h3>Nigeria Political Hotspot Map</h3>', unsafe_allow_html=True)
    if not hotspot_data:
        st.info("No geographic data available yet. Run the pipeline to collect data.")
    else:
        nigeria_map = build_nigeria_map(hotspot_data)
        st_folium(nigeria_map, width=None, height=500, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_topics(topics_data):
    st.markdown('<div class="chart-section"><h3>Top Political Topics</h3>', unsafe_allow_html=True)
    if not topics_data:
        st.info("No topic data available yet.")
    else:
        fig = chart_builder.build_topic_bar(topics_data)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_recent_posts(posts_data):
    st.markdown('<div class="chart-section"><h3>Recent Posts</h3>', unsafe_allow_html=True)
    if not posts_data:
        st.info("No posts available yet. Run the pipeline to collect data.")
    else:
        for post in posts_data[:10]:
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

def main():
    render_header()
    topic_filter, source_filter = render_sidebar()

    topic_param = None if topic_filter == "All Topics" else topic_filter
    source_param = None if source_filter == "All Sources" else source_filter

    with st.spinner("Loading dashboard data..."):
        summary_data = data_fetcher.get_sentiment_summary(topic=topic_param)
        trends_data = data_fetcher.get_trends(hours=24)
        hotspots_response = data_fetcher.get_regional_hotspots()
        topics_response = data_fetcher.get_topics()
        recent_response = data_fetcher.get_recent_posts(limit=50, source=source_param)

    hotspot_data = hotspots_response.get("data", [])
    topics_data = topics_response.get("data", [])
    recent_posts = recent_response.get("data", [])

    has_data = summary_data.get("total_posts", 0) > 0
    if not has_data:
        st.warning("⚠️ No data available yet. Click **Run Pipeline** in the sidebar to start collecting data.")

    render_key_metrics(summary_data)
    render_charts(summary_data, trends_data)

    col1, col2 = st.columns([3, 2])
    with col1:
        render_map(hotspot_data)
    with col2:
        render_topics(topics_data)

    render_recent_posts(recent_posts)

    st.markdown("---")
    st.caption("🇳🇬 Nigeria Political Pulse | Powered by Claude 3.5 Sonnet | Real-time Nigerian Political Intelligence")

if __name__ == "__main__":
    main()
