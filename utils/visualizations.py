"""
Visualizations for Emotional Journal MVP
Creates interactive charts using Plotly and word clouds
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from typing import Dict, List
import io
import base64
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Color scheme
COLORS = {
    'positive': '#4CAF50',  # Green
    'neutral': '#FFC107',   # Yellow
    'negative': '#F44336',  # Red
    'primary': '#6C63FF',   # Soft purple
    'background': '#F5F7FA',  # Light gray
    'text': '#2C3E50'       # Dark blue-gray
}


def create_mood_trend_chart(df: pd.DataFrame, days: int = None) -> go.Figure:
    """
    Create mood trend line chart

    Args:
        df: DataFrame with journal entries
        days: Number of days to show (None for all)

    Returns:
        Plotly Figure object
    """
    if df.empty:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available yet. Start journaling to see your mood trends!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=COLORS['text'])
        )
        fig.update_layout(
            title="Mood Trend Over Time",
            height=400,
            plot_bgcolor='white'
        )
        return fig

    # Filter by days if specified
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        df = df[df['timestamp'] >= cutoff_date]

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No entries in the last {days} days",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=COLORS['text'])
        )
        fig.update_layout(title="Mood Trend Over Time", height=400)
        return fig

    # Sort by timestamp
    df = df.sort_values('timestamp')

    # Create color gradient based on sentiment
    colors = df['ai_sentiment_score'].apply(lambda x:
        COLORS['positive'] if x > 0.3 else
        COLORS['negative'] if x < -0.3 else
        COLORS['neutral']
    )

    # Create hover text
    df['hover_text'] = df.apply(lambda row:
        f"Date: {row['timestamp'].strftime('%Y-%m-%d %H:%M')}<br>" +
        f"Mood Score: {row['ai_sentiment_score']:.2f}<br>" +
        f"Sentiment: {row['ai_sentiment_label']}<br>" +
        f"Preview: {row['entry_text'][:100]}...",
        axis=1
    )

    # Create figure
    fig = go.Figure()

    # Add line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['ai_sentiment_score'],
        mode='lines+markers',
        name='Mood Score',
        line=dict(color=COLORS['primary'], width=2),
        marker=dict(
            size=10,
            color=colors,
            line=dict(width=2, color='white')
        ),
        hovertext=df['hover_text'],
        hoverinfo='text'
    ))

    # Add horizontal lines for reference
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=0.3, line_dash="dot", line_color=COLORS['positive'], opacity=0.3)
    fig.add_hline(y=-0.3, line_dash="dot", line_color=COLORS['negative'], opacity=0.3)

    # Update layout
    fig.update_layout(
        title="Mood Trend Over Time",
        xaxis_title="Date",
        yaxis_title="Mood Score",
        height=400,
        hovermode='closest',
        plot_bgcolor='white',
        yaxis=dict(range=[-1.1, 1.1], gridcolor='lightgray'),
        xaxis=dict(gridcolor='lightgray'),
        font=dict(color=COLORS['text'])
    )

    return fig


def create_emotion_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create emotion distribution pie chart

    Args:
        df: DataFrame with journal entries

    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No emotion data available yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=COLORS['text'])
        )
        fig.update_layout(title="Emotion Distribution", height=400)
        return fig

    # Collect all emotions
    all_emotions = []
    for emotions in df['detected_emotions']:
        if emotions:
            all_emotions.extend(emotions)

    if not all_emotions:
        fig = go.Figure()
        fig.add_annotation(
            text="No emotions detected yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=COLORS['text'])
        )
        fig.update_layout(title="Emotion Distribution", height=400)
        return fig

    # Count emotions
    emotion_counts = Counter(all_emotions)
    top_emotions = dict(emotion_counts.most_common(5))

    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(top_emotions.keys()),
        values=list(top_emotions.values()),
        hole=0.3,
        marker=dict(colors=px.colors.qualitative.Pastel),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title="Top 5 Emotions",
        height=400,
        font=dict(color=COLORS['text'])
    )

    return fig


def create_word_cloud(df: pd.DataFrame) -> str:
    """
    Create word cloud from journal entries

    Args:
        df: DataFrame with journal entries

    Returns:
        Base64 encoded image string for display in Streamlit
    """
    if df.empty:
        return None

    # Combine all entry texts
    all_text = ' '.join(df['entry_text'].tolist())

    if not all_text.strip():
        return None

    try:
        # Create word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=50,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(all_text)

        # Convert to image
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plt.close()

        # Encode to base64
        img_base64 = base64.b64encode(buf.read()).decode()
        return img_base64

    except Exception as e:
        logger.error(f"Word cloud generation failed: {e}")
        return None


def create_day_of_week_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart showing average mood by day of week

    Args:
        df: DataFrame with journal entries

    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=COLORS['text'])
        )
        fig.update_layout(title="Mood by Day of Week", height=400)
        return fig

    # Add day of week
    df['day_of_week'] = df['timestamp'].dt.day_name()

    # Calculate average mood by day
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    mood_by_day = df.groupby('day_of_week')['ai_sentiment_score'].mean().reindex(day_order)

    # Create bar chart
    colors_map = [COLORS['positive'] if x > 0.3 else COLORS['negative'] if x < -0.3
                  else COLORS['neutral'] for x in mood_by_day.values]

    fig = go.Figure(data=[go.Bar(
        x=mood_by_day.index,
        y=mood_by_day.values,
        marker_color=colors_map,
        text=[f"{val:.2f}" for val in mood_by_day.values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Average Mood: %{y:.2f}<extra></extra>'
    )])

    fig.update_layout(
        title="Average Mood by Day of Week",
        xaxis_title="Day",
        yaxis_title="Average Mood Score",
        height=400,
        yaxis=dict(range=[-1.1, 1.1], gridcolor='lightgray'),
        plot_bgcolor='white',
        font=dict(color=COLORS['text'])
    )

    return fig


def create_sentiment_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart showing distribution of sentiment labels

    Args:
        df: DataFrame with journal entries

    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=COLORS['text'])
        )
        fig.update_layout(title="Sentiment Distribution", height=400)
        return fig

    # Count sentiment labels
    sentiment_counts = df['ai_sentiment_label'].value_counts()

    # Define colors
    color_map = {
        'POSITIVE': COLORS['positive'],
        'NEGATIVE': COLORS['negative'],
        'NEUTRAL': COLORS['neutral']
    }

    colors_list = [color_map.get(label, COLORS['primary']) for label in sentiment_counts.index]

    fig = go.Figure(data=[go.Bar(
        x=sentiment_counts.index,
        y=sentiment_counts.values,
        marker_color=colors_list,
        text=sentiment_counts.values,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title="Sentiment Distribution",
        xaxis_title="Sentiment",
        yaxis_title="Number of Entries",
        height=400,
        plot_bgcolor='white',
        font=dict(color=COLORS['text'])
    )

    return fig


def get_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate summary statistics for dashboard

    Args:
        df: DataFrame with journal entries

    Returns:
        Dictionary with statistics
    """
    if df.empty:
        return {
            'total_entries': 0,
            'current_streak': 0,
            'avg_mood_7d': 0,
            'top_emotion': 'None'
        }

    # Total entries
    total_entries = len(df)

    # Current streak
    current_streak = calculate_current_streak(df)

    # Average mood (last 7 days)
    now = datetime.now()
    df_7d = df[df['timestamp'] >= now - timedelta(days=7)]
    avg_mood_7d = df_7d['ai_sentiment_score'].mean() if not df_7d.empty else 0

    # Top emotion
    all_emotions = []
    for emotions in df['detected_emotions']:
        if emotions:
            all_emotions.extend(emotions)

    top_emotion = Counter(all_emotions).most_common(1)[0][0] if all_emotions else 'None'

    return {
        'total_entries': total_entries,
        'current_streak': current_streak,
        'avg_mood_7d': avg_mood_7d,
        'top_emotion': top_emotion
    }


def calculate_current_streak(df: pd.DataFrame) -> int:
    """
    Calculate current journaling streak

    Args:
        df: DataFrame with journal entries

    Returns:
        Current streak in days
    """
    if df.empty:
        return 0

    # Get unique dates
    dates = sorted(df['timestamp'].dt.date.unique(), reverse=True)

    if not dates:
        return 0

    # Check if there's an entry today or yesterday
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    if dates[0] != today and dates[0] != yesterday:
        return 0

    # Count consecutive days
    streak = 1
    for i in range(len(dates) - 1):
        if (dates[i] - dates[i + 1]).days == 1:
            streak += 1
        else:
            break

    return streak


def create_calendar_heatmap(df: pd.DataFrame, year: int = None, month: int = None) -> go.Figure:
    """
    Create calendar heatmap showing journaling activity

    Args:
        df: DataFrame with journal entries
        year: Year to display (default: current year)
        month: Month to display (None for full year)

    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="Activity Calendar", height=400)
        return fig

    # Use current year if not specified
    if year is None:
        year = datetime.now().year

    # Group by date and count entries
    df['date'] = df['timestamp'].dt.date
    daily_counts = df.groupby('date').size().reset_index(name='count')

    # Create hover text
    daily_counts['hover_text'] = daily_counts.apply(
        lambda row: f"{row['date']}<br>Entries: {row['count']}", axis=1
    )

    # Create scatter plot (simplified calendar view)
    fig = go.Figure(data=[go.Scatter(
        x=pd.to_datetime(daily_counts['date']),
        y=[1] * len(daily_counts),
        mode='markers',
        marker=dict(
            size=daily_counts['count'] * 10,
            color=daily_counts['count'],
            colorscale='Greens',
            showscale=True,
            colorbar=dict(title="Entries")
        ),
        hovertext=daily_counts['hover_text'],
        hoverinfo='text'
    )])

    fig.update_layout(
        title=f"Journaling Activity - {year}",
        height=200,
        yaxis=dict(visible=False),
        xaxis=dict(title="Date"),
        plot_bgcolor='white'
    )

    return fig
