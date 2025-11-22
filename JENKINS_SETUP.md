# Jenkins Pipeline Setup Guide

This guide explains how to set up and run the Jenkins pipeline for the Real-Time Speech-to-Text Translation project.

## Prerequisites

- Jenkins running on `http://localhost:8090`
- Git installed on Jenkins server
- Python 3.10+ installed
- Node.js 18+ installed
- Docker installed (for containerized builds)
- The project repository cloned or accessible via Git

## 1. Jenkins Pipeline Job Creation

### Option A: Using Jenkins UI (Recommended for beginners)

1. Go to `http://localhost:8090` in your browser
2. Click **"New Item"**
3. Enter job name: `RealtimeASR-Pipeline`
4. Select **"Pipeline"**
5. Click **OK**

### Option B: Using Jenkins Configuration as Code (Recommended for automation)

See `jenkins-config.yaml` in the repository root.

## 2. Configure the Pipeline Job

### Step 1: General Settings
- **Description**: Real-Time Speech-to-Text Translation CI/CD Pipeline
- **GitHub Project**: `https://github.com/Gitgo012/Real-Time-Speech-to-Text-Translation-Across-Languages`
- **Build Triggers**: 
  - Check "Poll SCM" → Schedule: `H/5 * * * *` (every 5 minutes)
  - OR use GitHub webhook (see section 5)

### Step 2: Pipeline Configuration
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/Gitgo012/Real-Time-Speech-to-Text-Translation-Across-Languages.git`
- **Credentials**: Add your GitHub credentials
- **Branch**: `feature/containerization` (or your branch)
- **Script Path**: `Jenkinsfile`

### Step 3: Save and Run

Click **"Save"** then **"Build Now"** to trigger the first build.

## 3. Pipeline Stages Explained

The `Jenkinsfile` includes these stages:

### Checkout
- Clones the repository
- Displays recent commits

### Environment Setup
- Verifies Python and Node.js versions

### Backend Dependencies
- Creates Python virtual environment
- Installs dependencies from `requirements.txt`
- Installs testing tools (pytest, pytest-cov)

### Frontend Dependencies
- Installs npm packages
- Installs testing libraries (vitest, @testing-library/react)

### Backend Linting
- Runs flake8 for code quality
- Checks code formatting with black

### Frontend Linting
- Runs ESLint (if configured)

### Backend Unit Tests
- Runs pytest with coverage reports
- Generates HTML coverage report

### Frontend Unit Tests
- Runs Jest/Vitest tests
- Generates coverage reports

### Security Scan
- Checks Python dependencies for vulnerabilities (safety)
- Checks npm dependencies (npm audit)

### Build Docker Images
- Builds backend Docker image
- Tags with build number and latest

### Docker Compose Validation
- Validates `docker-compose.yml` syntax

### Archive Reports
- Archives test and coverage reports
- Publishes HTML coverage reports

## 4. Running Tests Locally

### Backend Tests

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-flask

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py -v

# Run specific test class
pytest tests/test_app.py::TestHealthEndpoint -v

# Run specific test
pytest tests/test_app.py::TestHealthEndpoint::test_health_endpoint -v
```

### Frontend Tests

```bash
# Install dependencies
cd frontend
npm install
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom

# Run tests
npm run test

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

## 5. Setting Up GitHub Webhook

### For Automatic Build Triggering

1. Go to GitHub repository settings
2. Click **"Webhooks"** → **"Add webhook"**
3. **Payload URL**: `http://your-jenkins-server:8090/github-webhook/`
4. **Content type**: `application/json`
5. **Events**: Select "Push events" and "Pull requests"
6. Click **"Add webhook"**

### Verify Webhook

1. In Jenkins, go to **Manage Jenkins** → **Configure System**
2. Scroll to **GitHub** section
3. Add GitHub server
4. Test connection

## 6. Accessing Test Reports

### During Build
1. Click on build number in Jenkins
2. Click **"Coverage Report"** (if published)
3. View HTML coverage reports for Python code

### After Build Completes
- **Console Output**: Full build logs at `http://localhost:8090/job/RealtimeASR-Pipeline/[BUILD_NUMBER]/console`
- **Test Results**: Parsed JUnit test results
- **Coverage**: HTML reports in `htmlcov/` directory

## 7. Troubleshooting

### Build Fails at Python Dependencies

**Error**: `pip: command not found`

**Solution**:
```bash
# Ensure Python is in PATH
which python3
# Or use system Python path
/usr/bin/python3 -m pip install -r requirements.txt
```

### Build Fails at Docker Build

**Error**: `docker: command not found`

**Solution**:
- Ensure Docker is installed on Jenkins server
- Add Jenkins user to docker group: `sudo usermod -aG docker jenkins`
- Restart Jenkins: `sudo systemctl restart jenkins`

### FFmpeg Timeout Issues

**Error**: `ffmpeg conversion failed: Command timed out`

**Solution**: Increase timeout in `process_webm_audio()` or rebuild container with better resources.

### Tests Pass Locally But Fail in Jenkins

**Causes**:
- Different environment (Python version, missing packages)
- Missing .env file
- Database connection issues

**Solutions**:
- Check Jenkins environment variables
- Ensure test database is accessible
- Review logs at `http://localhost:8090/job/RealtimeASR-Pipeline/[BUILD_NUMBER]/console`

## 8. Performance Optimization

### Cache Dependencies

Add to Jenkinsfile (after `Checkout` stage):

```groovy
stage('Cache Dependencies') {
    steps {
        script {
            // Python cache
            sh 'pip cache purge || true'
            
            // npm cache
            sh 'cd frontend && npm cache clean --force || true'
        }
    }
}
```

### Parallel Execution

Modify Jenkinsfile for parallel stages:

```groovy
stage('Tests') {
    parallel {
        stage('Backend Tests') {
            steps { /* ... */ }
        }
        stage('Frontend Tests') {
            steps { /* ... */ }
        }
    }
}
```

## 9. Advanced Configuration

### Email Notifications

Add to `post` section in Jenkinsfile:

```groovy
post {
    always {
        emailext(
            subject: "Build ${BUILD_NUMBER}: ${currentBuild.result}",
            body: "Build log: ${BUILD_LOG}",
            to: "your-email@example.com"
        )
    }
}
```

### Slack Notifications

Install Slack plugin, then add:

```groovy
post {
    always {
        slackSend(
            channel: '#ci-builds',
            message: "Build #${BUILD_NUMBER} ${currentBuild.result}",
            color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger'
        )
    }
}
```

### SonarQube Integration

Add SonarQube step:

```groovy
stage('Code Quality') {
    steps {
        sh '''
            sonar-scanner \\
              -Dsonar.projectKey=RealtimeASR \\
              -Dsonar.host.url=http://localhost:9000 \\
              -Dsonar.login=YOUR_TOKEN
        '''
    }
}
```

## 10. Maintenance

### Clean Up Old Builds

1. Go to **Pipeline configuration**
2. Under **Options**, set:
   - Keep builds: 30 days
   - Max builds to keep: 50

### Monitor Jenkins Health

- Visit `http://localhost:8090/systeminfo`
- Check disk space: `df -h`
- Check running processes: `ps aux | grep jenkins`

## Additional Resources

- [Jenkins Official Docs](https://www.jenkins.io/doc/)
- [Jenkinsfile Documentation](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Docker in Jenkins](https://www.jenkins.io/doc/book/installing-jenkins/docker/)

## Quick Start Command

To trigger a build from command line:

```bash
curl -X POST http://localhost:8090/job/RealtimeASR-Pipeline/build \\
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

Get API token from Jenkins user settings: `http://localhost:8090/user/admin/configure`
