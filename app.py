"""
Emotional Journal MVP - Main Application
A local-only AI-powered emotional journaling platform
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add utils to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_manager import DataManager
from utils.sentiment_analyzer_lite import analyze_sentiment, get_mood_emoji, get_mood_color
from utils.visualizations import (
    create_mood_trend_chart,
    create_emotion_distribution_chart,
    create_word_cloud,
    create_day_of_week_chart,
    create_sentiment_distribution_chart,
    create_calendar_heatmap,
    get_summary_stats
)

# Page configuration
st.set_page_config(
    page_title="Emotional Journal",
    page_icon="📔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #6C63FF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2C3E50;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        background-color: #F5F7FA;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #6C63FF;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #4CAF50;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .warning-message {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #FFC107;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

if 'current_entry' not in st.session_state:
    st.session_state.current_entry = ""

if 'selected_mood' not in st.session_state:
    st.session_state.selected_mood = None

# Get data manager
dm = st.session_state.data_manager


def render_new_entry_page():
    """Render the new journal entry page"""
    st.markdown('<h1 class="main-header">📝 New Journal Entry</h1>', unsafe_allow_html=True)

    st.write("Take a moment to reflect on your day. Write about your thoughts, feelings, and experiences.")

    # Mood selector (optional)
    st.markdown("### How are you feeling? (Optional)")

    # Display currently selected mood
    if st.session_state.selected_mood:
        col_display, col_clear = st.columns([4, 1])
        with col_display:
            st.info(f"Selected mood: {st.session_state.selected_mood}")
        with col_clear:
            if st.button("Clear", key="clear_mood"):
                st.session_state.selected_mood = None
                st.rerun()

    col1, col2, col3, col4, col5 = st.columns(5)

    moods = {
        "Very Sad": "😭",
        "Sad": "😢",
        "Neutral": "😐",
        "Happy": "😊",
        "Very Happy": "😄"
    }

    for i, (mood_name, emoji) in enumerate(moods.items()):
        col = [col1, col2, col3, col4, col5][i]
        if col.button(f"{emoji} {mood_name}", key=f"mood_{mood_name}", use_container_width=True):
            st.session_state.selected_mood = emoji
            st.rerun()

    st.markdown("---")

    # Entry text area
    st.markdown("### Your Journal Entry")
    entry_text = st.text_area(
        "Write your thoughts here...",
        value=st.session_state.current_entry,
        height=300,
        max_chars=5000,
        placeholder="Today I felt..."
    )

    # Character counter
    char_count = len(entry_text)
    col1, col2 = st.columns([3, 1])
    with col2:
        if char_count < 20:
            st.caption(f"⚠️ {char_count}/5000 characters (minimum 20)")
        else:
            st.caption(f"✓ {char_count}/5000 characters")

    # Buttons
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        submit_button = st.button("Submit Entry", type="primary", use_container_width=True)

    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.current_entry = ""
            st.rerun()

    # Handle submission
    if submit_button:
        # Validation
        if not entry_text or len(entry_text.strip()) == 0:
            st.error("❌ Please write something before submitting!")
        elif len(entry_text) < 20:
            st.error(f"❌ Entry too short. Please write at least 20 characters. Current: {len(entry_text)}")
        elif len(entry_text) > 5000:
            st.error(f"❌ Entry too long. Maximum 5000 characters. Current: {len(entry_text)}")
        else:
            # Show loading spinner
            with st.spinner("Analyzing your entry..."):
                try:
                    # Analyze sentiment
                    analysis_result = analyze_sentiment(entry_text)

                    # Save to database
                    entry_id = dm.save_entry(
                        entry_text=entry_text,
                        user_selected_mood=st.session_state.selected_mood,
                        ai_sentiment_label=analysis_result['label'],
                        ai_sentiment_score=analysis_result['score'],
                        ai_confidence=analysis_result['confidence'],
                        detected_emotions=analysis_result['emotions'],
                        keywords=analysis_result['keywords']
                    )

                    # Get mood emoji
                    mood_emoji = get_mood_emoji(analysis_result['score'])

                    # Success message
                    user_mood_msg = f"<p><strong>Your Selected Mood:</strong> {st.session_state.selected_mood}</p>" if st.session_state.selected_mood else ""
                    st.markdown(f"""
                    <div class="success-message">
                        <h3>✅ Entry Saved Successfully!</h3>
                        {user_mood_msg}
                        <p><strong>AI Detected Mood:</strong> {mood_emoji} {analysis_result['label']}</p>
                        <p><strong>Sentiment Score:</strong> {analysis_result['score']:.2f}</p>
                        <p><strong>Emotions:</strong> {', '.join(analysis_result['emotions'])}</p>
                        <p><strong>Key Topics:</strong> {', '.join(analysis_result['keywords'])}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Clear entry and mood
                    st.session_state.current_entry = ""
                    st.session_state.selected_mood = None

                    # Show success button to navigate
                    if st.button("View Dashboard 📊"):
                        st.session_state.page = "📊 Dashboard"
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error saving entry: {str(e)}")
                    st.info("Your entry was not saved. Please try again.")


def render_dashboard_page():
    """Render the dashboard page"""
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)

    # Get all entries
    df = dm.get_all_entries()

    if df.empty:
        st.info("👋 Welcome! You haven't created any journal entries yet. Start by writing your first entry!")
        if st.button("Create First Entry ✍️"):
            st.session_state.page = "📝 New Entry"
            st.rerun()
        return

    # Summary statistics
    st.markdown("### 📈 Summary")
    stats = get_summary_stats(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Entries",
            value=stats['total_entries'],
            delta=None
        )

    with col2:
        st.metric(
            label="Current Streak 🔥",
            value=f"{stats['current_streak']} days",
            delta=None
        )

    with col3:
        avg_mood = stats['avg_mood_7d']
        mood_emoji = get_mood_emoji(avg_mood)
        st.metric(
            label="Avg Mood (7d)",
            value=f"{avg_mood:.2f} {mood_emoji}",
            delta=None
        )

    with col4:
        st.metric(
            label="Top Emotion",
            value=stats['top_emotion'].capitalize(),
            delta=None
        )

    st.markdown("---")

    # Time range selector
    st.markdown("### 📉 Mood Trend")
    time_range = st.selectbox(
        "Time Range",
        options=["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
        index=1
    )

    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "All Time": None
    }

    # Mood trend chart
    fig_trend = create_mood_trend_chart(df, days=days_map[time_range])
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # Two columns for additional charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎭 Emotion Distribution")
        fig_emotions = create_emotion_distribution_chart(df)
        st.plotly_chart(fig_emotions, use_container_width=True)

    with col2:
        st.markdown("### ☁️ Word Cloud")
        word_cloud_img = create_word_cloud(df)
        if word_cloud_img:
            st.image(f"data:image/png;base64,{word_cloud_img}", use_container_width=True)
        else:
            st.info("Not enough text data for word cloud yet")

    st.markdown("---")

    # Recent entries
    st.markdown("### 📚 Recent Entries")
    recent_df = dm.get_recent_entries(limit=10)

    if not recent_df.empty:
        for idx, row in recent_df.iterrows():
            with st.expander(
                f"{row['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
                f"{get_mood_emoji(row['ai_sentiment_score'])} "
                f"{row['entry_text'][:50]}..."
            ):
                st.write(f"**Full Entry:**")
                st.write(row['entry_text'])
                st.write(f"**Sentiment:** {row['ai_sentiment_label']} ({row['ai_sentiment_score']:.2f})")
                st.write(f"**Emotions:** {', '.join(row['detected_emotions'])}")
                st.write(f"**Keywords:** {', '.join(row['keywords'])}")

                if st.button(f"Delete", key=f"delete_{row['id']}"):
                    if dm.delete_entry(row['id']):
                        st.success("Entry deleted!")
                        st.rerun()


def render_insights_page():
    """Render the insights page"""
    st.markdown('<h1 class="main-header">💡 Insights</h1>', unsafe_allow_html=True)

    df = dm.get_all_entries()

    if df.empty:
        st.info("No data available yet. Start journaling to see insights!")
        return

    # Weekly summary
    st.markdown("### 📅 Weekly Summary")

    # Get last 7 days data
    now = datetime.now()
    df_7d = df[df['timestamp'] >= now - timedelta(days=7)]

    if not df_7d.empty:
        avg_sentiment = df_7d['ai_sentiment_score'].mean()
        num_entries = len(df_7d)

        # Collect all keywords
        all_keywords = []
        for keywords in df_7d['keywords']:
            if keywords:
                all_keywords.extend(keywords)

        from collections import Counter
        top_keywords = Counter(all_keywords).most_common(3)
        top_keyword = top_keywords[0][0] if top_keywords else "N/A"

        sentiment_desc = "positive" if avg_sentiment > 0.3 else "negative" if avg_sentiment < -0.3 else "mixed"

        st.markdown(f"""
        <div class="stat-card">
            <p>This week you journaled <strong>{num_entries}</strong> time(s).
            Your mood was generally <strong>{sentiment_desc}</strong> (score: {avg_sentiment:.2f}).</p>
            <p>You mentioned '<strong>{top_keyword}</strong>' frequently.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No entries in the last 7 days")

    st.markdown("---")

    # Pattern detection
    st.markdown("### 🔍 Patterns")

    col1, col2 = st.columns(2)

    with col1:
        # Day of week analysis
        st.markdown("#### Mood by Day of Week")
        fig_dow = create_day_of_week_chart(df)
        st.plotly_chart(fig_dow, use_container_width=True)

    with col2:
        # Sentiment distribution
        st.markdown("#### Sentiment Distribution")
        fig_sent = create_sentiment_distribution_chart(df)
        st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown("---")

    # Streak & Consistency
    st.markdown("### 🔥 Streak & Consistency")

    stats = dm.get_stats()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Streak", f"{stats['current_streak']} days")

    with col2:
        st.metric("Longest Streak", f"{stats['longest_streak']} days")

    with col3:
        st.metric("Consistency (30d)", f"{stats['consistency_30d']:.1f}%")

    # Calendar heatmap
    st.markdown("#### Activity Calendar")
    fig_calendar = create_calendar_heatmap(df)
    st.plotly_chart(fig_calendar, use_container_width=True)

    st.markdown("---")

    # Emotional journey
    st.markdown("### 🎢 Emotional Journey")

    if len(df) >= 2:
        # Find highest and lowest
        highest_idx = df['ai_sentiment_score'].idxmax()
        lowest_idx = df['ai_sentiment_score'].idxmin()

        highest_entry = df.loc[highest_idx]
        lowest_entry = df.loc[lowest_idx]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🌟 Peak Positive Day")
            st.write(f"**Date:** {highest_entry['timestamp'].strftime('%Y-%m-%d')}")
            st.write(f"**Score:** {highest_entry['ai_sentiment_score']:.2f}")
            with st.expander("View Entry"):
                st.write(highest_entry['entry_text'])

        with col2:
            st.markdown("#### 😔 Lowest Day")
            st.write(f"**Date:** {lowest_entry['timestamp'].strftime('%Y-%m-%d')}")
            st.write(f"**Score:** {lowest_entry['ai_sentiment_score']:.2f}")
            with st.expander("View Entry"):
                st.write(lowest_entry['entry_text'])


def render_all_entries_page():
    """Render the all entries page with filters"""
    st.markdown('<h1 class="main-header">📚 All Entries</h1>', unsafe_allow_html=True)

    df = dm.get_all_entries()

    if df.empty:
        st.info("No entries yet. Start journaling!")
        return

    # Filters
    with st.expander("🔍 Filters", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            # Date range
            min_date = df['timestamp'].min().date()
            max_date = df['timestamp'].max().date()

            start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
            end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

        with col2:
            # Sentiment filter
            sentiment_filter = st.multiselect(
                "Sentiment",
                options=["POSITIVE", "NEGATIVE", "NEUTRAL"],
                default=["POSITIVE", "NEGATIVE", "NEUTRAL"]
            )

        with col3:
            # Keyword search
            keyword = st.text_input("Search Keyword", placeholder="Enter keyword...")

    # Apply filters
    filtered_df = df.copy()

    # Date filter
    filtered_df = filtered_df[
        (filtered_df['timestamp'].dt.date >= start_date) &
        (filtered_df['timestamp'].dt.date <= end_date)
    ]

    # Sentiment filter
    if sentiment_filter:
        filtered_df = filtered_df[filtered_df['ai_sentiment_label'].isin(sentiment_filter)]

    # Keyword filter
    if keyword:
        filtered_df = filtered_df[
            filtered_df['entry_text'].str.contains(keyword, case=False, na=False)
        ]

    # Display results
    st.write(f"**Showing {len(filtered_df)} of {len(df)} entries**")

    if filtered_df.empty:
        st.warning("No entries match your filters")
        return

    # Sort options
    sort_by = st.selectbox(
        "Sort by",
        options=["Date (Newest)", "Date (Oldest)", "Mood (Highest)", "Mood (Lowest)"]
    )

    if sort_by == "Date (Newest)":
        filtered_df = filtered_df.sort_values('timestamp', ascending=False)
    elif sort_by == "Date (Oldest)":
        filtered_df = filtered_df.sort_values('timestamp', ascending=True)
    elif sort_by == "Mood (Highest)":
        filtered_df = filtered_df.sort_values('ai_sentiment_score', ascending=False)
    else:  # Mood (Lowest)
        filtered_df = filtered_df.sort_values('ai_sentiment_score', ascending=True)

    # Display entries
    st.markdown("---")

    # Pagination
    entries_per_page = 20
    total_pages = (len(filtered_df) - 1) // entries_per_page + 1

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=st.session_state.current_page
    )

    start_idx = (page - 1) * entries_per_page
    end_idx = start_idx + entries_per_page

    page_df = filtered_df.iloc[start_idx:end_idx]

    for idx, row in page_df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                st.write(f"**{row['timestamp'].strftime('%Y-%m-%d %H:%M')}**")

            with col2:
                mood_color = get_mood_color(row['ai_sentiment_score'])
                st.markdown(
                    f"<span style='color:{mood_color}'>●</span> {row['ai_sentiment_label']}",
                    unsafe_allow_html=True
                )

            with col3:
                st.write(f"Score: {row['ai_sentiment_score']:.2f}")

            with col4:
                if st.button("Delete", key=f"del_{row['id']}"):
                    if dm.delete_entry(row['id']):
                        st.success("Deleted!")
                        st.rerun()

            with st.expander("View Full Entry"):
                st.write(row['entry_text'])
                st.write(f"**Emotions:** {', '.join(row['detected_emotions'])}")
                st.write(f"**Keywords:** {', '.join(row['keywords'])}")

            st.markdown("---")


def render_export_page():
    """Render the export data page"""
    st.markdown('<h1 class="main-header">📥 Export Data</h1>', unsafe_allow_html=True)

    st.write("Export all your journal entries to a CSV file for backup or analysis.")

    df = dm.get_all_entries()

    if df.empty:
        st.info("No data to export yet.")
        return

    st.write(f"**Total Entries:** {len(df)}")

    # Preview
    st.markdown("### Preview")
    st.dataframe(df.head(10))

    # Export button
    if st.button("Download CSV", type="primary"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"journal_export_{timestamp}.csv"

        # Prepare dataframe for export
        export_df = df.copy()
        export_df['detected_emotions'] = export_df['detected_emotions'].apply(str)
        export_df['keywords'] = export_df['keywords'].apply(str)

        csv = export_df.to_csv(index=False)

        st.download_button(
            label="Click to Download",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )

        st.success(f"✅ Ready to download: {filename}")


# Main app
def main():
    """Main application"""

    # Sidebar navigation
    st.sidebar.markdown("# 📔 Emotional Journal")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        options=[
            "📝 New Entry",
            "📊 Dashboard",
            "💡 Insights",
            "📚 All Entries",
            "📥 Export Data"
        ]
    )

    # Render selected page
    if page == "📝 New Entry":
        render_new_entry_page()
    elif page == "📊 Dashboard":
        render_dashboard_page()
    elif page == "💡 Insights":
        render_insights_page()
    elif page == "📚 All Entries":
        render_all_entries_page()
    elif page == "📥 Export Data":
        render_export_page()


if __name__ == "__main__":
    main()
