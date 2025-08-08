"""High‑level agent that routes user requests to appropriate Mythiq services.

The `MythiqAgent` class encapsulates the logic for deciding which
microservice to call based on a free‑form user message.  It uses
keyword matching to select the service: messages containing words like
“game” or “play” are routed to the game generator, those mentioning
“image” or “picture” go to the image generator, and so on.  If no
keyword matches, the agent defaults to chat with the Mythiq assistant.

This module depends on the service wrapper functions defined in
`services.py`.  See `services.py` and the project README for details
about the underlying API calls and configuration.
"""

from __future__ import annotations

import re
from typing import Dict, Any

# Use absolute import to allow execution via `python mythiq_agent/main.py`
import mythiq_agent.services as services


class MythiqAgent:
    """A simple router for Mythiq’s microservices.

    The agent uses lists of keywords to map user messages to API calls.  You
    can modify `KEYWORDS` to support additional phrases or languages.  If
    multiple categories match, the first match in the order defined
    (image, game, music, speech, video, assistant) is used.
    """

    # Mapping of service name to list of keyword patterns.  Patterns are
    # lower‑case and may include simple regular expressions.  The agent
    # searches for these patterns in the user’s message.  Order matters:
    # earlier entries have higher priority.
    KEYWORDS = [
        ("image", [r"\bimage\b", r"\bpicture\b", r"\bphoto\b", r"\bgenerate\s+an?\s+image\b"]),
        ("game", [r"\bgame\b", r"\bplay\b", r"\bcreate\s+an?\s+game\b", r"\bgenerate\s+an?\s+game\b"]),
        ("music", [r"\bmusic\b", r"\bsong\b", r"\bmelody\b", r"\bcompose\b"]),
        ("speech", [r"\bspeech\b", r"\bvoice\b", r"\bsay\b", r"\bspeak\b", r"\btext to speech\b"]),
        ("video", [r"\bvideo\b", r"\banimation\b", r"\bfilm\b", r"\bgenerate\s+an?\s+video\b"]),
    ]

    def __init__(self) -> None:
        # Load environment variables from .env on initialization
        services.load_environment()

    def process(self, message: str) -> Dict[str, Any]:
        """Process a user message and call the appropriate service.

        Parameters
        ----------
        message : str
            A free‑form user message or request.

        Returns
        -------
        dict
            Contains the name of the service called (`service`) and the
            result from the service function (`result`).  If no service
            matches, `service` will be `'assistant'` and the result
            will be the assistant’s response.
        """
        text = message.strip().lower()

        # Determine which service to call based on keywords
        for service_name, patterns in self.KEYWORDS:
            for pattern in patterns:
                if re.search(pattern, text):
                    return self._call_service(service_name, message)

        # Default to assistant
        return self._call_service("assistant", message)

    def _call_service(self, service_name: str, message: str) -> Dict[str, Any]:
        """Call the underlying service based on the detected intent.

        Parameters
        ----------
        service_name : str
            One of `image`, `game`, `music`, `speech`, `video`, `assistant`.
        message : str
            The original user message.

        Returns
        -------
        dict
            A dictionary with keys `service` and `result`.  `result` is
            whatever the corresponding service wrapper returns.
        """
        if service_name == "image":
            result = services.generate_image(message)
        elif service_name == "game":
            result = services.generate_game(message)
        elif service_name == "music":
            # Default duration to 30 seconds.  You could parse numbers
            # from the message to set a custom length.
            result = services.generate_music(message, duration=30)
        elif service_name == "speech":
            result = services.generate_speech(message)
        elif service_name == "video":
            result = services.generate_video(message, duration=10)
        else:
            # Fall back to chat assistant
            result = services.chat_assistant(message)

        return {"service": service_name, "result": result}
