import requests
from typing import List, Dict, Optional
from config.config import Config

class LLMEngine:
    """
    Wrapper for FREE LLM APIs
    Supports: Groq, Hugging Face, Google Gemini, Ollama (local)
    """
    
    def __init__(self, provider: str = "groq", model: str = None):
        """
        Initialize LLM Engine
        
        Args:
            provider: "groq", "huggingface", "gemini", "ollama", "cohere"
            model: Specific model name (optional)
        """
        self.provider = provider.lower()
        self.model = model or self._get_default_model()
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        
        print(f"✓ Using {self.provider} with model: {self.model}")
    
    def _get_default_model(self) -> str:
        """Get default model for each provider"""
        defaults = {
            "groq": "llama3-70b-8192",
            "huggingface": "mistralai/Mistral-7B-Instruct-v0.2",
            "gemini": "gemini-2.0-flash",
            "ollama": "llama3",
            "cohere": "command"
        }
        return defaults.get(self.provider, "llama3-70b-8192")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from config"""
        key_map = {
            "groq": Config.GROQ_API_KEY,
            "huggingface": Config.HUGGINGFACE_API_KEY,
            "gemini": Config.GEMINI_API_KEY,
            "cohere": Config.COHERE_API_KEY,
            "ollama": None  # Local, no key needed
        }
        return key_map.get(self.provider)
    
    def _get_base_url(self) -> str:
        """Get base URL for each provider"""
        urls = {
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "huggingface": "https://api-inference.huggingface.co/models",
            "gemini": "https://generativelanguage.googleapis.com/v1/models",
            "ollama": "http://localhost:11434/api/chat",
            "cohere": "https://api.cohere.ai/v1/chat"
        }
        return urls.get(self.provider)
    
    def generate(self, messages: List[Dict], system_prompt: str = None, temperature: float = 0.7) -> str:
        """
        Generate response from LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System prompt to set behavior
            temperature: Creativity (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == "groq":
                return self._generate_groq(messages, system_prompt, temperature)
            elif self.provider == "huggingface":
                return self._generate_huggingface(messages, system_prompt, temperature)
            elif self.provider == "gemini":
                return self._generate_gemini(messages, system_prompt, temperature)
            elif self.provider == "ollama":
                return self._generate_ollama(messages, system_prompt, temperature)
            elif self.provider == "cohere":
                return self._generate_cohere(messages, system_prompt, temperature)
            else:
                return "Error: Unsupported provider"
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _generate_groq(self, messages: List[Dict], system_prompt: str, temperature: float) -> str:
        """Generate using Groq API (OpenAI compatible)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Add system prompt if provided
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            
            # Better error handling
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                except:
                    error_msg = response.text[:200]
                
                return f"Groq API Error ({response.status_code}): {error_msg}"
            
            return response.json()["choices"][0]["message"]["content"]
        
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Check your internet connection."
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except KeyError as e:
            return f"Error parsing Groq response: Missing key {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _generate_huggingface(self, messages: List[Dict], system_prompt: str, temperature: float) -> str:
        """Generate using Hugging Face Inference API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format as single prompt
        prompt = ""
        if system_prompt:
            prompt += f"<s>[INST] {system_prompt}\n\n"
        
        for msg in messages:
            if msg["role"] == "user":
                prompt += f"{msg['content']} [/INST]"
            elif msg["role"] == "assistant":
                prompt += f" {msg['content']} </s><s>[INST] "
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        
        try:
            url = f"{self.base_url}/{self.model}"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                except:
                    error_msg = response.text[:200]
                
                return f"HuggingFace API Error ({response.status_code}): {error_msg}"
            
            result = response.json()
            if isinstance(result, list):
                return result[0]["generated_text"]
            return result["generated_text"]
        
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Check your internet connection."
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except KeyError as e:
            return f"Error parsing HuggingFace response: Missing key {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _generate_gemini(self, messages: List[Dict], system_prompt: str, temperature: float) -> str:
        """Generate using Google Gemini API"""
        # Gemini 1.5 models require v1beta
        version = "v1beta" if "1.5" in self.model else "v1"
        url = f"https://generativelanguage.googleapis.com/{version}/models/{self.model}:generateContent?key={self.api_key}"
        
        # Format messages for Gemini
        contents = []
        
        # Add system prompt as first user message
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": system_prompt}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. I'll follow these guidelines."}]
            })
        
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            # Better error handling
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                except:
                    error_msg = response.text[:200]
                
                return f"Gemini API Error ({response.status_code}): {error_msg}"
            
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Check your internet connection."
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except KeyError as e:
            return f"Error parsing Gemini response: Missing key {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _generate_ollama(self, messages: List[Dict], system_prompt: str, temperature: float) -> str:
        """Generate using Ollama (local)"""
        # Add system prompt to messages
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": full_messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=60)
            
            if response.status_code != 200:
                return f"Ollama Error ({response.status_code}): Is Ollama running? Start it with: ollama serve"
            
            return response.json()["message"]["content"]
        
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Ollama might be processing a large model."
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except KeyError as e:
            return f"Error parsing Ollama response: Missing key {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _generate_cohere(self, messages: List[Dict], system_prompt: str, temperature: float) -> str:
        """Generate using Cohere API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Get last user message
        user_message = messages[-1]["content"] if messages else ""
        
        # Format chat history
        chat_history = []
        for msg in messages[:-1]:
            chat_history.append({
                "role": "USER" if msg["role"] == "user" else "CHATBOT",
                "message": msg["content"]
            })
        
        payload = {
            "model": self.model,
            "message": user_message,
            "chat_history": chat_history,
            "preamble": system_prompt,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                except:
                    error_msg = response.text[:200]
                
                return f"Cohere API Error ({response.status_code}): {error_msg}"
            
            return response.json()["text"]
        
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Check your internet connection."
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except KeyError as e:
            return f"Error parsing Cohere response: Missing key {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def stream_generate(self, messages: List[Dict], system_prompt: str = None):
        """
        Stream response from LLM (for future voice integration)
        Currently only supported for Groq
        """
        if self.provider == "groq":
            # Groq supports streaming
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)
            
            payload = {
                "model": self.model,
                "messages": full_messages,
                "stream": True
            }
            
            try:
                response = requests.post(self.base_url, json=payload, headers=headers, stream=True, timeout=30)
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data != '[DONE]':
                                import json
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
            except Exception as e:
                yield f"Streaming error: {str(e)}"
        else:
            # Fallback to regular generation
            response = self.generate(messages, system_prompt)
            yield response