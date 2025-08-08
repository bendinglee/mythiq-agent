"""
Flask web server wrapper for Mythiq Agent
Converts the CLI agent into a REST API for Railway deployment
"""

import os
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from mythiq_agent.agent import MythiqAgent

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize the agent
agent = MythiqAgent()

@app.route('/')
def home():
    """Health check and API documentation"""
    return render_template_string('''
    <h1>Mythiq Agent API</h1>
    <p>Status: <span style="color: green;">✅ Running</span></p>
    <h2>Endpoints:</h2>
    <ul>
        <li><code>GET /</code> - This page</li>
        <li><code>GET /health</code> - Health check</li>
        <li><code>POST /process</code> - Process user message</li>
        <li><code>POST /chat</code> - Chat with AI Assistant</li>
    </ul>
    <h2>Usage:</h2>
    <pre>
POST /process
{
    "message": "Create a puzzle game"
}

POST /chat  
{
    "message": "Hello, how are you?"
}
    </pre>
    ''')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "mythiq-agent",
        "version": "1.0.0"
    })

@app.route('/process', methods=['POST'])
def process_message():
    """Main endpoint for processing user messages"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' field in request body"
            }), 400
        
        message = data['message']
        response = agent.process(message)
        
        return jsonify({
            "success": True,
            "request": message,
            "response": response
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Dedicated chat endpoint for AI Assistant"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' field in request body"
            }), 400
        
        message = data['message']
        # Force chat mode by ensuring no keywords trigger other services
        response = agent.process(message)
        
        # Extract just the assistant response if it's a chat
        if response.get('service') == 'assistant':
            return jsonify({
                "success": True,
                "message": response.get('result', {}).get('response', 'No response'),
                "service": "assistant"
            })
        else:
            # If it triggered another service, still return the result
            return jsonify({
                "success": True,
                "response": response
            })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Railway provides PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Mythiq Agent API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
