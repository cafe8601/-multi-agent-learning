# 🚀 Big Three Agents - Complete Deployment Guide

**Version**: 2.0.0
**Last Updated**: 2025-11-09
**Status**: Production-Ready with Testing & CI/CD

---

## 📋 Quick Start Summary

```bash
# 1. Clone and setup
git clone https://github.com/cafe8601/-multi-agent-learning.git
cd multi-agent-learning

# 2. Configure environment
cp .env.sample .env
# Edit .env with your API keys

# 3. Run with Docker (Recommended)
docker compose up -d

# 4. Check logs
docker compose logs -f big-three-agents
```

---

## 🎯 System Requirements

### Minimum Requirements
- **Docker**: 24.0+ with Docker Compose v2
- **RAM**: 4GB (8GB recommended)
- **CPU**: 2 cores (4 cores recommended)
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### API Requirements
- **OpenAI API Key** (Required): For Realtime voice orchestration
- **Gemini API Key** (Required): For browser automation
- **Anthropic API Key** (Optional): For Claude Code API mode
  - OR **Claude Max Subscription** (Alternative): For browser automation mode

---

## 🔐 Environment Configuration

### 1. Create `.env` File

```bash
cp .env.sample .env
```

### 2. Configure API Keys

Edit `.env` with your actual keys:

```env
# ============================================================================
# API Keys (REQUIRED)
# ============================================================================
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
GEMINI_API_KEY=your-actual-gemini-api-key-here

# Claude Configuration
ANTHROPIC_API_KEY=sk-ant-your-key-here  # OR leave empty for Claude Max
CLAUDE_MODE=auto  # "auto", "api", or "max"

# ============================================================================
# System Configuration
# ============================================================================
ENGINEER_NAME=YourName
AGENT_WORKING_DIRECTORY=apps/content-gen

# ============================================================================
# Advanced Features
# ============================================================================
ENABLE_AGENT_POOL=true
ENABLE_WORKFLOW=true
ENABLE_MEMORY=true
ENABLE_LEARNING=true
ENABLE_SECURITY=true
```

---

## 🐳 Docker Deployment (Recommended)

### Standard Deployment

```bash
# Build and start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f big-three-agents

# Stop services
docker compose down
```

### With Monitoring (Prometheus + Grafana)

```bash
# Start with monitoring stack
docker compose --profile monitoring up -d

# Access services
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Redis: localhost:6379
```

### Resource Management

Modify `docker-compose.yml` for custom resource limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Increase CPU limit
      memory: 8G        # Increase memory limit
```

---

## 💻 Local Python Development

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium
```

### 2. Run Application

```bash
# Set Python path
export PYTHONPATH=$(pwd)

# Text mode (default)
python -m apps.realtime-poc.big_three_realtime_agents.main

# Voice mode (requires microphone)
python -m apps.realtime-poc.big_three_realtime_agents.main --voice

# Auto-prompt mode (non-interactive)
python -m apps.realtime-poc.big_three_realtime_agents.main \
  --prompt "Create a simple Flask web application"

# Use mini model (cost-effective)
python -m apps.realtime-poc.big_three_realtime_agents.main --mini
```

---

## 🧪 Testing

### Run All Tests

```bash
# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# All tests with coverage
pytest tests/ -v --cov=apps.realtime_poc.big_three_realtime_agents \
  --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Test configuration only
pytest tests/unit/test_config.py -v

# Test system integration
pytest tests/integration/test_system_integration.py -v

# Test with specific marker
pytest -m "not slow" -v
```

---

## 🔍 System Validation

### Health Check Script

Create `scripts/health_check.sh`:

```bash
#!/bin/bash
set -e

echo "🔍 Big Three Agents - Health Check"
echo "=================================="

# Check Docker services
echo -n "Docker services: "
docker compose ps --services --filter "status=running" | wc -l | tr -d ' '
echo " running"

# Check Redis
echo -n "Redis: "
docker compose exec redis redis-cli ping || echo "FAILED"

# Check main service
echo -n "Big Three Agents: "
docker compose exec big-three-agents python -c \
  "from apps.realtime_poc.big_three_realtime_agents import config; print('HEALTHY')" \
  || echo "FAILED"

# Check logs for errors
echo "Recent errors:"
docker compose logs --tail=50 big-three-agents | grep -i error | tail -5 || echo "None"

echo "=================================="
echo "✅ Health check complete"
```

Run with:
```bash
chmod +x scripts/health_check.sh
./scripts/health_check.sh
```

---

## 📊 Monitoring & Observability

### Logs

```bash
# View all logs
docker compose logs

# Follow specific service
docker compose logs -f big-three-agents

# Last 100 lines
docker compose logs --tail=100 big-three-agents

# Filter by level
docker compose logs big-three-agents | grep ERROR
```

### Metrics (With Monitoring Profile)

1. **Grafana Dashboard**: `http://localhost:3000`
   - Default credentials: `admin/admin`
   - Pre-configured dashboards in `monitoring/grafana-dashboards/`

2. **Prometheus**: `http://localhost:9090`
   - Query metrics directly
   - View targets and alerts

3. **Redis**: Monitor with `redis-cli`
   ```bash
   docker compose exec redis redis-cli info
   ```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'apps'"

**Solution**:
```bash
export PYTHONPATH=$(pwd)
# Or add to .bashrc/.zshrc permanently
```

#### 2. "Port already in use"

**Solution**:
```bash
# Check what's using the port
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

#### 3. "API key not found"

**Solution**:
```bash
# Verify .env file
cat .env | grep API_KEY

# Ensure .env is in project root
ls -la .env

# Restart containers to pick up changes
docker compose restart
```

#### 4. Playwright browser not installed

**Solution**:
```bash
# Inside container
docker compose exec big-three-agents playwright install chromium

# Or rebuild image
docker compose build --no-cache big-three-agents
```

#### 5. Memory/CPU limits

**Solution**:
```bash
# Check Docker stats
docker stats

# Increase limits in docker-compose.yml
# See Resource Management section above
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The system includes comprehensive CI/CD:

1. **Lint & Format**: Black, Ruff, MyPy
2. **Unit Tests**: With coverage reporting
3. **Integration Tests**: Full system validation
4. **Security Scans**: Bandit, Safety
5. **Docker Build**: Automated image building
6. **Dependency Review**: Automated on PRs

### Setup GitHub Secrets

Required secrets for full CI/CD:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

Optional for deployment:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

---

## 📦 Production Deployment

### Pre-Production Checklist

- [ ] All tests passing (`pytest tests/`)
- [ ] Security scans clean (`bandit`, `safety`)
- [ ] Docker image builds successfully
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] API keys securely stored (Vault/AWS Secrets Manager)
- [ ] Resource limits appropriate for load
- [ ] Logging configured correctly

### Production Environment Variables

```env
# Production-specific settings
CLAUDE_MODE=api  # Use API for reliability
CLAUDE_MAX_HEADLESS=true  # If using Max mode

# Resource management
MAX_INSTANCES_PER_EXPERT=5
AGENT_IDLE_TIMEOUT_MINUTES=15

# Monitoring (if using external services)
PROMETHEUS_ENDPOINT=https://your-prometheus.com
GRAFANA_ENDPOINT=https://your-grafana.com
```

### Backup Strategy

```bash
# Backup agent working directory
tar -czf backup-$(date +%Y%m%d).tar.gz apps/content-gen/

# Backup Redis data
docker compose exec redis redis-cli BGSAVE

# Automated backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/big-three-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup working directory
tar -czf "$BACKUP_DIR/content-gen.tar.gz" apps/content-gen/

# Backup Redis
docker compose exec redis redis-cli BGSAVE
sleep 5
docker cp big-three-redis:/data/dump.rdb "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
EOF
chmod +x scripts/backup.sh
```

---

## 🔐 Security Best Practices

1. **API Key Management**
   - Never commit `.env` to version control
   - Use secrets management (HashiCorp Vault, AWS Secrets Manager)
   - Rotate keys regularly

2. **Container Security**
   - Run as non-root user (already configured)
   - Scan images regularly: `docker scan big-three-agents:latest`
   - Keep base images updated

3. **Network Security**
   - Use bridge network (default in docker-compose)
   - Limit exposed ports
   - Use TLS for external communication

4. **Access Control**
   - Enable security manager (`ENABLE_SECURITY=true`)
   - Review audit logs regularly
   - Implement RBAC if multi-user

---

## 📚 Additional Resources

- **Main README**: `README.md`
- **Architecture Documentation**: `claudedocs/COMPLETE_SYSTEMS_SUMMARY.md`
- **Implementation Status**: `apps/realtime-poc/IMPLEMENTATION_STATUS.md`
- **Analysis Report**: `claudedocs/revision_md_analysis_report.md`
- **Refactoring Guide**: `apps/realtime-poc/REFACTORING_GUIDE.md`

---

## 🆘 Support

- **Issues**: https://github.com/cafe8601/-multi-agent-learning/issues
- **Discussions**: https://github.com/cafe8601/-multi-agent-learning/discussions
- **Documentation**: `claudedocs/` directory

---

## 📝 Version History

- **2.0.0** (2025-11-09): Complete system with Docker, testing, CI/CD
- **1.0.0**: Initial modular implementation
- **0.9.0**: Prototype phase

---

**Made with ❤️ by the Multi-Agent Learning Community**
