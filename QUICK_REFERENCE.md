# Jenkins & Testing - Quick Reference

## 🚀 Quick Start (2 minutes)

### Windows

```powershell
.\setup-jenkins.bat
# Then go to http://localhost:8090 and create pipeline job
```

### Linux/Mac

```bash
./setup-jenkins.sh
# Then go to http://localhost:8090 and create pipeline job
```

## 📋 Create Jenkins Job

1. `http://localhost:8090` → **New Item**
2. Name: `RealtimeASR-Pipeline`
3. Type: **Pipeline**
4. Pipeline → Definition: **Pipeline script from SCM**
5. SCM: **Git**
6. Repository: `https://github.com/Gitgo012/Real-Time-Speech-to-Text-Translation-Across-Languages.git`
7. Script Path: `Jenkinsfile`
8. **Save** → **Build Now**

## 🧪 Run Tests Locally

### Backend

```bash
pytest tests/ -v                              # Run all tests
pytest tests/ --cov=. --cov-report=html      # With coverage
pytest tests/test_app.py::TestHealthEndpoint -v  # Specific class
```

### Frontend

```bash
cd frontend
npm run test                                  # Run tests
npm run test:coverage                         # With coverage
npm run test:ui                               # With UI dashboard
```

## 📊 View Results

- Console: `http://localhost:8090/job/RealtimeASR-Pipeline/BUILD_NUMBER/console`
- Results: `http://localhost:8090/job/RealtimeASR-Pipeline/BUILD_NUMBER`
- Coverage: `http://localhost:8090/job/RealtimeASR-Pipeline/BUILD_NUMBER/HTML_Report/`

## 🔧 Common Commands

```bash
# Check Jenkins running
curl http://localhost:8090

# Run specific backend test
pytest tests/test_app.py::TestHealthEndpoint::test_health_endpoint -v

# Backend tests with details
pytest tests/ -v -s --tb=long

# Frontend tests with watch
npm run test -- --watch

# Generate coverage locally
pytest --cov=. --cov-report=html
open htmlcov/index.html  # View coverage

# Clean test artifacts
rm -rf .pytest_cache htmlcov coverage.xml
```

## 📁 Key Files

| File                                    | Purpose                           |
| --------------------------------------- | --------------------------------- |
| `Jenkinsfile`                           | Pipeline stages and configuration |
| `tests/test_app.py`                     | Backend unit tests (40+ tests)    |
| `frontend/src/pages/Dashboard.test.jsx` | React component tests             |
| `pytest.ini`                            | Python test config                |
| `frontend/vitest.config.js`             | JavaScript test config            |
| `JENKINS_SETUP.md`                      | Detailed setup guide              |
| `TESTING_README.md`                     | Testing documentation             |

## ⚡ Pipeline Stages

1. Checkout
2. Environment Setup
3. Backend Dependencies
4. Frontend Dependencies
5. Backend Lint
6. Frontend Lint
7. Backend Tests ← **Most Important**
8. Frontend Tests ← **Most Important**
9. Security Scan
10. Build Docker
11. Docker Validation
12. Archive Reports

## 🐛 Quick Fixes

| Issue                    | Solution                                            |
| ------------------------ | --------------------------------------------------- |
| Jenkins won't start      | `services.msc` → Find Jenkins → Start               |
| Tests fail - ImportError | `pip install --force-reinstall -r requirements.txt` |
| Docker build fails       | `sudo usermod -aG docker jenkins`                   |
| No coverage              | `pip install pytest-cov`                            |
| Node modules issue       | `cd frontend && npm install`                        |

## 📈 What Gets Tested

### Backend (40+ tests)

- ✅ REST API endpoints (health, session, history)
- ✅ Audio processing (PCM, WebM)
- ✅ Translation functions
- ✅ Streaming buffers
- ✅ WebSocket events
- ✅ Error handling
- ✅ Language support
- ✅ Model loading

### Frontend (9 tests)

- ✅ Component rendering
- ✅ Recording controls
- ✅ Mode toggle
- ✅ WebSocket integration
- ✅ State management
- ✅ Event handling

## 🔐 Security Checks

- Python: `safety` - CVE detection
- JavaScript: `npm audit` - Vulnerability scanning
- Code quality: `flake8`, `black`, `eslint`

## 📞 Help

- Setup: See `JENKINS_SETUP.md`
- Testing: See `TESTING_README.md`
- Summary: See `CI-CD_SUMMARY.md`
- Troubleshooting: See `JENKINS_SETUP.md` (Troubleshooting section)

---

**You're all set! Go to http://localhost:8090 now.** 🎉
