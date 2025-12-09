"""
Sentiment Analyzer for Emotional Journal MVP
Uses Hugging Face Transformers with TextBlob fallback
"""

import logging
from typing import Dict, List
import re
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache
_sentiment_pipeline = None
_emotion_pipeline = None


def _load_sentiment_model():
    """Load sentiment analysis model (singleton pattern)"""
    global _sentiment_pipeline

    if _sentiment_pipeline is None:
        try:
            from transformers import pipeline
            logger.info("Loading Hugging Face sentiment model...")
            _sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1  # Use CPU (set to 0 for GPU)
            )
            logger.info("Sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Hugging Face model: {e}")
            _sentiment_pipeline = "failed"

    return _sentiment_pipeline


def _load_emotion_model():
    """Load emotion classification model (optional)"""
    global _emotion_pipeline

    if _emotion_pipeline is None:
        try:
            from transformers import pipeline
            logger.info("Loading emotion classification model...")
            _emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=-1,
                top_k=None
            )
            logger.info("Emotion model loaded successfully")
        except Exception as e:
            logger.warning(f"Emotion model not available: {e}")
            _emotion_pipeline = "failed"

    return _emotion_pipeline


def _fallback_sentiment_textblob(text: str) -> Dict:
    """
    Fallback sentiment analysis using TextBlob

    Args:
        text: Text to analyze

    Returns:
        Dictionary with sentiment data
    """
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            label = "POSITIVE"
        elif polarity < -0.1:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"

        return {
            'label': label,
            'score': polarity,
            'confidence': 0.5  # TextBlob doesn't provide confidence
        }
    except Exception as e:
        logger.error(f"TextBlob fallback failed: {e}")
        return {
            'label': 'NEUTRAL',
            'score': 0.0,
            'confidence': 0.0
        }


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
        'joy': ['happy', 'joy', 'excited', 'wonderful', 'amazing', 'great', 'love', 'fantastic'],
        'sadness': ['sad', 'depressed', 'unhappy', 'down', 'crying', 'tears', 'lonely', 'miss'],
        'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated', 'hate'],
        'fear': ['afraid', 'scared', 'anxious', 'worried', 'nervous', 'panic', 'terrified'],
        'surprise': ['surprised', 'shocked', 'amazed', 'unexpected', 'sudden', 'wow'],
        'gratitude': ['grateful', 'thankful', 'appreciate', 'blessed', 'lucky', 'fortunate'],
        'hope': ['hope', 'optimistic', 'looking forward', 'excited about', 'can\'t wait'],
        'stress': ['stressed', 'overwhelmed', 'pressure', 'burden', 'exhausted', 'tired']
    }

    detected = []
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected.append(emotion)

    # If no specific emotions detected, infer from sentiment
    if not detected:
        if sentiment_label == "POSITIVE":
            detected.append('joy')
        elif sentiment_label == "NEGATIVE":
            detected.append('sadness')
        else:
            detected.append('neutral')

    return detected[:3]  # Return top 3 emotions


def _detect_emotions_with_model(text: str) -> List[str]:
    """
    Detect emotions using transformer model

    Args:
        text: Text to analyze

    Returns:
        List of detected emotions
    """
    emotion_pipeline = _load_emotion_model()

    if emotion_pipeline == "failed" or emotion_pipeline is None:
        return []

    try:
        # Truncate text to avoid token limit issues
        truncated_text = text[:512]

        results = emotion_pipeline(truncated_text)

        if results and isinstance(results, list) and len(results) > 0:
            # Sort by score and get top 3
            sorted_emotions = sorted(results[0], key=lambda x: x['score'], reverse=True)
            return [e['label'] for e in sorted_emotions[:3]]
        else:
            return []

    except Exception as e:
        logger.warning(f"Emotion detection failed: {e}")
        return []


def analyze_sentiment(text: str) -> Dict:
    """
    Analyze sentiment of journal entry text

    Args:
        text: Journal entry text

    Returns:
        Dictionary with sentiment analysis results:
        {
            'label': str,           # POSITIVE, NEGATIVE, NEUTRAL
            'score': float,         # -1 to 1 scale
            'confidence': float,    # 0 to 1
            'emotions': list,       # Detected emotions
            'keywords': list        # Top keywords
        }
    """
    # Load model
    sentiment_pipeline = _load_sentiment_model()

    # Try Hugging Face model first
    if sentiment_pipeline != "failed" and sentiment_pipeline is not None:
        try:
            # Truncate text to model's max length
            truncated_text = text[:512]

            result = sentiment_pipeline(truncated_text)[0]

            # Convert to -1 to 1 scale
            if result['label'] == 'POSITIVE':
                score = result['score']
            else:  # NEGATIVE
                score = -result['score']

            # Determine label with neutral zone
            if score > 0.3:
                label = 'POSITIVE'
            elif score < -0.3:
                label = 'NEGATIVE'
            else:
                label = 'NEUTRAL'

            sentiment_data = {
                'label': label,
                'score': score,
                'confidence': result['score']
            }

            logger.info(f"Sentiment analysis: {label} (score: {score:.2f})")

        except Exception as e:
            logger.warning(f"Hugging Face analysis failed, using fallback: {e}")
            sentiment_data = _fallback_sentiment_textblob(text)
    else:
        # Use TextBlob fallback
        logger.info("Using TextBlob fallback for sentiment analysis")
        sentiment_data = _fallback_sentiment_textblob(text)

    # Detect emotions
    # Try model-based detection first
    emotions = _detect_emotions_with_model(text)

    # If model fails or returns nothing, use keyword-based detection
    if not emotions:
        emotions = _detect_emotions_from_keywords(text, sentiment_data['label'])

    # Extract keywords
    keywords = _extract_keywords(text)

    # Combine all results
    return {
        'label': sentiment_data['label'],
        'score': sentiment_data['score'],
        'confidence': sentiment_data['confidence'],
        'emotions': emotions,
        'keywords': keywords
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
