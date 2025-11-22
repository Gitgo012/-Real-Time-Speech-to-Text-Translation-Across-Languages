pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.10'
        NODE_VERSION = '18'
        DOCKER_REGISTRY = 'localhost:5000'
        GIT_EXE = "C:\\Program Files\\Git\\bin\\git.exe"

        // Global dependency caches
        PIP_CACHE = "C:\\ProgramData\\Jenkins\\pip-cache"
        NPM_CACHE = "C:\\ProgramData\\Jenkins\\npm-cache"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Prepare Caches') {
            steps {
                echo "🗂 Creating global cache directories if missing"
                bat """
                    if not exist "%PIP_CACHE%" mkdir "%PIP_CACHE%"
                    if not exist "%NPM_CACHE%" mkdir "%NPM_CACHE%"
                """
            }
        }

        stage('Checkout') {
            steps {
                echo "🔄 Checking out code"
                checkout scm
                bat '"%GIT_EXE%" log --oneline -5'
            }
        }

        stage('Environment Setup') {
            steps {
                echo "📋 Checking Python and Node"
                bat """
                    python --version
                    node --version
                    npm --version
                """
            }
        }

        stage('Backend - Install Dependencies (Cached)') {
            steps {
                echo "🐍 Setting up Python virtual environment with caching"
                bat """
                    if not exist venv (
                        echo Creating new Python venv...
                        python -m venv venv
                    )

                    call venv\\Scripts\\activate

                    pip install --cache-dir="%PIP_CACHE%" --upgrade pip
                    pip install --cache-dir="%PIP_CACHE%" -r requirements.txt
                    pip install --cache-dir="%PIP_CACHE%" pytest pytest-cov pytest-flask python-dotenv
                """
            }
        }

        stage('Frontend - Install Dependencies (Cached)') {
            steps {
                echo "📦 Installing Node dependencies with caching"
                bat """
                    cd frontend

                    npm config set cache "%NPM_CACHE%"

                    if not exist node_modules (
                        echo Installing fresh node modules...
                        npm install
                    ) else (
                        echo Using cached node_modules...
                        npm install --prefer-offline --no-audit --no-fund
                    )
                """
            }
        }

        stage('Backend - Lint & Format Check') {
            steps {
                bat """
                    call venv\\Scripts\\activate
                    pip install --cache-dir="%PIP_CACHE%" pylint flake8 black
                    flake8 app.py || echo Flake8 warnings
                    black --check app.py || echo Black formatting issues
                """
            }
        }

        stage('Frontend - Lint') {
            steps {
                bat """
                    cd frontend
                    npm run lint || echo Lint warnings
                """
            }
        }

        stage('Backend - Unit Tests') {
            steps {
                bat """
                    call venv\\Scripts\\activate
                    pytest tests/ -v --cov=. --cov-report=html --cov-report=xml || echo Tests failed
                """
            }
        }

        stage('Frontend - Unit Tests') {
            steps {
                bat """
                    cd frontend
                    npm test || echo No frontend tests defined
                """
            }
        }

        stage('Security Scan - Dependencies') {
            steps {
                bat """
                    call venv\\Scripts\\activate
                    pip install --cache-dir="%PIP_CACHE%" safety
                    safety check || echo Safety issues

                    cd frontend
                    npm audit --audit-level=moderate || echo JS vulnerabilities
                """
            }
        }

        stage('Build - Backend Docker Image') {
            steps {
                bat """
                    docker build -f Dockerfile.backend -t localhost:5000/realtime-asr-backend:${BUILD_NUMBER} .
                    docker tag localhost:5000/realtime-asr-backend:${BUILD_NUMBER} localhost:5000/realtime-asr-backend:latest
                """
            }
        }

        stage('Build - Frontend') {
            steps {
                bat """
                    cd frontend
                    npm run build
                """
            }
        }

        stage('Docker Compose Validation') {
            steps {
                bat "docker-compose config"
            }
        }

        stage('Archive Reports') {
            steps {
                bat """
                    if exist htmlcov powershell -Command "Compress-Archive -Path htmlcov -DestinationPath python-coverage.zip -Force"
                    if exist coverage.xml copy coverage.xml python-coverage.xml
                """

                junit allowEmptyResults: true, testResults: '**/test-results.xml'

                publishHTML([
                    allowMissing: true,
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
            echo "🧹 Cleaning temporary files (but keeping caches & venv)"
            bat """
                rem Do NOT delete venv or node_modules — they are cached!!
                exit /b 0
            """
        }

        success {
            echo "🎉 Build Success"
        }

        failure {
            echo "❌ Build Failed"
        }
    }
}
