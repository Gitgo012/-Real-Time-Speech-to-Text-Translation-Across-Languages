@echo off
REM Quick start script for setting up Jenkins pipeline (Windows)

setlocal enabledelayedexpansion

echo ===============================================
echo Real-Time Speech-to-Text Translation
echo Jenkins Pipeline Setup ^(Windows^)
echo ===============================================
echo.

REM Check if Jenkins is running
echo Checking if Jenkins is running on port 8090...
timeout /t 1 /nobreak > nul
curl -s http://localhost:8090 > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Jenkins is running
) else (
    echo [ERROR] Jenkins is NOT running on localhost:8090
    echo Please start Jenkins first:
    echo   Windows Service: services.msc ^(search for Jenkins^)
    echo   Docker: docker run -p 8090:8080 jenkins/jenkins:latest
    pause
    exit /b 1
)

echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python !PYTHON_VERSION! found
) else (
    echo [ERROR] Python 3 not found
    pause
    exit /b 1
)

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('node --version') do set NODE_VERSION=%%i
    echo [OK] Node.js !NODE_VERSION! found
) else (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)

REM Check Git
echo Checking Git installation...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('git --version') do set GIT_VERSION=%%i
    echo [OK] !GIT_VERSION!
) else (
    echo [ERROR] Git not found
    pause
    exit /b 1
)

REM Check Docker (optional)
echo Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VERSION=%%i
    echo [OK] !DOCKER_VERSION!
) else (
    echo [INFO] Docker not found ^(optional, needed for Docker builds^)
)

echo.
echo Installing dependencies...

REM Backend dependencies
echo Installing Python dependencies...
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat

python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pytest pytest-cov pytest-flask python-dotenv -q

echo [OK] Backend dependencies installed

REM Frontend dependencies
echo Installing Node.js dependencies...
cd frontend
call npm install --legacy-peer-deps -q 2>nul || call npm install -q
call npm install --save-dev vitest @testing-library/react @testing-library/jest-dom -q 2>nul || echo.
cd ..

echo [OK] Frontend dependencies installed

echo.
echo Running local tests...

REM Run backend tests
echo Running backend tests...
call pytest tests/ -q --tb=line 2>nul || echo Some tests may have failed

REM Run frontend tests
echo Running frontend tests...
cd frontend
call npm run test 2>nul || echo Frontend tests skipped
cd ..

echo.
echo ===============================================
echo Setup Complete!
echo ===============================================
echo.
echo Next steps:
echo 1. Go to http://localhost:8090
echo 2. Create a new Pipeline job:
echo    - New Item ^> Pipeline
echo    - Name: RealtimeASR-Pipeline
echo    - Pipeline ^> Definition: Pipeline script from SCM
echo    - SCM: Git
echo    - Repository: https://github.com/Gitgo012/Real-Time-Speech-to-Text-Translation-Across-Languages.git
echo    - Script Path: Jenkinsfile
echo.
echo 3. Click 'Build Now' to trigger the first build
echo.
echo For detailed setup instructions, see: JENKINS_SETUP.md
echo.

pause
