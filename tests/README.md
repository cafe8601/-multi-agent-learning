# 🧪 Testing Guide

**Purpose**: Comprehensive testing guide for Big Three Agents

---

## 📋 Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── unit/                                # Unit tests (fast, isolated)
│   ├── test_config.py                  # Configuration tests
│   ├── test_agent_pool.py              # Agent Pool unit tests
│   └── test_rag_system.py              # RAG system unit tests
├── integration/                         # Integration tests (services)
│   └── test_system_integration.py      # Full system integration
└── e2e/                                # End-to-end tests (realistic scenarios)
    ├── test_agent_pool_tier1.py        # Tier 1 agent validation
    └── test_complete_workflow.py       # Complete workflow tests
```

---

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/unit/test_config.py -v

# Run by marker
pytest -m unit                  # Unit tests only
pytest -m integration           # Integration tests only
pytest -m e2e                   # End-to-end tests only
```

### By Test Type

```bash
# Unit tests (fast, no dependencies)
pytest tests/unit/ -v

# Integration tests (requires services)
pytest tests/integration/ -v

# E2E tests (full scenarios)
pytest tests/e2e/ -v
```

### Advanced Options

```bash
# Skip slow tests
pytest -m "not slow"

# Run expensive tests (requires API keys)
pytest --run-expensive

# Run with detailed output
pytest -vv --tb=long

# Run specific test
pytest tests/unit/test_config.py::test_api_keys_loaded -v

# Run with coverage report
pytest --cov=apps.realtime_poc.big_three_realtime_agents \
       --cov-report=html \
       --cov-report=term

# View HTML coverage report
open htmlcov/index.html
```

---

## 🏷️ Test Markers

Tests are categorized with markers for easy selection:

| Marker | Description | Run Command |
|--------|-------------|-------------|
| `unit` | Fast unit tests | `pytest -m unit` |
| `integration` | Integration tests | `pytest -m integration` |
| `e2e` | End-to-end tests | `pytest -m e2e` |
| `slow` | Slow tests | `pytest -m slow` or skip with `-m "not slow"` |
| `expensive` | API cost tests | `pytest --run-expensive` |
| `requires_api_keys` | Needs API keys | Set keys in .env first |
| `requires_audio` | Needs audio hardware | `pytest -m requires_audio` |
| `requires_docker` | Needs Docker | `docker compose up` first |

---

## 🎯 Test Categories Explained

### Unit Tests

**Purpose**: Test individual components in isolation

**Characteristics**:
- Fast (< 1 second each)
- No external dependencies
- Mocked services
- High coverage goal (>90%)

**Examples**:
- Configuration loading
- Data model validation
- Utility functions
- Error handling

**Run**: `pytest tests/unit/ -v`

---

### Integration Tests

**Purpose**: Test component interactions

**Characteristics**:
- Moderate speed (1-10 seconds)
- May require services (Redis, etc.)
- Test actual integrations
- Coverage goal (>80%)

**Examples**:
- Memory system with storage
- Workflow execution
- Security audit logging
- Pool manager with selectors

**Run**: `pytest tests/integration/ -v`

---

### End-to-End Tests

**Purpose**: Test complete user scenarios

**Characteristics**:
- Slower (10+ seconds)
- Full system stack
- Realistic workflows
- Coverage goal (>70%)

**Examples**:
- Agent Pool Tier 1 validation
- Complete workflow execution
- Multi-agent orchestration
- Memory + Learning + Security integration

**Run**: `pytest tests/e2e/ -v`

---

## 🔬 Agent Pool Testing

### Tier 1 Agent Validation

**Purpose**: Validate that Tier 1 agents are production-ready

**What's Tested**:
1. ✅ Agent definition files exist
2. ✅ Markdown structure is valid
3. ✅ Pool manager loads agents
4. ✅ Expert selection works
5. ✅ Instance management works
6. ✅ Error handling is robust

**Run**:
```bash
pytest tests/e2e/test_agent_pool_tier1.py -v
```

### Expensive Tests (Real API Calls)

**Warning**: These tests use real API keys and incur costs!

**Run**:
```bash
# Requires API keys in .env
pytest tests/e2e/test_agent_pool_tier1.py --run-expensive -m expensive
```

---

## 📊 Coverage Goals

| Test Type | Target Coverage | Current |
|-----------|----------------|---------|
| Unit Tests | >90% | 85%+ |
| Integration Tests | >80% | 75%+ |
| E2E Tests | >70% | 60%+ |
| Overall | >80% | 75%+ |

**Check coverage**:
```bash
pytest --cov --cov-report=term-missing
```

---

## 🐛 Debugging Tests

### Show Print Statements

```bash
pytest -s  # Show print output
pytest -v -s  # Verbose with print output
```

### Debug Failed Tests

```bash
# Show full traceback
pytest --tb=long

# Drop into debugger on failure
pytest --pdb

# Last failed tests only
pytest --lf
```

### Run Single Test

```bash
pytest tests/unit/test_config.py::test_api_keys_loaded -v
```

---

## 🔧 Test Environment Setup

### Prerequisites

```bash
# 1. Install test dependencies
pip install -r requirements.txt

# 2. Setup environment (optional for unit tests)
cp .env.sample .env

# 3. Start services (for integration tests)
docker compose up -d redis

# 4. Run tests
pytest
```

### Environment Variables for Tests

```bash
# Set test API keys (optional, for integration tests)
export OPENAI_API_KEY="sk-test-key"
export ANTHROPIC_API_KEY="sk-ant-test-key"
export GEMINI_API_KEY="test-gemini-key"

# Or use .env file
```

---

## 📝 Writing New Tests

### Test Template

```python
import pytest


class TestMyFeature:
    """Test description."""

    def test_basic_functionality(self):
        """Test basic case."""
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == "expected"

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async case."""
        result = await my_async_function()
        assert result is not None
```

### Fixtures

Use shared fixtures from `conftest.py`:

```python
def test_with_fixtures(all_api_keys, temp_working_dir):
    """Example using fixtures."""
    assert all_api_keys["OPENAI_API_KEY"]
    assert temp_working_dir.exists()
```

---

## 🎯 Test Execution Checklist

### Before Committing

- [ ] Run all unit tests: `pytest tests/unit/`
- [ ] Run all integration tests: `pytest tests/integration/`
- [ ] Check coverage: `pytest --cov`
- [ ] No failing tests
- [ ] Coverage >75%

### Before Deploying

- [ ] Run E2E tests: `pytest tests/e2e/`
- [ ] Run slow tests: `pytest -m slow`
- [ ] Docker tests: `pytest -m requires_docker`
- [ ] All tests passing
- [ ] Coverage >80%

---

## 🚀 CI/CD Integration

Tests run automatically on:
- Every push to main
- Every pull request
- Scheduled daily runs

**GitHub Actions**: `.github/workflows/ci.yml`

**Local CI simulation**:
```bash
# Run same tests as CI
pytest tests/unit tests/integration -v --cov
```

---

## 📚 Additional Resources

- **pytest documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Coverage.py**: https://coverage.readthedocs.io/

---

## 🆘 Getting Help

**Test failures?**
1. Check error message carefully
2. Run with `-vv` for detailed output
3. Check if services are running (Redis, etc.)
4. Verify API keys (if needed)
5. Check `conftest.py` for fixture setup

**Questions?**
- See main README.md
- Check DEPLOYMENT_GUIDE.md
- Open issue on GitHub

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**Addresses**: Manus AI recommendation for comprehensive testing
