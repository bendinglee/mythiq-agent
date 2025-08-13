"""
Command-line interface for Mythiq Agent.

This script allows you to query the Mythiq Agent from your terminal. You can
either pass a single message as a command-line argument or launch an
interactive session that reads input until you exit. The agent will
determine which Mythiq microservice to call based on the content of your
message and print the JSON response.
"""

import sys
import json
from typing import Optional
from mythiq_agent.agent import MythiqAgent

def run_once(message: str) -> None:
    """Send a single message to the agent and print the result."""
    agent = MythiqAgent()
    response = agent.process(message)
    print(json.dumps(response, indent=2))

def run_interactive() -> None:
    """Launch an interactive REPL for the Mythiq Agent."""
    agent = MythiqAgent()
    print("Mythiq Agent interactive mode. Type 'quit' or 'exit' to exit.")
    
    while True:
        try:
            message = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()  # newline
            break
            
        if not message:
            continue
            
        if message.lower() in ["quit", "exit"]:
            break
            
        try:
            response = agent.process(message)
            print(json.dumps(response, indent=2))
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    """Main entry point for the CLI."""
    if len(sys.argv) > 1:
        # Command-line mode: process the argument as a single message
        message = " ".join(sys.argv[1:])
        run_once(message)
    else:
        # Interactive mode
        run_interactive()

if __name__ == "__main__":
    main()

