# Quick Test Script for React Frontend
# Usage: .\test-react.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "React Frontend Testing Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "frontend")) {
    Write-Host "ERROR: frontend directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Starting Flask Backend..." -ForegroundColor Green
Write-Host "  → Open a NEW terminal and run:" -ForegroundColor Yellow
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "     python app.py" -ForegroundColor White
Write-Host ""

Write-Host "Step 2: Starting React Dev Server..." -ForegroundColor Green
Write-Host "  → In THIS terminal, run:" -ForegroundColor Yellow
Write-Host "     cd frontend" -ForegroundColor White
Write-Host "     npm run dev" -ForegroundColor White
Write-Host ""

Write-Host "Step 3: Access the Application" -ForegroundColor Green
Write-Host "  → Open browser: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""

Write-Host "Testing Checklist:" -ForegroundColor Cyan
Write-Host "  [ ] Sign Up page loads correctly" -ForegroundColor White
Write-Host "  [ ] Create a new account" -ForegroundColor White
Write-Host "  [ ] Login page works" -ForegroundColor White
Write-Host "  [ ] Dashboard loads with language dropdowns" -ForegroundColor White
Write-Host "  [ ] Start recording (grant microphone permission)" -ForegroundColor White
Write-Host "  [ ] Speak and stop recording" -ForegroundColor White
Write-Host "  [ ] See transcript and translation" -ForegroundColor White
Write-Host "  [ ] Check translation history" -ForegroundColor White
Write-Host ""

Write-Host "For detailed testing guide, see: TESTING_GUIDE.md" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to start React dev server now
$response = Read-Host "Do you want to start React dev server now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "Starting React dev server..." -ForegroundColor Green
    Write-Host "Make sure Flask is running in another terminal first!" -ForegroundColor Yellow
    Write-Host ""
    cd frontend
    npm run dev
}

