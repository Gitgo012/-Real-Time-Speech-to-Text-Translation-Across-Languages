# React Frontend Setup

## Overview
The application now has a React frontend that matches the Figma design, replacing the vanilla HTML/CSS/JS implementation.

## Structure

### Frontend (`frontend/`)
- **Pages**: SignUp, Login, Dashboard
- **Components**: All components are in `src/pages/`
- **Styling**: Each page has its own CSS file matching the Figma design

### Features Implemented

1. **Sign Up Page**
   - Full name, email, password, confirm password fields
   - Clean white card design
   - Error handling

2. **Login Page**
   - Email and password fields
   - "Forgot Password?" link
   - Social login buttons (Google, Apple)
   - Divider with "Or" text

3. **Dashboard Page**
   - Header with app title, logout button, user profile icon
   - Speech Input section:
     - Source Language dropdown (default: English US)
     - Target Language dropdown (default: Spanish)
     - Start/Stop Recording buttons
   - Original Text panel (left side)
   - Translated Text panel (left side)
   - Translation History sidebar (right side)
   - Real-time WebSocket communication
   - Audio recording functionality

## Development Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Development Mode
Run React dev server (with proxy to Flask):
```bash
cd frontend
npm run dev
```
This will start Vite dev server on `http://localhost:5173` with proxy to Flask backend.

### 3. Production Build
Build React app for production:
```bash
cd frontend
npm run build
```
This creates `frontend/dist/` with production-ready files.

### 4. Run Flask with React
After building, Flask will automatically serve the React app:
```bash
python app.py
```
Flask will serve the React build from `frontend/dist/` on `http://localhost:5000`.

## API Endpoints

The Flask backend now supports both form-based and JSON API requests:

- `POST /api/register` - Register new user (JSON)
- `POST /api/login` - Login user (JSON)
- `POST /api/logout` - Logout user (JSON)
- `GET /api/check-session` - Check if user is logged in

## WebSocket

WebSocket connection is handled automatically by the Dashboard component:
- Connects on component mount
- Handles `available_languages`, `transcription_result`, `error` events
- Sends `audio_chunk` events for recording

## Audio Processing Fix

The WebM audio processing error has been fixed by:
1. Using ffmpeg to convert WebM to WAV (if available)
2. Falling back to pydub if ffmpeg is not available
3. Using torchaudio to process the converted audio

**Note**: For best results, install ffmpeg:
- Windows: Download from https://ffmpeg.org/download.html
- Or use: `choco install ffmpeg` (if Chocolatey is installed)

## File Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── SignUp.jsx
│   │   ├── SignUp.css
│   │   ├── Login.jsx
│   │   ├── Login.css
│   │   ├── Dashboard.jsx
│   │   └── Dashboard.css
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

## Backend Changes

- Flask now serves React build from `frontend/dist/`
- API routes support JSON requests
- WebSocket functionality unchanged
- All existing backend features preserved

## Testing

1. **Development**: 
   - Start Flask: `python app.py`
   - Start React dev: `cd frontend && npm run dev`
   - Access via React dev server (port 5173)

2. **Production**:
   - Build React: `cd frontend && npm run build`
   - Start Flask: `python app.py`
   - Access via Flask (port 5000)

## Notes

- The React app uses client-side routing, so Flask serves `index.html` for all non-API routes
- Session management works via cookies (withCredentials: true)
- WebSocket connects to the same Flask server
- All styling matches the Figma design provided

