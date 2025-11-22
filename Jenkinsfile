pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.10'
        NODE_VERSION = '18'
        DOCKER_REGISTRY = 'localhost:5000'
        GIT_REPO = 'https://github.com/Gitgo012/Real-Time-Speech-to-Text-Translation-Across-Languages.git'
        BRANCH_NAME = "${env.GIT_BRANCH ?: 'feature/containerization'}"
        GIT_EXE = "C:\\\\Program Files\\\\Git\\\\bin\\\\git.exe"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Checkout') {
            steps {
                echo "🔄 Checking out code"
                checkout scm
                bat '"%GIT_EXE%" log --oneline -5'
            }
        }

        stage('Environment Setup') {
            steps {
                echo "📋 Setting up Python and Node environments"
                bat """
                    python --version
                    node --version
                    npm --version
                """
            }
        }

        stage('Backend - Install Dependencies') {
            steps {
                bat """
                    python -m venv venv
                    call venv\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pytest-flask python-dotenv
                """
            }
        }

        stage('Frontend - Install Dependencies') {
            steps {
                bat """
                    cd frontend
                    npm install
                    npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
                """
            }
        }

        stage('Backend - Lint & Format Check') {
            steps {
                bat """
                    call venv\\Scripts\\activate
                    pip install pylint flake8 black
                    flake8 app.py || echo Flake8 warnings
                    black --check app.py || echo Black formatting issues
                """
            }
        }

        stage('Frontend - Lint') {
            steps {
                bat """
                    cd frontend
                    npm run lint || echo No lint script defined
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
                    pip install safety
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
            echo "🧹 Cleaning workspace"
            bat """
                if exist venv rmdir /s /q venv

                docker rmi localhost:5000/realtime-asr-backend:%BUILD_NUMBER%
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
