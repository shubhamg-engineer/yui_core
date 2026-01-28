"""
Tool Executor - Intelligently detects when to use tools and executes them
Adds web search capability using DuckDuckGo
"""
import re
from typing import Optional, Dict
from tools.api_manager import APIManager

try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False


class ToolExecutor:
    """Detects intents and executes appropriate tools"""
    
    def __init__(self):
        self.api_manager = APIManager()
        
        # Intent detection patterns
        self.patterns = {
            'weather': r'(weather|temperature|forecast|hot|cold|sunny|rainy|climate)\s+(in|at|for)?\s+([a-zA-Z\s]+)',
            'joke': r'(tell|give|say)\s+(me\s+)?(a\s+)?(joke|funny)',
            'quote': r'(quote|inspiration|motivate|wisdom)',
            'fact': r'(fact|trivia|did you know|interesting)',
            'advice': r'(advice|tip|suggestion|recommend)',
            'activity': r'(bored|activity|something to do|what should i do)',
            'crypto': r'(bitcoin|ethereum|crypto|btc|eth)\s+(price)?',
            'definition': r'(define|definition|meaning|what (is|does))\s+(.+)',
            'search': r'(search|find|look up|google|tell me about|what is)\s+(.+)',
        }
    
    def detect_intent(self, message: str) -> Optional[tuple]:
        """
        Detect if user wants to use a tool
        
        Returns:
            (intent, extracted_value) or None
        """
        message_lower = message.lower()
        
        # Weather - extract location
        if match := re.search(self.patterns['weather'], message_lower):
            location = match.group(3).strip() if match.group(3) else "auto"
            return ('weather', location)
        
        # Joke
        if re.search(self.patterns['joke'], message_lower):
            return ('joke', None)
        
        # Quote
        if re.search(self.patterns['quote'], message_lower):
            return ('quote', None)
        
        # Fact
        if re.search(self.patterns['fact'], message_lower):
            return ('fact', None)
        
        # Advice
        if re.search(self.patterns['advice'], message_lower):
            return ('advice', None)
        
        # Activity
        if re.search(self.patterns['activity'], message_lower):
            return ('activity', None)
        
        # Crypto
        if match := re.search(self.patterns['crypto'], message_lower):
            coin = 'bitcoin'  # default
            if 'ethereum' in message_lower or 'eth' in message_lower:
                coin = 'ethereum'
            return ('crypto', coin)
        
        # Definition
        if match := re.search(self.patterns['definition'], message_lower):
            word = match.group(3).strip() if match.group(3) else None
            if word:
                return ('definition', word)
        
        # Web search (catch-all for questions)
        if match := re.search(self.patterns['search'], message_lower):
            query = match.group(2).strip() if match.group(2) else message
            return ('search', query)
        
        return None
    
    def execute_tool(self, intent: str, value: Optional[str] = None) -> Dict:
        """Execute the detected tool"""
        
        if intent == 'weather':
            return self.api_manager.get_weather(value or "auto")
        
        elif intent == 'joke':
            return self.api_manager.get_joke()
        
        elif intent == 'quote':
            return self.api_manager.get_quote()
        
        elif intent == 'fact':
            return self.api_manager.get_fun_fact()
        
        elif intent == 'advice':
            return self.api_manager.get_advice()
        
        elif intent == 'activity':
            return self.api_manager.get_activity()
        
        elif intent == 'crypto':
            return self.api_manager.get_crypto_price(value or "bitcoin")
        
        elif intent == 'definition':
            if value:
                return self.api_manager.get_definition(value)
        
        elif intent == 'search':
            return self.web_search(value or "")
        
        return {"success": False, "error": "Unknown intent"}
    
    def web_search(self, query: str, max_results: int = 3) -> Dict:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Number of results to return
            
        Returns:
            Search results
        """
        if not WEB_SEARCH_AVAILABLE:
            return {
                "success": False, 
                "error": "Web search not available (duckduckgo-search not installed)"
            }
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                
                if results:
                    return {
                        "success": True,
                        "query": query,
                        "results": [
                            {
                                "title": r.get('title', ''),
                                "snippet": r.get('body', ''),
                                "url": r.get('href', '')
                            }
                            for r in results
                        ]
                    }
                else:
                    return {"success": False, "error": "No results found"}
                    
        except Exception as e:
            return {"success": False, "error": f"Search failed: {str(e)}"}
    
    def process_message(self, message: str) -> Optional[str]:
        """
        Process message and execute tool if needed
        
        Args:
            message: User's message
            
        Returns:
            Formatted tool result or None if no tool detected
        """
        detection = self.detect_intent(message)
        
        if not detection:
            return None
        
        intent, value = detection
        result = self.execute_tool(intent, value)
        
        if not result.get('success'):
            return None  # Let LLM handle the conversation normally
        
        # Format results for different tools
        return self.format_result(intent, result)
    
    def format_result(self, intent: str, result: Dict) -> str:
        """Format tool result into readable text"""
        
        if intent == 'weather':
            return f"""Weather for {result['location']}:
- Temperature: {result['temperature_c']}°C ({result['temperature_f']}°F)
- Conditions: {result['description']}
- Feels like: {result['feels_like_c']}°C
- Humidity: {result['humidity']}%
- Wind: {result['wind_speed']} km/h"""
        
        elif intent == 'joke':
            if 'joke' in result:
                return f"😄 {result['joke']}"
            else:
                return f"😄 {result['setup']}\n\n{result['delivery']}"
        
        elif intent == 'quote':
            return f'"{result["quote"]}"\n- {result["author"]}'
        
        elif intent == 'fact':
            return f"💡 {result['fact']}"
        
        elif intent == 'advice':
            return f"💭 {result['advice']}"
        
        elif intent == 'activity':
            return f"🎯 {result['activity']} ({result['type']})"
        
        elif intent == 'crypto':
            change = result.get('change_24h', 0)
            change_symbol = "📈" if change > 0 else "📉"
            return f"""💰 {result['coin'].title()} Price:
- USD: ${result['price_usd']:,.2f}
- INR: ₹{result['price_inr']:,.2f}
- 24h Change: {change_symbol} {change:.2f}%"""
        
        elif intent == 'definition':
            example = f"\nExample: {result['example']}" if result.get('example') else ""
            return f"""📖 {result['word']} ({result['part_of_speech']}):
{result['definition']}{example}"""
        
        elif intent == 'search':
            formatted = f"🔍 Search results for '{result['query']}':\n\n"
            for i, r in enumerate(result['results'], 1):
                formatted += f"{i}. **{r['title']}**\n   {r['snippet']}\n   {r['url']}\n\n"
            return formatted.strip()
        
        return str(result)
