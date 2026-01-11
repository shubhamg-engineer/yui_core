import requests
from typing import Dict, Optional, List
import random

class APIManager:
    """Manager for external APIs to enhance Yui's intelligence"""
    
    def __init__(self):
        # No API keys required for these free APIs!
        self.apis = {
            "weather": "https://wttr.in",  # Free weather API
            "jokes": "https://v2.jokeapi.dev/joke",
            "quotes": "https://zenquotes.io/api",
            "facts": "https://uselessfacts.jsph.pl/api/v2/facts",
            "advice": "https://api.adviceslip.com/advice",
            "activities": "https://www.boredapi.com/api/activity",
            "crypto": "https://api.coingecko.com/api/v3",
            "dictionary": "https://api.dictionaryapi.dev/api/v2/entries/en"
        }
    
    # ============ WEATHER ============
    def get_weather(self, location: str = "auto") -> Dict:
        """
        Get current weather for location
        
        Args:
            location: City name or "auto" for automatic detection
        
        Returns:
            Weather data dictionary
        """
        try:
            url = f"{self.apis['weather']}/{location}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                return {
                    "success": True,
                    "location": data['nearest_area'][0]['areaName'][0]['value'],
                    "temperature_c": current['temp_C'],
                    "temperature_f": current['temp_F'],
                    "description": current['weatherDesc'][0]['value'],
                    "feels_like_c": current['FeelsLikeC'],
                    "humidity": current['humidity'],
                    "wind_speed": current['windspeedKmph']
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ JOKES ============
    def get_joke(self, category: str = "Any") -> Dict:
        """
        Get a random joke
        
        Args:
            category: Programming, Misc, Dark, Pun, Spooky, Christmas
        
        Returns:
            Joke data
        """
        try:
            url = f"{self.apis['jokes']}/{category}?safe-mode"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['type'] == 'single':
                    return {
                        "success": True,
                        "joke": data['joke'],
                        "category": data['category']
                    }
                else:
                    return {
                        "success": True,
                        "setup": data['setup'],
                        "delivery": data['delivery'],
                        "category": data['category']
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ QUOTES ============
    def get_quote(self) -> Dict:
        """Get inspirational quote"""
        try:
            url = f"{self.apis['quotes']}/random"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()[0]
                return {
                    "success": True,
                    "quote": data['q'],
                    "author": data['a']
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ FUN FACTS ============
    def get_fun_fact(self) -> Dict:
        """Get a random fun fact"""
        try:
            url = f"{self.apis['facts']}/random"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "fact": data['text']
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ ADVICE ============
    def get_advice(self) -> Dict:
        """Get random advice"""
        try:
            url = f"{self.apis['advice']}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "advice": data['slip']['advice']
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ ACTIVITIES ============
    def get_activity(self, activity_type: Optional[str] = None) -> Dict:
        """
        Get activity suggestion
        
        Args:
            activity_type: education, recreational, social, diy, charity, 
                          cooking, relaxation, music, busywork
        """
        try:
            url = f"{self.apis['activities']}"
            if activity_type:
                url += f"?type={activity_type}"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "activity": data['activity'],
                    "type": data['type'],
                    "participants": data['participants'],
                    "price": data['price']
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ CRYPTOCURRENCY ============
    def get_crypto_price(self, coin_id: str = "bitcoin") -> Dict:
        """
        Get cryptocurrency price
        
        Args:
            coin_id: bitcoin, ethereum, cardano, etc.
        """
        try:
            url = f"{self.apis['crypto']}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd,inr",
                "include_24hr_change": "true"
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if coin_id in data:
                    return {
                        "success": True,
                        "coin": coin_id,
                        "price_usd": data[coin_id].get('usd'),
                        "price_inr": data[coin_id].get('inr'),
                        "change_24h": data[coin_id].get('usd_24h_change')
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ DICTIONARY ============
    def get_definition(self, word: str) -> Dict:
        """Get word definition"""
        try:
            url = f"{self.apis['dictionary']}/{word}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()[0]
                meanings = data['meanings'][0]
                
                return {
                    "success": True,
                    "word": data['word'],
                    "phonetic": data.get('phonetic', ''),
                    "part_of_speech": meanings['partOfSpeech'],
                    "definition": meanings['definitions'][0]['definition'],
                    "example": meanings['definitions'][0].get('example', '')
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ HELPER: Smart API Call ============
    def smart_call(self, intent: str, **kwargs) -> Dict:
        """
        Intelligently call the right API based on user intent
        
        Args:
            intent: weather, joke, quote, fact, advice, activity, crypto, definition
            **kwargs: Additional parameters
        
        Returns:
            API response
        """
        intent_map = {
            "weather": self.get_weather,
            "joke": self.get_joke,
            "quote": self.get_quote,
            "fact": self.get_fun_fact,
            "advice": self.get_advice,
            "activity": self.get_activity,
            "crypto": self.get_crypto_price,
            "definition": self.get_definition
        }
        
        if intent in intent_map:
            return intent_map[intent](**kwargs)
        else:
            return {"success": False, "error": f"Unknown intent: {intent}"}


# ============ USAGE EXAMPLES ============
if __name__ == "__main__":
    api = APIManager()
    
    # Test weather
    print("Weather:", api.get_weather("London"))
    
    # Test joke
    print("\nJoke:", api.get_joke())
    
    # Test quote
    print("\nQuote:", api.get_quote())
    
    # Test fact
    print("\nFact:", api.get_fun_fact())
    
    # Test advice
    print("\nAdvice:", api.get_advice())
    
    # Test activity
    print("\nActivity:", api.get_activity())
    
    # Test crypto
    print("\nBitcoin:", api.get_crypto_price("bitcoin"))
    
    # Test definition
    print("\nDefinition:", api.get_definition("serendipity"))