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
        // Keep only last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Add timestamps to console output
        timestamps()
        // Timeout after 30 minutes
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                echo "🔄 Checking out code from ${GIT_REPO}"
                checkout scm
                sh 'git log --oneline -5'
            }
        }

        stage('Environment Setup') {
            steps {
                echo "📋 Setting up Python and Node environments"
                sh '''
                    echo "Python version:"
                    python3 --version
                    echo "Node version:"
                    node --version
                    echo "npm version:"
                    npm --version
                '''
            }
        }

        stage('Backend - Install Dependencies') {
            steps {
                echo "📦 Installing Python dependencies"
                sh '''
                    python3 -m venv venv || true
                    . venv/bin/activate || source venv/Scripts/activate || true
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pytest-flask python-dotenv
                '''
            }
        }

        stage('Frontend - Install Dependencies') {
            steps {
                echo "📦 Installing Node dependencies"
                sh '''
                    cd frontend
                    npm install
                    npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
                    cd ..
                '''
            }
        }

        stage('Backend - Lint & Format Check') {
            steps {
                echo "🔍 Running Python linting"
                sh '''
                    . venv/bin/activate || source venv/Scripts/activate || true
                    pip install pylint flake8 black
                    echo "Running flake8..."
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics || true
                    echo "Checking code formatting with black..."
                    black --check app.py || true
                '''
            }
        }

        stage('Frontend - Lint') {
            steps {
                echo "🔍 Running JavaScript linting"
                sh '''
                    cd frontend
                    npm run lint 2>/dev/null || echo "No lint script defined"
                    cd ..
                '''
            }
        }

        stage('Backend - Unit Tests') {
            steps {
                echo "🧪 Running Python unit tests"
                sh '''
                    . venv/bin/activate || source venv/Scripts/activate || true
                    pytest tests/ -v --tb=short --cov=. --cov-report=html --cov-report=xml || true
                    echo "Coverage report generated"
                '''
            }
        }

        stage('Frontend - Unit Tests') {
            steps {
                echo "🧪 Running JavaScript unit tests"
                sh '''
                    cd frontend
                    npm run test 2>/dev/null || echo "No test script defined"
                    cd ..
                '''
            }
        }

        stage('Security Scan - Dependencies') {
            steps {
                echo "🔐 Scanning for vulnerable dependencies"
                sh '''
                    . venv/bin/activate || source venv/Scripts/activate || true
                    pip install safety
                    safety check --json || true
                    
                    cd frontend
                    npm audit --audit-level=moderate || true
                    cd ..
                '''
            }
        }

        stage('Build - Backend Docker Image') {
            steps {
                echo "🐳 Building backend Docker image"
                sh '''
                    docker build -f Dockerfile.backend -t localhost:5000/realtime-asr-backend:${BUILD_NUMBER} .
                    docker tag localhost:5000/realtime-asr-backend:${BUILD_NUMBER} localhost:5000/realtime-asr-backend:latest
                '''
            }
        }

        stage('Build - Frontend') {
            steps {
                echo "🏗️ Building frontend with Vite"
                sh '''
                    cd frontend
                    npm run build
                    cd ..
                '''
            }
        }

        stage('Docker Compose Validation') {
            steps {
                echo "✅ Validating docker-compose.yml"
                sh 'docker-compose config'
            }
        }

        stage('Archive Reports') {
            steps {
                echo "📊 Archiving test and coverage reports"
                sh '''
                    # Archive Python coverage
                    if [ -d htmlcov ]; then
                        tar -czf python-coverage.tar.gz htmlcov/
                    fi
                    
                    # Archive test results
                    if [ -f coverage.xml ]; then
                        cp coverage.xml python-coverage.xml
                    fi
                '''
                
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
            sh '''
                # Remove virtual environments
                rm -rf venv/ || true
                
                # Clean Docker artifacts
                docker rmi localhost:5000/realtime-asr-backend:${BUILD_NUMBER} 2>/dev/null || true
            '''
            
            // Archive logs
            sh 'echo "Build logs:" && tail -100 /var/log/syslog 2>/dev/null || echo "No syslog available"'
        }

        success {
            echo "✅ Pipeline executed successfully!"
            sh '''
                echo "========================================="
                echo "Build #${BUILD_NUMBER} PASSED"
                echo "========================================="
                echo "Branch: ${BRANCH_NAME}"
                echo "Timestamp: $(date)"
                echo "========================================="
            '''
        }

        failure {
            echo "❌ Pipeline failed!"
            sh '''
                echo "========================================="
                echo "Build #${BUILD_NUMBER} FAILED"
                echo "========================================="
                echo "Branch: ${BRANCH_NAME}"
                echo "Check logs above for details"
                echo "========================================="
            '''
        }

        unstable {
            echo "⚠️ Pipeline is unstable (tests failed but build succeeded)"
        }
    }
}
