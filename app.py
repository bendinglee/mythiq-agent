"""
Enhanced Mythiq Agent Backend with Multi-API Integration
Version: 2.0 - Multi-Provider AI Ecosystem

This enhanced backend implements intelligent routing across multiple AI providers
with fallback mechanisms, load balancing, and comprehensive error handling.
"""

import os
import json
import time
import asyncio
import aiohttp
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog
import psutil
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import httpx
from groq import Groq
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"

@dataclass
class RequestType(Enum):
    CHAT = "chat"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    GAME = "game"
    TRANSLATION = "translation"

@dataclass
class ProviderConfig:
    name: str
    api_key_env: str
    base_url: str
    endpoints: Dict[str, str] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)  # requests per minute
    capabilities: List[RequestType] = field(default_factory=list)
    priority: int = 1  # Lower number = higher priority
    timeout: int = 30
    max_retries: int = 3

@dataclass
class ProviderHealth:
    status: ProviderStatus = field(default_factory=lambda: ProviderStatus.HEALTHY)
    last_check: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0
    error_count: int = 0
    success_count: int = 0
    rate_limit_reset: Optional[datetime] = None
    consecutive_failures: int = 0

class AIProviderManager:
    """Manages multiple AI providers with intelligent routing and fallback"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.health_status = {name: ProviderHealth() for name in self.providers.keys()}
        self.request_history = {}
        self.circuit_breaker_timeout = 300  # 5 minutes before retry
        
    def _initialize_providers(self) -> Dict[str, ProviderConfig]:
        """Initialize all supported AI providers"""
        return {
            "groq": ProviderConfig(
                name="groq",
                api_key_env="GROQ_API_KEY",
                base_url="https://api.groq.com/openai/v1",
                endpoints={
                    "chat": "/chat/completions"
                },
                rate_limits={"chat": 100},  # requests per minute
                capabilities=[RequestType.CHAT],
                priority=1
            ),
            "openrouter": ProviderConfig(
                name="openrouter",
                api_key_env="OPENROUTER_API_KEY", 
                base_url="https://openrouter.ai/api/v1",
                endpoints={
                    "chat": "/chat/completions"
                },
                rate_limits={"chat": 200},
                capabilities=[RequestType.CHAT],
                priority=2
            ),
            "together": ProviderConfig(
                name="together",
                api_key_env="TOGETHER_API_KEY",
                base_url="https://api.together.xyz/v1",
                endpoints={
                    "chat": "/chat/completions",
                    "image": "/images/generations"
                },
                rate_limits={"chat": 150, "image": 50},
                capabilities=[RequestType.CHAT, RequestType.IMAGE],
                priority=3
            )
        }
    
    def get_healthy_providers(self, capability: RequestType) -> List[Tuple[str, ProviderConfig]]:
        """Get list of healthy providers for a specific capability, sorted by priority"""
        healthy_providers = []
        
        for name, config in self.providers.items():
            if capability in config.capabilities:
                health = self.health_status[name]
                if health.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]:
                    healthy_providers.append((name, config))
        
        # Sort by priority (lower number = higher priority)
        return sorted(healthy_providers, key=lambda x: x[1].priority)
    
    async def check_provider_health(self, provider_name: str) -> ProviderHealth:
        """Check health of a specific provider"""
        config = self.providers[provider_name]
        health = self.health_status[provider_name]
        
        try:
            start_time = time.time()
            
            # Simple health check - try to make a minimal request
            api_key = os.getenv(config.api_key_env)
            if not api_key:
                health.status = ProviderStatus.FAILED
                return health
            
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {api_key}"}
                async with session.get(
                    f"{config.base_url}/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        health.status = ProviderStatus.HEALTHY
                        health.success_count += 1
                        health.consecutive_failures = 0
                    elif response.status == 429:
                        health.status = ProviderStatus.RATE_LIMITED
                        health.rate_limit_reset = datetime.now() + timedelta(minutes=5)
                    else:
                        health.status = ProviderStatus.DEGRADED
                        health.error_count += 1
                        health.consecutive_failures += 1
                    
                    health.response_time = response_time
                    health.last_check = datetime.now()
        
        except Exception as e:
            health.status = ProviderStatus.FAILED
            health.error_count += 1
            health.consecutive_failures += 1
            health.last_check = datetime.now()
            logger.error(f"Health check failed for {provider_name}: {str(e)}")
        
        return health

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize AI Provider Manager
ai_manager = AIProviderManager()

# Import Mythiq Agent
from mythiq_agent import MythiqAgent

# Initialize Mythiq Agent
mythiq_agent = MythiqAgent()

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for deployment platforms"""
    try:
        # Basic health check
        system_info = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time(),
            "memory_usage": psutil.virtual_memory().percent,
            "cpu_usage": psutil.cpu_percent()
        }
        
        # Check AI providers health
        provider_health = {}
        for name in ai_manager.providers.keys():
            health = ai_manager.health_status[name]
            provider_health[name] = {
                "status": health.status.value,
                "last_check": health.last_check.isoformat(),
                "response_time": health.response_time,
                "error_count": health.error_count,
                "success_count": health.success_count
            }
        
        return jsonify({
            "system": system_info,
            "providers": provider_health
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "name": "Mythiq Agent API",
        "version": "2.0.0",
        "description": "Enhanced AI agent with multi-provider routing and Mythiq service integration",
        "endpoints": {
            "/health": "Health check",
            "/chat": "Chat with AI assistant",
            "/process": "Process request through Mythiq Agent",
            "/capabilities": "Get agent capabilities",
            "/providers": "Get provider status"
        }
    })

@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint with multi-provider fallback"""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data["message"]
        context = data.get("context", "")
        
        # Get healthy providers for chat
        healthy_providers = ai_manager.get_healthy_providers(RequestType.CHAT)
        
        if not healthy_providers:
            return jsonify({"error": "No healthy chat providers available"}), 503
        
        # Try providers in order of priority
        for provider_name, config in healthy_providers:
            try:
                api_key = os.getenv(config.api_key_env)
                if not api_key:
                    continue
                
                # Make chat request
                if provider_name == "groq":
                    client = Groq(api_key=api_key)
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[
                            {"role": "system", "content": "You are a helpful AI assistant."},
                            {"role": "user", "content": message}
                        ],
                        max_tokens=1000
                    )
                    result = response.choices[0].message.content
                    
                elif provider_name in ["openrouter", "together"]:
                    client = openai.OpenAI(
                        api_key=api_key,
                        base_url=config.base_url
                    )
                    response = client.chat.completions.create(
                        model="meta-llama/llama-3.1-8b-instruct:free" if provider_name == "openrouter" else "meta-llama/Llama-2-7b-chat-hf",
                        messages=[
                            {"role": "system", "content": "You are a helpful AI assistant."},
                            {"role": "user", "content": message}
                        ],
                        max_tokens=1000
                    )
                    result = response.choices[0].message.content
                
                # Update provider health on success
                health = ai_manager.health_status[provider_name]
                health.success_count += 1
                health.consecutive_failures = 0
                
                return jsonify({
                    "response": result,
                    "provider": provider_name,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Chat failed with {provider_name}: {str(e)}")
                # Update provider health on failure
                health = ai_manager.health_status[provider_name]
                health.error_count += 1
                health.consecutive_failures += 1
                continue
        
        return jsonify({"error": "All chat providers failed"}), 503
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/process", methods=["POST"])
def process_request():
    """Process request through Mythiq Agent"""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data["message"]
        context = data.get("context")
        
        # Process through Mythiq Agent
        result = mythiq_agent.process(message, context)
        
        return jsonify({
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Process endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/capabilities", methods=["GET"])
def get_capabilities():
    """Get agent capabilities"""
    try:
        capabilities = mythiq_agent.get_capabilities()
        return jsonify(capabilities)
    except Exception as e:
        logger.error(f"Capabilities endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/providers", methods=["GET"])
def get_providers():
    """Get provider status and configuration"""
    try:
        provider_info = {}
        
        for name, config in ai_manager.providers.items():
            health = ai_manager.health_status[name]
            provider_info[name] = {
                "name": config.name,
                "capabilities": [cap.value for cap in config.capabilities],
                "priority": config.priority,
                "status": health.status.value,
                "last_check": health.last_check.isoformat(),
                "response_time": health.response_time,
                "error_count": health.error_count,
                "success_count": health.success_count,
                "has_api_key": bool(os.getenv(config.api_key_env))
            }
        
        return jsonify(provider_info)
        
    except Exception as e:
        logger.error(f"Providers endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Mythiq Agent API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

