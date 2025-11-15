# Testing Guide - React Frontend Application

## Prerequisites Check

Before testing, ensure you have:
1. ✅ Python virtual environment activated
2. ✅ All Python dependencies installed
3. ✅ Node.js and npm installed
4. ✅ MongoDB running (if using database)
5. ✅ ffmpeg installed (optional but recommended for audio)

## Quick Start Testing

### Step 1: Start Flask Backend

Open **Terminal 1** (PowerShell):

```powershell
# Navigate to project directory
cd "E:\Capstone Project Frontend\-Real-Time-Speech-to-Text-Translation-Across-Languages"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Flask server
python app.py
```

**Expected Output:**
```
Loading models...
Loading ASR model (Whisper-medium)...
ASR model loaded successfully
Loading M2M100 multilingual translation model...
M2M100 model loaded successfully
Starting Flask-SocketIO server on http://0.0.0.0:5000
```

**Note:** Model loading may take 2-5 minutes on first run.

### Step 2: Start React Development Server

Open **Terminal 2** (PowerShell):

```powershell
# Navigate to frontend directory
cd "E:\Capstone Project Frontend\-Real-Time-Speech-to-Text-Translation-Across-Languages\frontend"

# Install dependencies (if not already done)
npm install

# Start React dev server
npm run dev
```

**Expected Output:**
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 3: Access the Application

Open your browser and go to:
```
http://localhost:5173
```

## Testing Checklist

### ✅ 1. Sign Up Page

**URL:** `http://localhost:5173/signup`

**Test Steps:**
1. Fill in "Full name" field
2. Fill in "Email" field
3. Fill in "Password" field (min 6 characters)
4. Fill in "Confirm your password" field
5. Click "Sign Up" button

**Expected Results:**
- ✅ Form validates all fields
- ✅ Passwords match validation
- ✅ Success: Redirects to dashboard
- ✅ Error: Shows error message if username exists

**Test Cases:**
- [ ] Valid registration → Should redirect to dashboard
- [ ] Duplicate email → Should show error
- [ ] Password mismatch → Should show error
- [ ] Empty fields → Should show validation error

### ✅ 2. Login Page

**URL:** `http://localhost:5173/login`

**Test Steps:**
1. Enter registered email
2. Enter password
3. Click "Login" button

**Expected Results:**
- ✅ Valid credentials → Redirects to dashboard
- ✅ Invalid credentials → Shows error message
- ✅ "Forgot Password?" link visible (not functional yet)
- ✅ Social login buttons visible

**Test Cases:**
- [ ] Valid login → Should redirect to dashboard
- [ ] Invalid credentials → Should show error
- [ ] Google login button → Should redirect to Google OAuth
- [ ] Apple login button → Placeholder (not implemented)
- [ ] "Sign Up" link → Should navigate to signup page

### ✅ 3. Dashboard Page

**URL:** `http://localhost:5173/dashboard`

**Test Steps:**

#### 3.1 Language Selection
1. Check "Source Language" dropdown
2. Check "Target Language" dropdown
3. Select different languages

**Expected Results:**
- ✅ Dropdowns populated with available languages
- ✅ Default: Source = English (US), Target = Spanish
- ✅ Can change languages when not recording

#### 3.2 Recording Functionality
1. Select a target language
2. Click "Start Recording" button
3. Speak into microphone
4. Click "Stop Recording" button

**Expected Results:**
- ✅ Microphone permission prompt appears
- ✅ "Start Recording" button changes to "Stop Recording"
- ✅ Status shows "Recording..."
- ✅ Original text shows "Listening..."
- ✅ Translated text shows "Translating..."
- ✅ After stopping, results appear in text panels

**Test Cases:**
- [ ] Start recording → Should request mic permission
- [ ] Speak → Should process audio
- [ ] Stop recording → Should show transcript and translation
- [ ] Multiple recordings → Should work repeatedly
- [ ] Language change → Should affect translation

#### 3.3 Text Display
1. After recording, check "Original Text" panel
2. Check "Translated Text" panel

**Expected Results:**
- ✅ Original text displays transcribed speech
- ✅ Translated text displays translation
- ✅ Text is readable and formatted
- ✅ Placeholder text disappears when results arrive

#### 3.4 Translation History
1. Make several recordings
2. Check right sidebar "Translation History"

**Expected Results:**
- ✅ History items appear with timestamps
- ✅ Shows language pair (e.g., "English → Spanish")
- ✅ Shows original and translated text
- ✅ "Clear History" button appears when history exists
- ✅ Can scroll through history

**Test Cases:**
- [ ] History appears after recording
- [ ] Timestamps are correct
- [ ] Language pairs are correct
- [ ] Clear History → Should remove all items
- [ ] Multiple items → Should show in reverse chronological order

#### 3.5 Header Features
1. Check app title "🎤 Real-Time STT Translation"
2. Click "Logout" button
3. Check user profile icon

**Expected Results:**
- ✅ Header displays correctly
- ✅ Logout button works
- ✅ User profile icon visible

### ✅ 4. WebSocket Connection

**Test Steps:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Navigate to dashboard
4. Check for WebSocket connection messages

**Expected Results:**
- ✅ No WebSocket errors in console
- ✅ Connection established
- ✅ Language list received
- ✅ Transcription results received

**Test Cases:**
- [ ] WebSocket connects → Should see connection message
- [ ] Languages loaded → Should populate dropdowns
- [ ] Audio sent → Should receive transcription
- [ ] Errors handled → Should show error messages

### ✅ 5. Error Handling

**Test Cases:**
- [ ] No target language selected → Should show alert
- [ ] Microphone denied → Should show error
- [ ] Network error → Should handle gracefully
- [ ] Server error → Should display error message

## Production Mode Testing

### Build and Test Production Build

```powershell
# Terminal 1: Build React
cd frontend
npm run build

# Terminal 2: Start Flask (serves React build)
cd "E:\Capstone Project Frontend\-Real-Time-Speech-to-Text-Translation-Across-Languages"
.\venv\Scripts\Activate.ps1
python app.py
```

**Access at:** `http://localhost:5000`

**Test:** All features should work the same as development mode.

## Troubleshooting

### Issue: React dev server won't start
**Solution:**
```powershell
cd frontend
npm install
npm run dev
```

### Issue: Flask can't find React build
**Solution:**
```powershell
cd frontend
npm run build
```

### Issue: WebSocket connection fails
**Check:**
- Flask server is running on port 5000
- Vite proxy is configured correctly
- No firewall blocking connections

### Issue: Audio recording doesn't work
**Check:**
- Microphone permissions granted
- Browser supports MediaRecorder API
- ffmpeg installed (for best results)

### Issue: Models not loading
**Check:**
- Internet connection (for downloading models)
- Sufficient disk space
- Python dependencies installed

## Browser Compatibility

Tested browsers:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari (may have WebSocket limitations)

## Performance Testing

1. **Multiple Recordings:**
   - Record 10+ times in succession
   - Check for memory leaks
   - Verify history doesn't slow down

2. **Long Recordings:**
   - Record for 30+ seconds
   - Verify processing completes

3. **Language Switching:**
   - Switch languages multiple times
   - Verify translations update correctly

## Security Testing

- [ ] Session persists after page refresh
- [ ] Logout clears session
- [ ] Protected routes redirect to login
- [ ] API endpoints require authentication

## Next Steps After Testing

1. Report any bugs or issues
2. Test on different browsers
3. Test on mobile devices (responsive design)
4. Performance optimization if needed

