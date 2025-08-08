"""Service wrappers for Mythiq microservices.

This module defines helper functions that wrap the HTTP API exposed by
Mythiq’s assistant, game maker, media creator, audio creator and video
creator services.  Each function takes the required inputs, constructs
the appropriate JSON payload, sends the request using the `requests`
library and returns a dictionary with either the parsed data or an
error message.

Before using these functions, ensure that the following environment
variables are set (or defined in a `.env` file at the project root):

* `ASSISTANT_URL`
* `GAME_URL`
* `MEDIA_URL`
* `AUDIO_URL`
* `VIDEO_URL`

`load_environment()` reads these variables using `python-dotenv`.
"""

from __future__ import annotations

import os
import json
from typing import Any, Dict, Optional

import requests

try:
    # Attempt to import python-dotenv; this will not raise an error if the
    # package is missing (ImportError) because of the try/except below.
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    load_dotenv = None  # type: ignore


def load_environment() -> None:
    """Load environment variables from a `.env` file if present.

    This function should be called once at the start of your program
    (e.g., in `main.py` or within `MythiqAgent.__init__()`).  It uses
    `python-dotenv` to load variables from a file called `.env` in the
    current working directory.  Environment variables defined by the
    system take precedence.
    """
    if load_dotenv is not None:
        # Use python-dotenv if available; it silently ignores missing files.
        load_dotenv()
    else:
        # Fallback: manually read key=value lines from a .env file if it exists.
        env_path = os.path.join(os.getcwd(), ".env")
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for raw_line in f.read().splitlines():
                        line = raw_line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, value = line.split("=", 1)
                        # Do not overwrite existing environment variables
                        os.environ.setdefault(key.strip(), value.strip())
            except Exception:
                # Ignore any errors reading the .env file
                pass


def _post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Internal helper to send a POST request with JSON and parse the response.

    Returns a dictionary with keys:

    * `success` (bool)
    * `data` (any) – the parsed JSON response if successful
    * `error` (str) – error message if the request failed or returned
      non‑success status code
    """
    try:
        response = requests.post(url, json=payload, timeout=30)
    except Exception as exc:
        return {
            "success": False,
            "error": f"Failed to call {url}: {exc}",
            "data": None,
        }

    if response.status_code >= 200 and response.status_code < 300:
        try:
            data = response.json()
        except Exception:
            return {
                "success": False,
                "error": f"Invalid JSON returned from {url}",
                "data": None,
            }
        return {"success": True, "data": data, "error": None}
    else:
        # Attempt to extract error message from JSON if available
        try:
            err_data = response.json()
            err_msg = err_data.get("message") or err_data.get("error") or response.text
        except Exception:
            err_msg = response.text
        return {
            "success": False,
            "error": f"{url} returned status {response.status_code}: {err_msg}",
            "data": None,
        }


def chat_assistant(message: str) -> Dict[str, Any]:
    """Send a chat message to the Mythiq Assistant service.

    Parameters
    ----------
    message : str
        The user’s message or prompt.

    Returns
    -------
    dict
        A dictionary with keys `success`, `data`, and `error`.  On success,
        `data` contains the JSON response from the assistant service.
    """
    base_url = os.environ.get("ASSISTANT_URL")
    if not base_url:
        return {"success": False, "error": "ASSISTANT_URL is not set", "data": None}
    endpoint = base_url.rstrip("/") + "/chat"
    payload = {"message": message}
    return _post_json(endpoint, payload)


def generate_game(prompt: str) -> Dict[str, Any]:
    """Generate a game from a textual description using the game maker service.

    Parameters
    ----------
    prompt : str
        A description of the game you want to create.

    Returns
    -------
    dict
        A dictionary with `success`, `data` and `error`.  On success,
        `data` will include the generated game metadata, play and download
        URLs (as returned by the backend)【39432226201812†L2591-L2715】.
    """
    base_url = os.environ.get("GAME_URL")
    if not base_url:
        return {"success": False, "error": "GAME_URL is not set", "data": None}
    endpoint = base_url.rstrip("/") + "/generate-game"
    payload = {"prompt": prompt}
    return _post_json(endpoint, payload)


def generate_image(prompt: str) -> Dict[str, Any]:
    """Generate an image from a text prompt using the media creator service.

    Parameters
    ----------
    prompt : str
        A description of the desired image.

    Returns
    -------
    dict
        On success, the returned `data` contains `image_data` (a base64
        encoded PNG), `enhanced_prompt`, `original_prompt` and other
        generation information【602996636764176†L214-L260】.
    """
    base_url = os.environ.get("MEDIA_URL")
    if not base_url:
        return {"success": False, "error": "MEDIA_URL is not set", "data": None}
    endpoint = base_url.rstrip("/") + "/generate-image"
    payload = {"prompt": prompt}
    return _post_json(endpoint, payload)


def generate_speech(text: str, voice_preset: Optional[str] = None) -> Dict[str, Any]:
    """Convert text to speech using the audio creator service.

    Parameters
    ----------
    text : str
        The text to convert to speech.
    voice_preset : str, optional
        A voice preset ID (e.g. `v2/en_speaker_0`).  If omitted, the
        backend’s default voice will be used.

    Returns
    -------
    dict
        The `data` field contains `audio_data` (base64 encoded WAV) and
        `generation_info` such as duration and sample rate【222645300190768†L322-L335】.
    """
    base_url = os.environ.get("AUDIO_URL")
    if not base_url:
        return {"success": False, "error": "AUDIO_URL is not set", "data": None}
    endpoint = base_url.rstrip("/") + "/generate-speech"
    payload: Dict[str, Any] = {"text": text}
    if voice_preset:
        payload["voice_preset"] = voice_preset
    return _post_json(endpoint, payload)


def generate_music(prompt: str, duration: int = 30) -> Dict[str, Any]:
    """Compose a music clip using the audio creator service.

    Parameters
    ----------
    prompt : str
        A short description of the desired music (e.g. “ambient chill”).
    duration : int, optional
        Length of the composition in seconds (default: 30).

    Returns
    -------
    dict
        On success, `data` contains `audio_data` (base64) and other
        generation details such as style and sample rate【222645300190768†L503-L516】.
    """
    base_url = os.environ.get("AUDIO_URL")
    if not base_url:
        return {"success": False, "error": "AUDIO_URL is not set", "data": None}
    endpoint = base_url.rstrip("/") + "/generate-music"
    payload = {"prompt": prompt, "duration": duration}
    return _post_json(endpoint, payload)


def generate_video(prompt: str, duration: int = 10) -> Dict[str, Any]:
    """Generate a video concept using the video creator service.

    Parameters
    ----------
    prompt : str
        A description of the desired video content.
    duration : int, optional
        Requested duration in seconds.  Some backends may ignore this
        parameter if they only produce fixed‑length clips.

    Returns
    -------
    dict
        On success, `data` contains `video_data` (with URL and
        thumbnail) and `generation_info`【609355187556678†L145-L168】.
    """
    base_url = os.environ.get("VIDEO_URL")
    if not base_url:
        return {"success": False, "error": "VIDEO_URL is not set", "data": None}
    endpoint = base_url.rstrip("/") + "/generate-video"
    payload = {"prompt": prompt, "duration": duration}
    return _post_json(endpoint, payload)
