"""
Emotion Detection System for Yui AI Companion
Uses VADER sentiment analysis to detect user emotions
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Tuple
import re


class EmotionDetector:
    """Detects emotions from user messages using sentiment analysis"""
    
    def __init__(self):
        """Initialize VADER sentiment analyzer"""
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Emotion keywords for better classification
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'wonderful', 'awesome', 'love', 'perfect', 
                   'amazing', 'fantastic', 'excellent', 'yay', '😊', '😄', '🎉', '❤️'],
            'sadness': ['sad', 'unhappy', 'depressed', 'down', 'upset', 'disappointed',
                       'miserable', 'hurt', 'cry', 'crying', '😢', '😞', '💔'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated',
                     'pissed', 'rage', 'hate', '😠', '😡', '🤬'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'terrified',
                    'frightened', 'panic', 'stress', 'stressed', '😰', '😨'],
            'surprise': ['surprising', 'shocked', 'amazed', 'unexpected', 'wow', 'omg',
                        'incredible', 'unbelievable', '😲', '😮'],
            'disgust': ['disgusting', 'gross', 'awful', 'terrible', 'horrible', 'nasty',
                       'revolting', '🤢', '🤮'],
            'love': ['love', 'adore', 'cherish', 'affection', 'care', 'appreciate',
                    'grateful', 'thankful', 'blessed', '❤️', '💕', '🥰'],
            'excitement': ['excited', 'thrilled', 'eager', 'pumped', 'hyped', 'enthusiastic',
                          'can\'t wait', '🔥', '⚡', '🎊'],
        }
    
    def analyze_emotion(self, text: str) -> Dict:
        """
        Analyze emotion from text
        
        Args:
            text: User's message
            
        Returns:
            Dict with emotion, sentiment scores, and confidence
        """
        # Get VADER sentiment scores
        scores = self.analyzer.polarity_scores(text)
        
        # Classify emotion based on keywords
        emotion = self._classify_emotion(text, scores)
        
        # Determine intensity
        intensity = self._get_intensity(scores)
        
        return {
            'emotion': emotion,
            'sentiment': 'positive' if scores['compound'] > 0.05 else 'negative' if scores['compound'] < -0.05 else 'neutral',
            'intensity': intensity,
            'confidence': abs(scores['compound']),
            'scores': {
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'compound': scores['compound']
            }
        }
    
    def _classify_emotion(self, text: str, scores: Dict) -> str:
        """Classify specific emotion based on keywords and scores"""
        text_lower = text.lower()
        
        # Check for specific emotion keywords
        emotion_matches = {}
        for emotion, keywords in self.emotion_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                emotion_matches[emotion] = matches
        
        # If we found emotion keywords, return the most matched one
        if emotion_matches:
            return max(emotion_matches, key=emotion_matches.get)
        
        # Otherwise, classify based on sentiment scores
        compound = scores['compound']
        
        if compound > 0.5:
            return 'joy'
        elif compound < -0.5:
            if scores['neg'] > 0.3:
                return 'anger'
            else:
                return 'sadness'
        elif compound > 0.05:
            return 'positive'
        elif compound < -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_intensity(self, scores: Dict) -> str:
        """Determine emotion intensity"""
        compound = abs(scores['compound'])
        
        if compound > 0.7:
            return 'strong'
        elif compound > 0.3:
            return 'moderate'
        else:
            return 'mild'
    
    def should_show_empathy(self, emotion_data: Dict) -> bool:
        """Determine if bot should show strong empathy"""
        negative_emotions = ['sadness', 'anger', 'fear', 'disgust', 'negative']
        return (
            emotion_data['emotion'] in negative_emotions and 
            emotion_data['intensity'] in ['moderate', 'strong']
        )
    
    def should_celebrate(self, emotion_data: Dict) -> bool:
        """Determine if bot should celebrate with user"""
        positive_emotions = ['joy', 'excitement', 'love', 'surprise']
        return (
            emotion_data['emotion'] in positive_emotions and
            emotion_data['intensity'] in ['moderate', 'strong']
        )
    
    def get_emotion_context(self, emotion_data: Dict) -> str:
        """
        Get context string for emotion to include in prompt
        
        Args:
            emotion_data: Result from analyze_emotion()
            
        Returns:
            Context string for LLM
        """
        emotion = emotion_data['emotion']
        intensity = emotion_data['intensity']
        
        if self.should_show_empathy(emotion_data):
            return f"The user seems to be feeling {emotion} ({intensity} intensity). Show empathy and support."
        elif self.should_celebrate(emotion_data):
            return f"The user is feeling {emotion} ({intensity} intensity). Share their excitement!"
        else:
            return f"The user's emotional state: {emotion} ({intensity})."


class EmotionState:
    """Tracks bot's emotional state for consistent personality"""
    
    def __init__(self):
        """Initialize emotion state"""
        self.current_mood = 'neutral'
        self.mood_history = []
        self.conversation_tone = 'balanced'
    
    def update_mood(self, user_emotion: str):
        """Update bot's mood based on user emotion"""
        # Bot mirrors user emotions to some degree
        mood_mapping = {
            'joy': 'cheerful',
            'excitement': 'energetic',
            'love': 'warm',
            'sadness': 'empathetic',
            'anger': 'calm',  # Bot stays calm when user is angry
            'fear': 'reassuring',
            'neutral': 'neutral'
        }
        
        self.current_mood = mood_mapping.get(user_emotion, 'neutral')
        self.mood_history.append(self.current_mood)
        
        # Keep only last 10 moods
        if len(self.mood_history) > 10:
            self.mood_history = self.mood_history[-10:]
    
    def get_tone_instruction(self) -> str:
        """Get instruction for bot's tone based on mood"""
        tone_instructions = {
            'cheerful': "Respond with warmth and positivity.",
            'energetic': "Match their energy with enthusiasm!",
            'warm': "Be extra caring and affectionate.",
            'empathetic': "Be gentle, understanding, and supportive.",
            'calm': "Stay calm and de-escalate. Be patient and understanding.",
            'reassuring': "Be reassuring and help them feel safe.",
            'neutral': "Maintain your natural personality."
        }
        
        return tone_instructions.get(self.current_mood, "Be yourself.")
