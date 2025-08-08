"""Command‑line interface for Mythiq Agent.

This script allows you to query the Mythiq Agent from your terminal.  You can
either pass a single message as a command‑line argument or launch an
interactive session that reads input until you exit.  The agent will
determine which Mythiq microservice to call based on the content of your
message and print the JSON response.
"""

import sys
import json
from typing import Optional

# Import via absolute package to support running as a script
from mythiq_agent.agent import MythiqAgent


def run_once(message: str) -> None:
    """Send a single message to the agent and print the result."""
    agent = MythiqAgent()
    response = agent.process(message)
    print(json.dumps(response, indent=2))


def run_interactive() -> None:
    """Launch an interactive REPL for the Mythiq Agent."""
    agent = MythiqAgent()
    print("Mythiq Agent interactive mode.  Type 'quit' or 'exit' to exit.")
    while True:
        try:
            message = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()  # newline
            break
        if not message:
            continue
        if message.lower() in {"quit", "exit"}:
            break
        response = agent.process(message)
        # Pretty print the result
        print(json.dumps(response, indent=2))


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point for the CLI.

    If any arguments are provided, they are concatenated into a single
    message and sent to the agent.  Otherwise, the interactive REPL is
    started.
    """
    args = argv if argv is not None else sys.argv[1:]
    if args:
        message = " ".join(args)
        run_once(message)
    else:
        run_interactive()


if __name__ == "__main__":
    main()