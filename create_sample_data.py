"""
Sample Data Generator for Emotional Journal MVP
Creates realistic journal entries for testing and demonstration
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add utils to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_manager import DataManager
from utils.sentiment_analyzer_lite import analyze_sentiment


# Sample journal entries with varying sentiments
SAMPLE_ENTRIES = [
    # Positive entries
    {
        "text": "Today was absolutely wonderful! I finally completed that big project I've been working on for weeks. My team was so supportive and we celebrated together. Feeling really accomplished and grateful for this opportunity. Can't wait to see what tomorrow brings!",
        "days_ago": 1
    },
    {
        "text": "Had the most amazing coffee with an old friend today. We laughed so much reminiscing about college days. It's incredible how some friendships never fade no matter how much time passes. Feeling blessed and happy!",
        "days_ago": 3
    },
    {
        "text": "Started my morning with a beautiful sunrise run. The weather was perfect and I felt so energized afterwards. Made a healthy breakfast and tackled my to-do list. These are the days I feel most alive and productive!",
        "days_ago": 5
    },
    {
        "text": "Got promoted at work today! All the hard work and late nights finally paid off. My manager praised my dedication and innovative thinking. Celebrated with family over dinner. So excited for this new chapter!",
        "days_ago": 8
    },
    {
        "text": "Discovered a new hobby today - painting! Never thought I'd enjoy it but it was so therapeutic. Spent hours just creating and it felt amazing to express myself artistically. Looking forward to exploring this more.",
        "days_ago": 12
    },

    # Negative entries
    {
        "text": "Rough day at work. The presentation didn't go as planned and I felt unprepared. My boss seemed disappointed and I couldn't stop replaying my mistakes. Feeling stressed and down about the whole situation.",
        "days_ago": 2
    },
    {
        "text": "Feeling overwhelmed with everything on my plate right now. Work deadlines, family responsibilities, and personal goals all seem impossible to manage. Haven't been sleeping well and it's affecting my mood. Need to find a better balance.",
        "days_ago": 6
    },
    {
        "text": "Had an argument with my best friend today over something silly. I hate conflict and it's been weighing on me all day. Worried about our friendship and feeling sad about how things escalated. Hope we can talk it through soon.",
        "days_ago": 10
    },
    {
        "text": "Received some disappointing news about the apartment I wanted to rent. Back to square one with house hunting and feeling frustrated with the whole process. Sometimes it feels like nothing is going right.",
        "days_ago": 15
    },

    # Neutral/Mixed entries
    {
        "text": "Pretty ordinary day. Went to work, had some meetings, came home. Nothing particularly exciting but nothing bad either. Made dinner, watched TV, now getting ready for bed. Just another Tuesday I guess.",
        "days_ago": 4
    },
    {
        "text": "Worked from home today which had its ups and downs. More productive without office distractions but also felt a bit isolated. Had a good lunch break walk though. Mixed feelings about the remote work setup.",
        "days_ago": 7
    },
    {
        "text": "Tried a new recipe for dinner - turned out okay but not amazing. Spent some time organizing my closet which was overdue. Got some things done but still have a long to-do list. Making progress slowly.",
        "days_ago": 9
    },
    {
        "text": "Attended a virtual conference today. Some sessions were interesting, others not so much. Made a few professional connections which could be useful. Overall a decent learning experience but quite exhausting staring at screens all day.",
        "days_ago": 13
    },
    {
        "text": "Weekend is here! Slept in, did some errands, meal prepped for the week. Nothing extraordinary but it felt good to have a relaxed day. Sometimes the simple things are enough.",
        "days_ago": 16
    },

    # Reflective entries
    {
        "text": "Been thinking a lot about my goals and where I want to be in five years. It's both exciting and scary to dream big. Started journaling more regularly to track my thoughts and progress. Feeling hopeful about the future.",
        "days_ago": 11
    },
    {
        "text": "Reconnected with nature today with a long hike in the mountains. It was exactly what I needed to clear my head and gain perspective. Reminded me to slow down and appreciate the present moment more often.",
        "days_ago": 14
    },
]


def create_sample_data(num_entries: int = None):
    """
    Create sample journal entries for testing

    Args:
        num_entries: Number of entries to create (None = all samples)
    """
    print("🎨 Creating sample journal entries...")

    # Initialize data manager
    dm = DataManager()

    # Select entries to create
    entries_to_create = SAMPLE_ENTRIES if num_entries is None else SAMPLE_ENTRIES[:num_entries]

    created_count = 0
    for entry_data in entries_to_create:
        try:
            # Calculate timestamp
            timestamp = datetime.now() - timedelta(days=entry_data['days_ago'])

            # Analyze sentiment
            analysis = analyze_sentiment(entry_data['text'])

            # Save entry
            # Note: We're bypassing the normal save to set custom timestamps
            import sqlite3
            import json
            conn = sqlite3.connect(dm.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO journal_entries (
                    timestamp, entry_text, ai_sentiment_label,
                    ai_sentiment_score, ai_confidence, word_count,
                    detected_emotions, keywords
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                entry_data['text'],
                analysis['label'],
                analysis['score'],
                analysis['confidence'],
                len(entry_data['text'].split()),
                json.dumps(analysis['emotions']),
                json.dumps(analysis['keywords'])
            ))

            conn.commit()
            conn.close()

            created_count += 1
            print(f"✅ Created entry {created_count}/{len(entries_to_create)}: {analysis['label']} "
                  f"({entry_data['days_ago']} days ago)")

        except Exception as e:
            print(f"❌ Error creating entry: {e}")

    print(f"\n🎉 Successfully created {created_count} sample entries!")
    print("You can now run the app with: streamlit run app.py")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate sample journal entries")
    parser.add_argument(
        '--count',
        type=int,
        default=None,
        help='Number of entries to create (default: all available)'
    )

    args = parser.parse_args()

    create_sample_data(num_entries=args.count)
