# Quick Start Testing Guide

## 🚀 Fastest Way to Test

### Option 1: Use the Test Script

```powershell
.\test-react.ps1
```

This script will guide you through the testing process.

### Option 2: Manual Steps

#### Terminal 1 - Flask Backend
```powershell
.\venv\Scripts\Activate.ps1
python app.py
```
**Wait for:** "Starting Flask-SocketIO server on http://0.0.0.0:5000"

#### Terminal 2 - React Frontend
```powershell
cd frontend
npm run dev
```
**Wait for:** "Local: http://localhost:5173/"

#### Browser
Open: **http://localhost:5173**

## 🧪 Quick Test Flow

1. **Sign Up**
   - Go to `/signup`
   - Fill form and create account
   - Should redirect to dashboard

2. **Dashboard**
   - Select target language (e.g., Spanish)
   - Click "Start Recording"
   - Grant microphone permission
   - Speak something
   - Click "Stop Recording"
   - See transcript and translation appear

3. **History**
   - Check right sidebar
   - See your translation history
   - Try "Clear History"

## ⚠️ Common Issues

**Problem:** React dev server shows connection error
- **Solution:** Make sure Flask is running first on port 5000

**Problem:** Microphone not working
- **Solution:** Check browser permissions, allow microphone access

**Problem:** No languages in dropdown
- **Solution:** Wait for models to load (check Flask terminal for "ASR model loaded")

**Problem:** Audio processing error
- **Solution:** Install ffmpeg (optional but recommended)

## 📋 Full Testing Guide

See `TESTING_GUIDE.md` for comprehensive testing instructions.

