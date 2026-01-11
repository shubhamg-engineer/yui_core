#!/usr/bin/env python3
"""
Yui - AI Companion Core System
Phase 1: Basic Conversation Engine
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from config.config import Config
from core.conversation import ConversationManager

console = Console()

def display_welcome():
    """Display welcome message"""
    welcome_text = f"""
# 🌙 Welcome to Project Yui

**Version:** 0.1.0 (Phase 1 - Foundation)
**Current Personality:** {Config.DEFAULT_PERSONALITY.title()}

Type your message and press Enter to chat.

**Commands:**
- `/quit` or `/exit` - Exit the program
- `/clear` - Clear conversation history
- `/switch <name>` - Switch personality (yui, friday, jarvis)
- `/help` - Show this help message
- `/info` - Show conversation info

---
"""
    console.print(Markdown(welcome_text))

def display_help():
    """Display help information"""
    help_text = """
# 📖 Yui Commands

**Chat Commands:**
- `/quit`, `/exit` - Exit Yui
- `/clear` - Clear conversation history
- `/switch <personality>` - Switch between personalities
  - Available: yui, friday, jarvis
- `/info` - Show conversation statistics
- `/help` - Show this help

**Tips:**
- Just type naturally - Yui will remember your conversation
- Ask questions, share thoughts, or just chat
- Yui adapts to your emotional state and needs
"""
    console.print(Markdown(help_text))

def main():
    """Main application loop"""
    
    try:
        # Display welcome message
        display_welcome()
        
        # Get user name
        user_name = Prompt.ask("What's your name?", default="Friend")
        console.print(f"\n✨ Nice to meet you, {user_name}!\n")
        
        # Initialize conversation manager
        conversation = ConversationManager(
            personality_name=Config.DEFAULT_PERSONALITY,
            user_name=user_name
        )
        
        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask(f"\n[bold cyan]{user_name}[/bold cyan]")
                
                # Skip empty inputs
                if not user_input.strip():
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    command = user_input.lower().strip()
                    
                    if command in ['/quit', '/exit']:
                        console.print("\n👋 Goodbye! Come back soon.\n")
                        break
                    
                    elif command == '/clear':
                        conversation.clear_history()
                        continue
                    
                    elif command.startswith('/switch'):
                        parts = command.split()
                        if len(parts) > 1:
                            personality_name = parts[1]
                            try:
                                conversation.switch_personality(personality_name)
                            except Exception as e:
                                console.print(f"[red]Error: {e}[/red]")
                        else:
                            console.print("[yellow]Usage: /switch <personality>[/yellow]")
                            console.print("Available: yui, friday, jarvis")
                        continue
                    
                    elif command == '/help':
                        display_help()
                        continue
                    
                    elif command == '/info':
                        console.print(conversation.get_conversation_summary())
                        continue
                    
                    else:
                        console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")
                        continue
                
                # Send message and get response
                console.print(f"\n[bold magenta]{conversation.personality.name}[/bold magenta] is thinking...")
                
                response = conversation.send_message(user_input)
                
                # Display response in a panel
                console.print(
                    Panel(
                        response,
                        title=f"[bold magenta]{conversation.personality.name}[/bold magenta]",
                        border_style="magenta"
                    )
                )
                
            except KeyboardInterrupt:
                console.print("\n\n👋 Interrupted. Goodbye!\n")
                break
            
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]\n")
                console.print("[yellow]Type /help for commands or /quit to exit.[/yellow]")
    
    except Exception as e:
        console.print(f"\n[bold red]Fatal Error:[/bold red] {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()