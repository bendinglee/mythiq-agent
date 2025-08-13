import os
import time
import logging
from datetime import datetime
import psutil
from flask import Flask, request, jsonify
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mythiq")

# Try to import the real MythiqAgent; fall back to a stub if missing
try:
    from mythiq_agent import MythiqAgent  # your real implementation
    mythiq_agent = MythiqAgent()
    AGENT_SOURCE = "real"
except Exception as e:
    logger.warning(f"Using stub MythiqAgent (import failed: {e})")
    AGENT_SOURCE = "stub"

    class MythiqAgent:
        def process(self, message: str, context=None):
            reply = (
                "Mythiq (stub): I hear you. "
                "For a full experience, enable providers or install the real agent."
            )
            return {"message": message, "reply": reply, "context": context}

        def get_capabilities(self):
            return {
                "chat": True,
                "summarize": True,
                "providers": ["local"],
                "notes": "Stub agent; no external providers enabled."
            }

    mythiq_agent = MythiqAgent()

app = Flask(__name__)
CORS(app)

START_TIME = time.time()

@app.route("/health", methods=["GET"])
def health():
    try:
        system_info = {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": round(time.time() - START_TIME, 3),
            "memory_usage_percent": psutil.virtual_memory().percent,
            "cpu_usage_percent": psutil.cpu_percent(interval=0.1),
            "agent_source": AGENT_SOURCE,
        }
        # Keep this endpoint pure: no network calls, no heavy work
        return jsonify(system_info), 200
    except Exception as e:
        logger.exception("Health check failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "name": "Mythiq Agent API",
        "version": "2.0.0",
        "description": "Enhanced AI agent (paid providers disabled).",
        "endpoints": {
            "/health": "Health check",
            "/chat": "Chat with Mythiq (local/stub)",
            "/process": "Process request through Mythiq Agent",
            "/capabilities": "Get agent capabilities",
            "/providers": "Get provider status"
        }
    }), 200

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message")
        context = data.get("context")
        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Simple local reply to keep things functional without paid APIs
        result = mythiq_agent.process(message, context)
        reply = result.get("reply") if isinstance(result, dict) else str(result)

        return jsonify({
            "response": reply,
            "provider": "local",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 200
    except Exception as e:
        logger.exception("Chat endpoint error")
        return jsonify({"error": str(e)}), 500

@app.route("/process", methods=["POST"])
def process_request():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message")
        context = data.get("context")
        if not message:
            return jsonify({"error": "Message is required"}), 400

        result = mythiq_agent.process(message, context)
        return jsonify({
            "result": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 200
    except Exception as e:
        logger.exception("Process endpoint error")
        return jsonify({"error": str(e)}), 500

@app.route("/capabilities", methods=["GET"])
def get_capabilities():
    try:
        return jsonify(mythiq_agent.get_capabilities()), 200
    except Exception as e:
        logger.exception("Capabilities endpoint error")
        return jsonify({"error": str(e)}), 500

@app.route("/providers", methods=["GET"])
def get_providers():
    # Paid providers disabled; report local only
    return jsonify({
        "local": {
            "name": "local",
            "capabilities": ["chat", "summarize"],
            "priority": 1,
            "status": "healthy",
            "has_api_key": False,
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
