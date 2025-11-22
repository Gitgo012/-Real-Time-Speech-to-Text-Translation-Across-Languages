# Testing & Jenkins CI/CD Setup

This directory contains comprehensive testing setup and Jenkins pipeline configuration for the Real-Time Speech-to-Text Translation project.

## Quick Start

### Option 1: Windows

```powershell
.\setup-jenkins.bat
```

### Option 2: Linux/Mac

```bash
chmod +x setup-jenkins.sh
./setup-jenkins.sh
```

### Manual Setup

#### Backend Tests

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-flask

# Run tests
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

#### Frontend Tests

```bash
cd frontend
npm install
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom

# Run tests
npm run test
npm run test:coverage
npm run test:ui
```

## Directory Structure

```
tests/
├── test_app.py                 # Backend unit tests
├── conftest.py                 # Pytest configuration and fixtures
└── __init__.py

frontend/
├── src/
│   └── pages/
│       └── Dashboard.test.jsx  # React component tests
├── vitest.config.js            # Vitest configuration
├── vitest.setup.js             # Test environment setup
└── package.json                # NPM scripts with test commands

Jenkinsfile                      # Jenkins pipeline definition
JENKINS_SETUP.md                 # Detailed Jenkins setup guide
jenkins-casc.yaml               # Jenkins Configuration as Code
```

## Test Coverage

### Backend (Python)

**Files Tested:**

- `app.py` - Main Flask application
  - Health check endpoint
  - Session management
  - Translation history endpoints
  - Audio processing functions
  - Streaming handlers
  - SocketIO events
  - Error handling

**Test Classes:**

- `TestHealthEndpoint` - Health check functionality
- `TestSessionCheck` - Authentication
- `TestTranslationHistory` - History CRUD operations
- `TestAudioProcessing` - Audio codec handling
- `TestTranslationFunctions` - M2M100 translation
- `TestStreamingBuffers` - Buffer management
- `TestSocketIOEvents` - WebSocket events
- `TestErrorHandling` - Error scenarios
- `TestLanguageSupport` - Language configuration
- `TestModelLoading` - Model initialization

**Running Backend Tests:**

```bash
# All tests
pytest tests/test_app.py -v

# With coverage
pytest tests/test_app.py --cov=. --cov-report=html

# Specific test class
pytest tests/test_app.py::TestHealthEndpoint -v

# Specific test
pytest tests/test_app.py::TestHealthEndpoint::test_health_endpoint -v

# Show print statements
pytest tests/test_app.py -v -s

# Stop on first failure
pytest tests/test_app.py -x

# Run last failed tests
pytest tests/test_app.py --lf
```

### Frontend (JavaScript/React)

**Files Tested:**

- `Dashboard.jsx` - Main dashboard component
  - Rendering
  - Recording functionality
  - Mode toggle
  - Socket.IO integration
  - State management
  - Event handling

**Running Frontend Tests:**

```bash
cd frontend

# All tests
npm run test

# With coverage
npm run test:coverage

# With UI dashboard
npm run test:ui

# Watch mode
npm run test -- --watch

# Specific file
npm run test -- Dashboard.test.jsx
```

## Jenkins Pipeline Stages

The `Jenkinsfile` contains the following stages:

1. **Checkout** - Clone repository
2. **Environment Setup** - Verify Python/Node versions
3. **Backend Dependencies** - Install Python packages
4. **Frontend Dependencies** - Install npm packages
5. **Backend Lint** - Code quality checks
6. **Frontend Lint** - ESLint validation
7. **Backend Tests** - pytest with coverage
8. **Frontend Tests** - Vitest/Jest tests
9. **Security Scan** - CVE checks (safety, npm audit)
10. **Build Docker** - Create container images
11. **Docker Compose** - Validate docker-compose.yml
12. **Archive Reports** - Save test results

## Configuration Files

### pytest.ini

Configures pytest behavior:

- Test discovery patterns
- Output options
- Custom markers (unit, integration, websocket, etc.)
- Warnings handling

### vitest.config.js

Configures Vitest (JavaScript test runner):

- jsdom environment for React
- Coverage providers and reporters
- Module aliases
- Setup files

### vitest.setup.js

Test environment setup:

- Testing Library imports
- Window.matchMedia mock
- MediaDevices API mock
- AudioContext mock
- AudioWorkletNode mock

## Jenkins Configuration

### Setup Jenkins Job

1. Open `http://localhost:8090`
2. Click "New Item"
3. Name: `RealtimeASR-Pipeline`
4. Type: Pipeline
5. Pipeline → Definition: Pipeline script from SCM
6. SCM: Git
7. Repository: `https://github.com/Gitgo012/Real-Time-Speech-to-Text-Translation-Across-Languages.git`
8. Script Path: `Jenkinsfile`
9. Save and Build

### GitHub Webhook Setup (Optional)

1. Repository Settings → Webhooks
2. Add webhook:
   - URL: `http://localhost:8090/github-webhook/`
   - Content-type: application/json
   - Events: Push events

### Jenkins Configuration as Code (Advanced)

To use automatic Jenkins setup:

```bash
# Set environment variable
export CASC_JENKINS_CONFIG=/path/to/jenkins-casc.yaml

# Or in docker-compose.yml
services:
  jenkins:
    environment:
      - CASC_JENKINS_CONFIG=/var/jenkins_home/jenkins.yaml
    volumes:
      - ./jenkins-casc.yaml:/var/jenkins_home/jenkins.yaml
```

## Test Reports

After running tests:

### Backend Coverage

```
htmlcov/index.html     # Open in browser for detailed coverage
coverage.xml           # Machine-readable format
```

### Frontend Coverage

```
frontend/coverage/     # Coverage directory
```

### Jenkins Reports

- `http://localhost:8090/job/RealtimeASR-Pipeline/[BUILD]/HTML_Report/`
- Console output at `[BUILD]/console`

## Troubleshooting

### Tests fail with "ModuleNotFoundError"

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
cd frontend && npm install && cd ..
```

### Jenkins can't find Python/Node

```bash
# Check PATH in Jenkins
# Go to Manage Jenkins → Configure System
# Add to PATH: /usr/local/bin:/usr/bin:/bin
```

### Docker build fails

```bash
# Ensure Jenkins user can access Docker
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### WebSocket tests fail

- Ensure Socket.IO mocks are loaded in `vitest.setup.js`
- Check that `socket.io-client` is properly mocked

### Coverage reports not generated

```bash
# Ensure pytest and coverage installed
pip install pytest-cov

# Force regenerate
pytest --cov=. --cov-report=html --cov-report=xml
```

## CI/CD Best Practices

1. **Run tests before committing**

   ```bash
   git add .
   pytest tests/ && npm run test && git commit
   ```

2. **Use pre-commit hooks**
   Create `.git/hooks/pre-commit`:

   ```bash
   #!/bin/bash
   pytest tests/ || exit 1
   ```

3. **Monitor coverage**

   - Aim for >80% coverage
   - Review coverage reports regularly
   - Set minimum coverage thresholds in Jenkinsfile

4. **Security scanning**

   ```bash
   pip install safety
   safety check
   npm audit
   ```

5. **Performance testing**
   - Add stress tests for streaming
   - Monitor memory usage
   - Profile hot code paths

## Continuous Improvement

- Add integration tests for API endpoints
- Expand frontend component tests
- Add end-to-end tests with Playwright
- Implement SonarQube code quality analysis
- Set up performance benchmarks
- Add load testing for streaming

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [GitHub Actions Alternative](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

## Support

For issues or questions:

1. Check logs: `http://localhost:8090/job/RealtimeASR-Pipeline/[BUILD]/console`
2. Review JENKINS_SETUP.md for detailed configuration
3. Check test output for specific failures
4. Review GitHub issues in the repository
