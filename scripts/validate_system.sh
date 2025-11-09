#!/bin/bash
# System Validation Script for Big Three Agents
# Validates that all components are properly configured

set -e

echo "🔍 Big Three Agents - System Validation"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Check function
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $1"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}: $1"
        ((FAIL++))
    fi
}

check_warn() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $1"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  WARN${NC}: $1"
        ((WARN++))
    fi
}

echo "1. Checking Core Files"
echo "----------------------"
[ -f "requirements.txt" ]
check "requirements.txt exists"

[ -f "Dockerfile" ]
check "Dockerfile exists"

[ -f "docker-compose.yml" ]
check "docker-compose.yml exists"

[ -f ".dockerignore" ]
check ".dockerignore exists"

[ -f ".env.sample" ]
check ".env.sample exists"

echo ""
echo "2. Checking Directory Structure"
echo "--------------------------------"
[ -d "apps/realtime-poc/big_three_realtime_agents" ]
check "Main application directory exists"

[ -d "apps/realtime-poc/big_three_realtime_agents/agents" ]
check "Agents directory exists"

[ -d "apps/realtime-poc/big_three_realtime_agents/memory" ]
check "Memory subsystem exists"

[ -d "apps/realtime-poc/big_three_realtime_agents/learning" ]
check "Learning subsystem exists"

[ -d "apps/realtime-poc/big_three_realtime_agents/security" ]
check "Security subsystem exists"

[ -d "apps/realtime-poc/big_three_realtime_agents/workflow" ]
check "Workflow subsystem exists"

[ -d "tests/unit" ]
check "Unit tests directory exists"

[ -d "tests/integration" ]
check "Integration tests directory exists"

[ -d ".github/workflows" ]
check "CI/CD workflows directory exists"

echo ""
echo "3. Checking Python Files"
echo "------------------------"
[ -f "apps/realtime-poc/big_three_realtime_agents/__init__.py" ]
check "Main __init__.py exists"

[ -f "apps/realtime-poc/big_three_realtime_agents/config.py" ]
check "Configuration module exists"

[ -f "apps/realtime-poc/big_three_realtime_agents/main.py" ]
check "Main entry point exists"

echo ""
echo "4. Checking Test Files"
echo "----------------------"
[ -f "tests/conftest.py" ]
check "Pytest configuration exists"

[ -f "tests/unit/test_config.py" ]
check "Unit tests exist"

[ -f "tests/integration/test_system_integration.py" ]
check "Integration tests exist"

echo ""
echo "5. Checking CI/CD Configuration"
echo "--------------------------------"
[ -f ".github/workflows/ci.yml" ]
check "GitHub Actions workflow exists"

echo ""
echo "6. Checking Documentation"
echo "-------------------------"
[ -f "README.md" ]
check "Main README exists"

[ -f "DEPLOYMENT_GUIDE.md" ]
check "Deployment guide exists"

[ -f "IMPLEMENTATION_COMPLETE.md" ]
check "Implementation summary exists"

[ -f "claudedocs/revision_md_analysis_report.md" ]
check "Analysis report exists"

echo ""
echo "7. Checking Python Syntax (if Python available)"
echo "------------------------------------------------"
if command -v python3 &> /dev/null; then
    python3 -c "import sys; sys.path.insert(0, '.'); from apps.realtime_poc.big_three_realtime_agents import config" 2>&1 | grep -q "Error"
    if [ $? -eq 1 ]; then
        echo -e "${GREEN}✅ PASS${NC}: Python imports work"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}: Python import errors"
        ((FAIL++))
    fi
else
    echo -e "${YELLOW}⚠️  WARN${NC}: Python not available for syntax check"
    ((WARN++))
fi

echo ""
echo "8. Checking Environment Configuration"
echo "--------------------------------------"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ PASS${NC}: .env file exists"
    ((PASS++))

    # Check for required keys
    if grep -q "OPENAI_API_KEY=" .env; then
        echo -e "${GREEN}✅ PASS${NC}: OPENAI_API_KEY configured"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  WARN${NC}: OPENAI_API_KEY not found in .env"
        ((WARN++))
    fi

    if grep -q "GEMINI_API_KEY=" .env; then
        echo -e "${GREEN}✅ PASS${NC}: GEMINI_API_KEY configured"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  WARN${NC}: GEMINI_API_KEY not found in .env"
        ((WARN++))
    fi
else
    echo -e "${YELLOW}⚠️  WARN${NC}: .env file not found (copy from .env.sample)"
    ((WARN++))
fi

echo ""
echo "9. Checking Docker (if available)"
echo "----------------------------------"
if command -v docker &> /dev/null; then
    docker --version &> /dev/null
    check "Docker is installed"

    if command -v docker compose &> /dev/null; then
        echo -e "${GREEN}✅ PASS${NC}: Docker Compose v2 available"
        ((PASS++))
    elif command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✅ PASS${NC}: Docker Compose v1 available"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}: Docker Compose not found"
        ((FAIL++))
    fi
else
    echo -e "${YELLOW}⚠️  WARN${NC}: Docker not installed"
    ((WARN++))
fi

echo ""
echo "10. Checking Agent Pool"
echo "-----------------------"
[ -d "agentpool/tier1-core" ]
check "Tier 1 agents directory exists"

[ -d "agentpool/tier2-specialized" ]
check "Tier 2 agents directory exists"

# Count agents
TIER1_COUNT=$(find agentpool/tier1-core -name "*.md" 2>/dev/null | wc -l)
TIER2_COUNT=$(find agentpool/tier2-specialized -name "*.md" 2>/dev/null | wc -l)

echo "   Found $TIER1_COUNT Tier 1 agents"
echo "   Found $TIER2_COUNT Tier 2 agents"

echo ""
echo "========================================"
echo "📊 Validation Summary"
echo "========================================"
echo -e "${GREEN}✅ PASSED${NC}: $PASS"
echo -e "${YELLOW}⚠️  WARNINGS${NC}: $WARN"
echo -e "${RED}❌ FAILED${NC}: $FAIL"
echo ""

# Overall status
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 System validation PASSED!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure .env with your API keys (if not done)"
    echo "2. Run: docker compose up -d"
    echo "3. Check logs: docker compose logs -f big-three-agents"
    exit 0
else
    echo -e "${RED}❌ System validation FAILED with $FAIL errors${NC}"
    echo "Please fix the errors above before deployment"
    exit 1
fi
