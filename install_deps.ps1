# PowerShell script to install dependencies in virtual environment
# Usage: .\install_deps.ps1

Write-Host "Checking for virtual environment..." -ForegroundColor Green

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

Write-Host "Installing Flask and core dependencies..." -ForegroundColor Green
pip install Flask==2.3.3 Flask-SocketIO==5.5.1 Flask-PyMongo==2.3.0 Flask-Bcrypt==1.0.1 Flask-Session==0.5.0 authlib==1.2.1 python-dotenv==1.0.0
Write-Host "Note: eventlet not installed (not compatible with Python 3.13). Using threading mode." -ForegroundColor Yellow

Write-Host "Installing ML/AI dependencies (this may take a while)..." -ForegroundColor Green
pip install torch==2.7.1 torchaudio==2.7.1 transformers soundfile numpy sentencepiece tokenizers

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "To start the app, run: .\start_app.ps1" -ForegroundColor Cyan

