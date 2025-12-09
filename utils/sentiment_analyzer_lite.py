"""
Lightweight Sentiment Analyzer for Emotional Journal MVP
Uses TextBlob for stability - no heavy ML models
"""

import logging
from typing import Dict, List
import re
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract top keywords from text

    Args:
        text: Text to analyze
        top_n: Number of keywords to extract

    Returns:
        List of keywords
    """
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'i', 'you', 'he', 'she',
        'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'this', 'that', 'these', 'those', 'am', 'me', 'just', 'so', 'very',
        'really', 'too', 'much', 'more', 'most', 'some', 'any', 'all', 'both',
        'each', 'few', 'many', 'other', 'such', 'no', 'not', 'only', 'own',
        'same', 'than', 'then', 'there', 'when', 'where', 'why', 'how'
    }

    # Clean and tokenize text
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Filter stop words and count
    filtered_words = [w for w in words if w not in stop_words]
    word_counts = Counter(filtered_words)

    # Return top N keywords
    return [word for word, _ in word_counts.most_common(top_n)]


def _detect_emotions_from_keywords(text: str, sentiment_label: str) -> List[str]:
    """
    Detect emotions based on keywords (simple rule-based approach)

    Args:
        text: Text to analyze
        sentiment_label: Overall sentiment label

    Returns:
        List of detected emotions
    """
    text_lower = text.lower()

    emotion_keywords = {
        'joy': ['happy', 'joy', 'excited', 'wonderful', 'amazing', 'great', 'love', 'fantastic', 'delighted', 'thrilled'],
        'sadness': ['sad', 'depressed', 'unhappy', 'down', 'crying', 'tears', 'lonely', 'miss', 'disappointed', 'heartbroken'],
        'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated', 'hate', 'rage', 'outraged'],
        'fear': ['afraid', 'scared', 'anxious', 'worried', 'nervous', 'panic', 'terrified', 'frightened'],
        'surprise': ['surprised', 'shocked', 'amazed', 'unexpected', 'sudden', 'wow', 'astonished'],
        'gratitude': ['grateful', 'thankful', 'appreciate', 'blessed', 'lucky', 'fortunate', 'thanks'],
        'hope': ['hope', 'optimistic', 'looking forward', 'excited about', 'can\'t wait', 'hopeful'],
        'stress': ['stressed', 'overwhelmed', 'pressure', 'burden', 'exhausted', 'tired', 'burned out']
    }

    detected = []
    emotion_scores = {}

    for emotion, keywords in emotion_keywords.items():
        count = sum(1 for keyword in keywords if keyword in text_lower)
        if count > 0:
            emotion_scores[emotion] = count

    # Sort by count and take top 3
    if emotion_scores:
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        detected = [emotion for emotion, _ in sorted_emotions[:3]]

    # If no specific emotions detected, infer from sentiment
    if not detected:
        if sentiment_label == "POSITIVE":
            detected.append('joy')
        elif sentiment_label == "NEGATIVE":
            detected.append('sadness')
        else:
            detected.append('neutral')

    return detected


def analyze_sentiment(text: str) -> Dict:
    """
    Analyze sentiment of journal entry text using TextBlob

    Args:
        text: Journal entry text

    Returns:
        Dictionary with sentiment analysis results
    """
    try:
        from textblob import TextBlob

        # Analyze with TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Convert polarity to label
        if polarity > 0.1:
            label = 'POSITIVE'
        elif polarity < -0.1:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'

        # Detect emotions
        emotions = _detect_emotions_from_keywords(text, label)

        # Extract keywords
        keywords = _extract_keywords(text)

        logger.info(f"Sentiment analysis: {label} (score: {polarity:.2f})")

        return {
            'label': label,
            'score': polarity,
            'confidence': abs(polarity),  # Use absolute polarity as confidence
            'emotions': emotions,
            'keywords': keywords
        }

    except ImportError:
        logger.error("TextBlob not installed")
        # Return default values if TextBlob isn't available
        return {
            'label': 'NEUTRAL',
            'score': 0.0,
            'confidence': 0.0,
            'emotions': ['neutral'],
            'keywords': _extract_keywords(text)
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return {
            'label': 'NEUTRAL',
            'score': 0.0,
            'confidence': 0.0,
            'emotions': ['neutral'],
            'keywords': _extract_keywords(text)
        }


def get_mood_emoji(sentiment_score: float) -> str:
    """
    Get emoji representation of mood based on sentiment score

    Args:
        sentiment_score: Sentiment score (-1 to 1)

    Returns:
        Emoji string
    """
    if sentiment_score > 0.5:
        return "😄"
    elif sentiment_score > 0.3:
        return "😊"
    elif sentiment_score > -0.3:
        return "😐"
    elif sentiment_score > -0.5:
        return "😢"
    else:
        return "😭"


def get_mood_color(sentiment_score: float) -> str:
    """
    Get color code for mood based on sentiment score

    Args:
        sentiment_score: Sentiment score (-1 to 1)

    Returns:
        Hex color code
    """
    if sentiment_score > 0.3:
        return "#4CAF50"  # Green
    elif sentiment_score < -0.3:
        return "#F44336"  # Red
    else:
        return "#FFC107"  # Yellow
