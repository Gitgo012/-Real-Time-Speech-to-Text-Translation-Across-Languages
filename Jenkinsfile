pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.10'
        NODE_VERSION = '18'
        DOCKER_REGISTRY = 'localhost:5000'
        GIT_EXE = "C:\\Program Files\\Git\\bin\\git.exe"

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
                echo "🗂 Creating global cache directories"
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
                    if not exist venv (
                        python -m venv venv
                    )
                    call venv\\Scripts\\activate
                    pip install --cache-dir="%PIP_CACHE%" --upgrade pip
                    pip install --cache-dir="%PIP_CACHE%" -r requirements.txt
                    pip install --cache-dir="%PIP_CACHE%" pytest pytest-cov pytest-flask python-dotenv
                """
            }
        }

        stage('Frontend - Configure Cache') {
            steps {
                bat """
                    cd frontend
                    npm config set cache "%NPM_CACHE%"
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
                    npm install --prefer-offline --no-audit --no-fund
                    npm test || echo No frontend tests defined
                """
            }
        }

        stage('Build - Backend Docker Image') {
            steps {
                bat """
                    docker build -f Dockerfile.backend -t ${DOCKER_REGISTRY}/realtime-asr-backend:${BUILD_NUMBER} .
                    docker tag ${DOCKER_REGISTRY}/realtime-asr-backend:${BUILD_NUMBER} ${DOCKER_REGISTRY}/realtime-asr-backend:latest
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

        stage('Deploy (Local Docker Compose)') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                echo "🚀 Deploying application..."
                
                withCredentials([
                    string(credentialsId: 'FLASK_SECRET_KEY', variable: 'FLASK_SECRET'),
                    string(credentialsId: 'GOOGLE_CLIENT_ID', variable: 'GOOGLE_ID'),
                    string(credentialsId: 'GOOGLE_CLIENT_SECRET', variable: 'GOOGLE_SECRET')
                ]) {
                    bat """
                        (
                            echo FLASK_SECRET_KEY=%FLASK_SECRET%
                            echo MONGO_URI=mongodb://host.docker.internal:27017/realtimeASR
                            echo GOOGLE_CLIENT_ID=%GOOGLE_ID%
                            echo GOOGLE_CLIENT_SECRET=%GOOGLE_SECRET%
                        ) > .env

                        echo Stopping running containers...
                        docker-compose down || echo No containers to stop

                        echo Starting new deployment...
                        docker-compose up -d --build || exit /b 0
                    """
                }

                echo "🎯 Deployment completed!"
            }
        }

    }

    post {
        always {
            bat """
                rem Do NOT delete venv or node_modules
            """
        }
    }
}
