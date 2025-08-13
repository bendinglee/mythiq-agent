# Mythiq Agent Deployment Guide

## Quick Deployment Options

### 1. Railway (Recommended)

**One-Click Deploy:**
1. Connect your GitHub repository to Railway
2. Railway will automatically detect `railway.toml`
3. Set environment variables in Railway dashboard:
   ```
   GROQ_API_KEY=your_groq_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   TOGETHER_API_KEY=your_together_api_key
   ```
4. Deploy automatically with health checks

**Manual Setup:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

### 2. Render

**One-Click Deploy:**
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Manual Setup:**
1. Connect GitHub repository to Render
2. Use `render.yaml` configuration
3. Set environment variables in Render dashboard
4. Deploy with automatic health checks

### 3. Heroku

**One-Click Deploy:**
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

**Manual Setup:**
```bash
# Install Heroku CLI and login
heroku login

# Create app and deploy
heroku create your-app-name
git push heroku main
```

### 4. Docker

**Local Docker:**
```bash
# Build and run
docker build -t mythiq-agent .
docker run -p 8000:8000 --env-file .env mythiq-agent
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  mythiq-agent:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Environment Variables

### Required for AI Providers
```bash
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
TOGETHER_API_KEY=your_together_api_key_here
```

### Required for Mythiq Services
```bash
ASSISTANT_URL=https://mythiq-assistant-production.up.railway.app
GAME_URL=https://mythiq-game-maker-production.up.railway.app
MEDIA_URL=https://mythiq-media-creator-production.up.railway.app
AUDIO_URL=https://mythiq-audio-creator-production.up.railway.app
VIDEO_URL=https://mythiq-video-creator-production.up.railway.app
```

### Optional Configuration
```bash
DEBUG=false
PORT=8000
```

## Health Check Endpoints

- **Health Check:** `GET /health`
- **API Info:** `GET /`
- **Capabilities:** `GET /capabilities`
- **Provider Status:** `GET /providers`

## Testing Deployment

```bash
# Test health endpoint
curl https://your-app-url.com/health

# Test chat endpoint
curl -X POST https://your-app-url.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'

# Test Mythiq agent processing
curl -X POST https://your-app-url.com/process \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a puzzle game"}'
```

## Monitoring

### Health Monitoring
- System metrics (CPU, memory)
- Provider health status
- Response time tracking
- Error rate monitoring

### Logs
- Structured logging with timestamps
- Provider-specific error tracking
- Request/response logging

## Troubleshooting

### Common Issues

1. **Health Check Fails**
   - Verify `/health` endpoint is accessible
   - Check if app is listening on `0.0.0.0:$PORT`
   - Ensure all dependencies are installed

2. **Provider Errors**
   - Verify API keys are set correctly
   - Check provider status at `/providers`
   - Review logs for specific error messages

3. **Service Unavailable**
   - Check Mythiq service URLs
   - Verify network connectivity
   - Review service health status

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
python app.py
```

## Security Considerations

- API keys stored as environment variables
- Non-root user in Docker container
- CORS configured for frontend integration
- Input validation and sanitization
- Health checks don't expose sensitive data

## Performance Optimization

- Multi-provider fallback for high availability
- Circuit breaker pattern for failed providers
- Rate limiting awareness
- Efficient health monitoring
- Minimal resource usage

## Support

For deployment issues:
1. Check the health endpoint: `/health`
2. Review application logs
3. Verify environment variables
4. Test individual endpoints
5. Check provider status: `/providers`

