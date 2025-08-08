# Mythiq Agent

Mythiq Agent is a Python‑based client for the Mythiq creative platform.  It
provides a unified interface that can talk to the existing Mythiq microservices
— game maker, audio creator, media creator, video creator and AI assistant —
and exposes a simple “agent” capable of routing requests to the right
service.

## Motivation

Mythiq offers separate endpoints for chat, game generation, image creation,
music composition, speech synthesis and video concept generation, but there
is no single entry point that orchestrates these capabilities.  This project
demonstrates how to build an “agent mode” on top of those services: it
takes user input, decides which service to call based on keywords, sends
the request to the appropriate API and returns a consolidated response.  With
proper configuration, the agent can be used from a command‑line interface
or integrated into a larger application.

## Features

* **Chat** with the Mythiq Assistant using Groq’s Llama 3.1 model, with
  automatic fallback to HuggingFace’s DialoGPT when Groq is unavailable【33637396242431†L90-L205】.
* **Game Generation** via the Mythiq Game Maker service.  The agent sends
  your description to `/generate-game` and returns play and download
  URLs along with the generated game’s metadata【39432226201812†L2591-L2715】.
* **Image Creation** using the Media Creator’s `/generate-image` endpoint.
  The service returns a base64‑encoded image along with the original and
  enhanced prompts and generation details【602996636764176†L214-L260】.
* **Music Composition** and **Speech Synthesis** via the Audio Creator.
  The agent supports both `/generate-music` and `/generate-speech` and
  returns base64 audio data, sample rate and other generation info【222645300190768†L322-L335】【222645300190768†L503-L516】.
* **Video Concepts** via the Video Creator.  The agent calls
  `/generate-video` and returns a placeholder URL, thumbnail and
  metadata【609355187556678†L145-L168】.

## Repository layout

* `services.py` – Thin wrapper functions around each Mythiq service.  Each
  function prepares the JSON payload, sends the HTTP request and returns
  the parsed response or a structured error.
* `agent.py` – Contains the `MythiqAgent` class.  It implements a simple
  keyword‑based router that decides which service to call based on the
  user’s message.  If none of the keywords match, it falls back to the
  assistant chat.
* `main.py` – A command‑line interface and interactive REPL that lets you
  talk to the agent.  It reads the user’s input, passes it to
  `MythiqAgent.process()` and prints the response.  You can use this as
  a starting point for your own application.
* `requirements.txt` – Python dependencies.  Only `requests` and
  `python-dotenv` are required.  If you plan to persist configuration
  across environments, you can also add `click` or other libraries.

## Installation

Clone the repository and install the dependencies:

```bash
git clone <your fork of this repo>
cd mythiq_agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Set the base URLs for each Mythiq microservice in your environment.  The
agent uses these variables to construct requests:

* `ASSISTANT_URL` – Base URL of the Mythiq Assistant (e.g.
  `https://mythiq-assistant-production.up.railway.app`).
* `GAME_URL` – Base URL of the Mythiq Game Maker (e.g.
  `https://mythiq-game-maker-production.up.railway.app`).
* `MEDIA_URL` – Base URL of the Mythiq Media Creator (for images).
* `AUDIO_URL` – Base URL of the Mythiq Audio Creator (for speech and music).
* `VIDEO_URL` – Base URL of the Mythiq Video Creator.

You can define these variables in a `.env` file at the project root (see
`example.env` below) or export them in your shell before running the
application.  The agent loads `.env` automatically if present.

Example `.env`:

```
ASSISTANT_URL=https://mythiq-assistant-production.up.railway.app
GAME_URL=https://mythiq-game-maker-production.up.railway.app
MEDIA_URL=https://mythiq-media-creator-production.up.railway.app
AUDIO_URL=https://mythiq-audio-creator-production.up.railway.app
VIDEO_URL=https://mythiq-video-creator-production.up.railway.app
```

## Usage

### Command‑line

Run the agent from the command line by passing your query as an argument:

```bash
python main.py "Create an underwater puzzle game"
```

Alternatively, launch the interactive REPL:

```bash
python main.py
```

In interactive mode, simply type your requests.  Enter `quit` or `exit` to
terminate.

### Programmatic use

Import the `MythiqAgent` class and call `process()` directly:

```python
from mythiq_agent.agent import MythiqAgent

agent = MythiqAgent()
response = agent.process("generate a calming ambient music piece")
print(response)
```

`process()` returns a dictionary with at least two keys:

* `service`: The name of the service called (`assistant`, `game`, `image`,
  `music`, `speech`, `video`).
* `result`: The JSON response from the microservice or a structured error
  message.

## Limitations

* This repository does not provide its own AI models.  It merely forwards
  requests to the existing Mythiq services and aggregates their responses.
* The keyword router is intentionally simple and may misclassify requests
  that contain ambiguous terms.  Consider integrating a proper natural
  language understanding component for more robust intent detection.
* The agent does not persist conversation context across calls.  If you
  require conversation memory, extend the `MythiqAgent` class to store and
  pass context to the assistant service.

## Future improvements

* Add authentication support if the Mythiq services are secured.
* Integrate streaming responses for long‑running operations like music
  generation.
* Extend the router with a lightweight NLP model to better classify user
  intents and parameters.
