# dashboard/utils/chart_builder.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class ChartBuilder:
    """Builds all charts for the dashboard"""

    COLORS = {
        "positive": "#28A745",
        "negative": "#DC3545",
        "neutral": "#8E8E93",
        "hope": "#007BFF",
        "anger": "#DC3545",
        "apathy": "#8E8E93",
        "excitement": "#FFC107",
        "mixed": "#6C757D",
        "primary": "#007BFF",
        "secondary": "#F5F6FA",
    }

    def build_polarity_donut(
        self,
        positive: int,
        negative: int,
        neutral: int
    ) -> go.Figure:
        """Build polarity distribution donut chart with modern styling"""
        labels = ["Positive", "Negative", "Neutral"]
        values = [positive, negative, neutral]
        colors = [
            self.COLORS["positive"],
            self.COLORS["negative"],
            self.COLORS["neutral"],
        ]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker_colors=colors,
            textinfo="label+percent",
            textfont_size=14,
            textfont_family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
            textfont_color="#1D1D1F",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
            marker=dict(
                line=dict(color="white", width=3)
            )
        )])

        fig.update_layout(
            title={
                "text": "Sentiment Polarity",
                "x": 0.5,
                "font": {"size": 20, "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif", "color": "#1D1D1F"}
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font={"size": 12, "color": "#86868B"}
            ),
            height=380,
            margin=dict(t=80, b=60, l=20, r=20),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font={"family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif"},
        )
        return fig

    def build_emotion_bar(
        self,
        hope: int,
        anger: int,
        apathy: int,
        excitement: int,
        mixed: int
    ) -> go.Figure:
        """Build emotional tone bar chart with modern styling"""
        emotions = ["Hope", "Anger", "Apathy", "Excitement", "Mixed"]
        values = [hope, anger, apathy, excitement, mixed]
        colors = [
            self.COLORS["hope"],
            self.COLORS["anger"],
            self.COLORS["apathy"],
            self.COLORS["excitement"],
            self.COLORS["mixed"],
        ]

        fig = go.Figure(data=[go.Bar(
            x=emotions,
            y=values,
            marker_color=colors,
            marker_line=dict(color="white", width=2),
            text=values,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        )])

        fig.update_layout(
            title={
                "text": "Emotional Tone Distribution",
                "x": 0.5,
                "font": {"size": 20, "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif", "color": "#1D1D1F"}
            },
            xaxis_title="Emotion",
            yaxis_title="Post Count",
            height=380,
            margin=dict(t=80, b=40, l=40, r=20),
            paper_bgcolor="white",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            font={"family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif"},
            xaxis={
                "gridcolor": "rgba(0,0,0,0)",
                "tickfont": {"size": 13, "color": "#1D1D1F"},
                "title": {"font": {"size": 14, "color": "#86868B"}}
            },
            yaxis={
                "gridcolor": "#E5E5EA",
                "gridwidth": 1,
                "tickfont": {"size": 12, "color": "#86868B"},
                "title": {"font": {"size": 14, "color": "#86868B"}}
            },
        )
        fig.update_traces(textfont_size=14, textfont_color="#1D1D1F")
        return fig

    def build_trend_line(
        self,
        trend_data: list
    ) -> go.Figure:
        """Build sentiment trend line chart with modern styling"""
        if not trend_data:
            fig = go.Figure()
            fig.update_layout(
                title={
                    "text": "Sentiment Trends Over Time",
                    "x": 0.5,
                    "font": {"size": 20, "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif", "color": "#1D1D1F"}
                },
                paper_bgcolor="white",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400,
            )
            fig.add_annotation(
                text="No trend data available yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font={"size": 14, "color": "#86868B"}
            )
            return fig

        timestamps = [d["timestamp"] for d in trend_data]
        positive = [d.get("positive", 0) for d in trend_data]
        negative = [d.get("negative", 0) for d in trend_data]
        neutral = [d.get("neutral", 0) for d in trend_data]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=positive,
            name="Positive",
            line=dict(
                color=self.COLORS["positive"],
                width=3
            ),
            fill="tozeroy",
            fillcolor="rgba(52,199,89,0.15)",
            hovertemplate="<b>Positive</b><br>Time: %{x}<br>Count: %{y}<extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=negative,
            name="Negative",
            line=dict(
                color=self.COLORS["negative"],
                width=3
            ),
            fill="tozeroy",
            fillcolor="rgba(255,59,48,0.15)",
            hovertemplate="<b>Negative</b><br>Time: %{x}<br>Count: %{y}<extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=neutral,
            name="Neutral",
            line=dict(
                color=self.COLORS["neutral"],
                width=3,
                dash="dot"
            ),
            hovertemplate="<b>Neutral</b><br>Time: %{x}<br>Count: %{y}<extra></extra>",
        ))

        fig.update_layout(
            title={
                "text": "Sentiment Trends Over Time",
                "x": 0.5,
                "font": {"size": 20, "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif", "color": "#1D1D1F"}
            },
            xaxis_title="Time",
            yaxis_title="Post Count",
            height=420,
            hovermode="x unified",
            paper_bgcolor="white",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif"},
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font={"size": 12, "color": "#86868B"},
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#E5E5EA",
                borderwidth=1,
            ),
            xaxis={
                "gridcolor": "#E5E5EA",
                "gridwidth": 1,
                "tickfont": {"size": 12, "color": "#86868B"},
                "title": {"font": {"size": 14, "color": "#86868B"}},
                "linecolor": "#E5E5EA",
                "linewidth": 1,
            },
            yaxis={
                "gridcolor": "#E5E5EA",
                "gridwidth": 1,
                "tickfont": {"size": 12, "color": "#86868B"},
                "title": {"font": {"size": 14, "color": "#86868B"}},
                "linecolor": "#E5E5EA",
                "linewidth": 1,
            },
        )
        return fig

    def build_topic_bar(
        self,
        topics_data: list
    ) -> go.Figure:
        """Build topic distribution bar chart with modern styling"""
        if not topics_data:
            fig = go.Figure()
            fig.update_layout(
                title={
                    "text": "Top Political Topics",
                    "x": 0.5,
                    "font": {"size": 20, "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif", "color": "#1D1D1F"}
                },
                paper_bgcolor="white",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400,
            )
            fig.add_annotation(
                text="No topic data available yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font={"size": 14, "color": "#86868B"}
            )
            return fig

        topics = [t["topic"] for t in topics_data[:8]]
        counts = [t["mention_count"] for t in topics_data[:8]]

        fig = go.Figure(data=[go.Bar(
            y=topics,
            x=counts,
            orientation="h",
            marker_color=self.COLORS["primary"],
            marker_line=dict(color="white", width=2),
            text=counts,
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Mentions: %{x}<extra></extra>",
        )])

        fig.update_layout(
            title={
                "text": "Top Political Topics",
                "x": 0.5,
                "font": {"size": 20, "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif", "color": "#1D1D1F"}
            },
            xaxis_title="Mention Count",
            height=420,
            margin=dict(t=80, b=40, l=140, r=40),
            paper_bgcolor="white",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif"},
            xaxis={
                "gridcolor": "#E5E5EA",
                "gridwidth": 1,
                "tickfont": {"size": 13, "color": "#86868B"},
                "title": {"font": {"size": 14, "color": "#86868B"}}
            },
            yaxis={
                "gridcolor": "rgba(0,0,0,0)",
                "tickfont": {"size": 13, "color": "#1D1D1F"},
            },
        )
        fig.update_traces(textfont_size=14, textfont_color="#1D1D1F")
        return fig

    def build_source_pie(
        self,
        source_data: dict
    ) -> go.Figure:
        """Build source distribution pie chart with modern styling"""
        if not source_data:
            fig = go.Figure()
            fig.update_layout(
                title={
                    "text": "Posts by Source",
                    "x": 0.5,
                    "font": {"size": 20, "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif", "color": "#1D1D1F"}
                },
                paper_bgcolor="white",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300,
            )
            fig.add_annotation(
                text="No source data available yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font={"size": 14, "color": "#86868B"}
            )
            return fig

        labels = list(source_data.keys())
        values = [v["total"] for v in source_data.values()]
        colors = ["#007BFF", "#28A745", "#FFC107"]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker_colors=colors,
            marker_line=dict(color="white", width=3),
            textinfo="label+percent",
            textfont_size=13,
            textfont_family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
            textfont_color="#1D1D1F",
            hovertemplate="<b>%{label}</b><br>Posts: %{value}<br>Percentage: %{percent}<extra></extra>",
        )])

        fig.update_layout(
            title={
                "text": "Posts by Source",
                "x": 0.5,
                "font": {"size": 20, "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif", "color": "#1D1D1F"}
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font={"size": 12, "color": "#86868B"},
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#E5E5EA",
                borderwidth=1,
            ),
            height=320,
            margin=dict(t=80, b=60, l=20, r=20),
            paper_bgcolor="white",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif"},
        )
        return fig


# Single instance
chart_builder = ChartBuilder()