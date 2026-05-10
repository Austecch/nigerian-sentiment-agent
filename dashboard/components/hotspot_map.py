# dashboard/components/hotspot_map.py
import folium
from folium import plugins


def build_nigeria_map(hotspot_data: list) -> folium.Map:
    """
    Build interactive Nigeria hotspot map
    showing where political conversations are active
    """

    # Center map on Nigeria
    nigeria_map = folium.Map(
        location=[9.0820, 8.6753],
        zoom_start=6,
        tiles="CartoDB positron"
    )

    # Apple-style color mapping for sentiment
    sentiment_colors = {
        "Positive": "#34C759",
        "Negative": "#FF3B30",
        "Neutral": "#8E8E93",
    }

    # Add markers for each hotspot
    for hotspot in hotspot_data:
        lat = hotspot.get("latitude")
        lon = hotspot.get("longitude")

        if not lat or not lon:
            continue

        location = hotspot.get("location", "Unknown")
        mention_count = hotspot.get("mention_count", 0)
        sentiment = hotspot.get(
            "dominant_sentiment", "Neutral"
        )
        emotion = hotspot.get("dominant_emotion", "Mixed")
        positive_pct = hotspot.get("positive_percent", 0)
        negative_pct = hotspot.get("negative_percent", 0)

        # Circle size based on mention count (smaller for minimalism)
        radius = min(max(mention_count * 1.5, 6), 20)
        color = sentiment_colors.get(sentiment, "#8E8E93")

        # Build popup content
        popup_html = f"""
        
            
                📍 {location}
            
            
            Mentions: {mention_count}
            Sentiment:
            
                {sentiment}
            
            Emotion: {emotion}
            Positive: {positive_pct}%
            Negative: {negative_pct}%
        
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(
                popup_html,
                max_width=250
            ),
            tooltip=f"{location}: {mention_count} mentions",
        ).add_to(nigeria_map)

    # Remove custom legend - will use Streamlit native components in app.py
    return nigeria_map