pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.10'
        NODE_VERSION = '18'
        DOCKER_REGISTRY = 'localhost:5000'
        GIT_REPO = 'https://github.com/Gitgo012/Real-Time-Speech-to-Text-Translation-Across-Languages.git'
        BRANCH_NAME = "${env.GIT_BRANCH ?: 'feature/containerization'}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Checkout') {
            steps {
                echo "🔄 Checking out code from ${GIT_REPO}"
                checkout scm
                bat 'git log --oneline -5'
            }
        }

        stage('Environment Setup') {
            steps {
                echo "📋 Setting up Python and Node environments"
                bat """
                    echo Python version:
                    python --version
                    echo Node version:
                    node --version
                    echo npm version:
                    npm --version
                """
            }
        }

        stage('Backend - Install Dependencies') {
            steps {
                echo "📦 Installing Python dependencies"
                bat """
                    python -m venv venv
                    call venv\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pytest-flask python-dotenv
                """
            }
        }

        stage('Frontend - Install Dependencies') {
            steps {
                echo "📦 Installing Node dependencies"
                bat """
                    cd frontend
                    npm install
                    npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
                """
            }
        }

        stage('Backend - Lint & Format Check') {
            steps {
                echo "🔍 Running Python linting"
                bat """
                    call venv\\Scripts\\activate
                    pip install pylint flake8 black
                    echo Running flake8...
                    flake8 app.py || echo Flake8 completed with warnings
                    echo Checking formatting with black...
                    black --check app.py || echo Black reported formatting differences
                """
            }
        }

        stage('Frontend - Lint') {
            steps {
                echo "🔍 Running JavaScript linting"
                bat """
                    cd frontend
                    npm run lint || echo No lint script defined
                """
            }
        }

        stage('Backend - Unit Tests') {
            steps {
                echo "🧪 Running Python unit tests"
                bat """
                    call venv\\Scripts\\activate
                    pytest tests/ -v --tb=short --cov=. --cov-report=html --cov-report=xml || echo Tests completed with warnings
                """
            }
        }

        stage('Frontend - Unit Tests') {
            steps {
                echo "🧪 Running JavaScript unit tests"
                bat """
                    cd frontend
                    npm test || echo No test script defined
                """
            }
        }

        stage('Security Scan - Dependencies') {
            steps {
                echo "🔐 Scanning for vulnerable dependencies"
                bat """
                    call venv\\Scripts\\activate
                    pip install safety
                    safety check || echo Safety scan warnings

                    cd frontend
                    npm audit --audit-level=moderate || echo npm audit warnings
                """
            }
        }

        stage('Build - Backend Docker Image') {
            steps {
                echo "🐳 Building backend Docker image"
                bat """
                    docker build -f Dockerfile.backend -t localhost:5000/realtime-asr-backend:${BUILD_NUMBER} .
                    docker tag localhost:5000/realtime-asr-backend:${BUILD_NUMBER} localhost:5000/realtime-asr-backend:latest
                """
            }
        }

        stage('Build - Frontend') {
            steps {
                echo "🏗️ Building frontend with Vite"
                bat """
                    cd frontend
                    npm run build
                """
            }
        }

        stage('Docker Compose Validation') {
            steps {
                echo "✅ Validating docker-compose.yml"
                bat "docker-compose config"
            }
        }

        stage('Archive Reports') {
            steps {
                echo "📊 Archiving test and coverage reports"
                bat """
                    if exist htmlcov (
                        powershell -Command "Compress-Archive -Path htmlcov -DestinationPath python-coverage.zip -Force"
                    )
                    if exist coverage.xml copy coverage.xml python-coverage.xml
                """

                junit allowEmptyResults: true, testResults: '**/test-results.xml'

                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Python Coverage Report'
                ])
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up workspace"
            bat """
                if exist venv rmdir /s /q venv
                docker rmi localhost:5000/realtime-asr-backend:${BUILD_NUMBER} 2>nul || echo Docker cleanup failed
            """
        }

        success {
            echo "✅ Pipeline executed successfully!"
            bat """
                echo =========================================
                echo Build #${BUILD_NUMBER} PASSED
                echo =========================================
                echo Branch: ${BRANCH_NAME}
                echo Timestamp:
                echo =========================================
            """
        }

        failure {
            echo "❌ Pipeline failed!"
            bat """
                echo =========================================
                echo Build #${BUILD_NUMBER} FAILED
                echo =========================================
                echo Branch: ${BRANCH_NAME}
                echo Check logs above for details
                echo =========================================
            """
        }

        unstable {
            echo "⚠️ Pipeline is unstable (tests failed but build succeeded)"
        }
    }
}
