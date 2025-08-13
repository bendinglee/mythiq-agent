# Mythiq Agent

Mythiq Agent is a Python-based client for the Mythiq creative platform. It provides a unified interface that can talk to the existing Mythiq microservices — game maker, audio creator, media creator, video creator and AI assistant — and exposes a simple "agent" capable of routing requests to the right service.

## Features

- **Multi-Provider AI Integration**: Supports Groq, OpenRouter, and Together AI with intelligent fallback
- **Health Monitoring**: Real-time provider health checks and circuit breaker patterns
- **Intelligent Routing**: Keyword-based routing to appropriate Mythiq services
- **Chat**: AI assistant with multi-provider fallback for high availability
- **Game Generation**: Create games via Mythiq Game Maker service
- **Image Creation**: Generate images using Media Creator
- **Music Composition**: Create music via Audio Creator
- **Speech Synthesis**: Text-to-speech via Audio Creator
- **Video Concepts**: Generate video concepts via Video Creator
- **RESTful API**: Complete Flask API with comprehensive endpoints
- **Health Checks**: Built-in health monitoring for deployment platforms

## Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd mythiq-agent
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and service URLs
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Test the Health Endpoint**
   ```bash
   curl http://localhost:8000/health
   ```

### Docker Deployment

1. **Build the Image**
   ```bash
   docker build -t mythiq-agent .
   ```

2. **Run the Container**
   ```bash
   docker run -p 8000:8000 --env-file .env mythiq-agent
   ```

### Railway Deployment

1. **Connect Repository**
   - Connect your GitHub repository to Railway
   - Railway will automatically detect the `railway.toml` configuration

2. **Set Environment Variables**
   In Railway dashboard, set these environment variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   TOGETHER_API_KEY=your_together_api_key
   ASSISTANT_URL=https://mythiq-assistant-production.up.railway.app
   GAME_URL=https://mythiq-game-maker-production.up.railway.app
   MEDIA_URL=https://mythiq-media-creator-production.up.railway.app
   AUDIO_URL=https://mythiq-audio-creator-production.up.railway.app
   VIDEO_URL=https://mythiq-video-creator-production.up.railway.app
   ```

3. **Deploy**
   - Railway will automatically build and deploy your application
   - Health checks are configured to ensure successful deployment

## API Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check with system and provider status
- `POST /chat` - Chat with AI assistant (multi-provider fallback)
- `POST /process` - Process request through Mythiq Agent routing
- `GET /capabilities` - Get agent capabilities and supported services
- `GET /providers` - Get AI provider status and configuration

### Example Usage

**Chat with AI Assistant:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

**Process through Mythiq Agent:**
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a puzzle game about space exploration"}'
```

**Check Provider Status:**
```bash
curl http://localhost:8000/providers
```

## Command Line Interface

### Interactive Mode
```bash
python main.py
```

### Single Command Mode
```bash
python main.py "Create an underwater puzzle game"
```

## Configuration

### Required Environment Variables

**AI Provider API Keys:**
- `GROQ_API_KEY` - Groq API key for Llama models
- `OPENROUTER_API_KEY` - OpenRouter API key for various models
- `TOGETHER_API_KEY` - Together AI API key

**Mythiq Service URLs:**
- `ASSISTANT_URL` - Mythiq Assistant service URL
- `GAME_URL` - Mythiq Game Maker service URL
- `MEDIA_URL` - Mythiq Media Creator service URL
- `AUDIO_URL` - Mythiq Audio Creator service URL
- `VIDEO_URL` - Mythiq Video Creator service URL

**Optional Configuration:**
- `DEBUG` - Enable Flask debug mode (default: false)
- `PORT` - Server port (default: 8000)

### Provider Priority

The system uses the following provider priority order:
1. **Groq** (Priority 1) - Primary provider for chat
2. **OpenRouter** (Priority 2) - Secondary provider for chat
3. **Together** (Priority 3) - Tertiary provider for chat and images

## Architecture

### Components

1. **Flask Application** (`app.py`)
   - RESTful API endpoints
   - Multi-provider AI management
   - Health monitoring and circuit breakers
   - CORS support for frontend integration

2. **Mythiq Agent** (`mythiq_agent/agent.py`)
   - Intelligent keyword-based routing
   - Parameter extraction from user messages
   - Service capability mapping

3. **Service Wrappers** (`mythiq_agent/services.py`)
   - HTTP client wrappers for Mythiq services
   - Error handling and timeout management
   - Health check implementations

4. **CLI Interface** (`main.py`)
   - Interactive and single-command modes
   - JSON response formatting

### AI Provider Management

- **Health Monitoring**: Continuous health checks for all providers
- **Circuit Breaker**: Automatic failover when providers are unhealthy
- **Rate Limiting**: Respect provider rate limits and quotas
- **Load Balancing**: Intelligent routing based on provider health and priority

## Deployment Platforms

### Railway
- Automatic deployment with `railway.toml`
- Built-in health checks
- Environment variable management
- Automatic HTTPS and custom domains

### Render
- Use the provided Dockerfile
- Set environment variables in Render dashboard
- Configure health check endpoint: `/health`

### Heroku
- Use the provided Dockerfile or buildpacks
- Set environment variables via Heroku CLI or dashboard
- Configure health checks in `app.json` if needed

## Monitoring and Observability

### Health Checks
- System metrics (CPU, memory usage)
- Provider health status
- Response time monitoring
- Error rate tracking

### Logging
- Structured logging with different levels
- Provider-specific error tracking
- Request/response logging for debugging

## Security

- Non-root user in Docker container
- Environment variable protection
- CORS configuration for frontend integration
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the health endpoint for system status
- Review logs for debugging information

