# PowerShell script to activate venv and start Flask app
# Usage: .\start_app.ps1

Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Virtual environment not found. Please run: python -m venv venv" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Flask application..." -ForegroundColor Green
Write-Host "The app will be available at http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python app.py

