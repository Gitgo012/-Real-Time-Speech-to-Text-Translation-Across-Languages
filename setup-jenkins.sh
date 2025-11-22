#!/bin/bash
# Quick start script for setting up Jenkins pipeline

set -e

echo "==============================================="
echo "Real-Time Speech-to-Text Translation"
echo "Jenkins Pipeline Setup"
echo "==============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Jenkins is running
echo -e "${YELLOW}Checking if Jenkins is running on port 8090...${NC}"
if curl -s http://localhost:8090 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Jenkins is running${NC}"
else
    echo -e "${RED}✗ Jenkins is NOT running on localhost:8090${NC}"
    echo "  Please start Jenkins first:"
    echo "  Windows Service: services.msc (search for Jenkins)"
    echo "  Docker: docker run -p 8090:8080 jenkins/jenkins:latest"
    exit 1
fi

echo ""

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Check Node.js
echo -e "${YELLOW}Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js ${NODE_VERSION} found${NC}"
else
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi

# Check Git
echo -e "${YELLOW}Checking Git installation...${NC}"
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "${GREEN}✓ ${GIT_VERSION}${NC}"
else
    echo -e "${RED}✗ Git not found${NC}"
    exit 1
fi

# Check Docker (optional)
echo -e "${YELLOW}Checking Docker installation...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ ${DOCKER_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠ Docker not found (optional, needed for Docker builds)${NC}"
fi

echo ""
echo -e "${YELLOW}Installing dependencies...${NC}"

# Backend dependencies
echo "Installing Python dependencies..."
python3 -m venv venv 2>/dev/null || true
if [ -f venv/bin/activate ]; then
    . venv/bin/activate
elif [ -f venv/Scripts/activate ]; then
    . venv/Scripts/activate
fi

pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q pytest pytest-cov pytest-flask python-dotenv

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Frontend dependencies
echo "Installing Node.js dependencies..."
cd frontend
npm install -q --legacy-peer-deps 2>/dev/null || npm install -q
npm install -q --save-dev vitest @testing-library/react @testing-library/jest-dom 2>/dev/null || true
cd ..

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Running local tests...${NC}"

# Run backend tests
echo "Running backend tests..."
pytest tests/ -q --tb=line || echo -e "${YELLOW}Some tests may have failed${NC}"

# Run frontend tests
echo "Running frontend tests..."
cd frontend
npm run test 2>/dev/null || echo -e "${YELLOW}Frontend tests skipped${NC}"
cd ..

echo ""
echo "==============================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "==============================================="
echo ""
echo "Next steps:"
echo "1. Go to http://localhost:8090"
echo "2. Create a new Pipeline job:"
echo "   - New Item → Pipeline"
echo "   - Name: RealtimeASR-Pipeline"
echo "   - Pipeline → Definition: Pipeline script from SCM"
echo "   - SCM: Git"
echo "   - Repository: https://github.com/Gitgo012/Real-Time-Speech-to-Text-Translation-Across-Languages.git"
echo "   - Script Path: Jenkinsfile"
echo ""
echo "3. Click 'Build Now' to trigger the first build"
echo ""
echo "For detailed setup instructions, see: JENKINS_SETUP.md"
echo ""
