# Python 3.13 Compatibility Fixes

This document describes the fixes applied to make the application compatible with Python 3.13.

## Issues Fixed

### 1. **audioop Module Removed** (Python 3.13 Breaking Change)
- **Problem**: Python 3.13 removed the `audioop` module, which `pydub` depends on
- **Solution**: 
  - Made `pydub` optional in the code
  - Updated `process_webm_audio()` to use `torchaudio` as the primary method
  - `torchaudio` can handle WebM files directly and doesn't require `audioop`
  - Falls back to `pydub` only if available (for older Python versions)

### 2. **eventlet Incompatibility** (Python 3.13 Breaking Change)
- **Problem**: `eventlet` uses `ssl.wrap_socket()` which was removed in Python 3.13
- **Solution**: 
  - Removed `eventlet`` from requirements
  - Changed Flask-SocketIO to use `threading` mode instead
  - Updated: `SocketIO(app, async_mode='threading')`

### 3. **Package Version Updates**
- Updated `torch` from 2.2.0 to 2.7.1 (Python 3.13 compatible)
- Updated `torchaudio` from 2.2.0 to 2.7.1
- Updated `sentencepiece` to >=0.2.0 (has pre-built wheels for Python 3.13)
- Made `transformers`, `numpy`, `soundfile`, and `tokenizers` use flexible versions (>=)

## Code Changes

### app.py
1. Made `pydub` import optional with try/except
2. Rewrote `process_webm_audio()` to prioritize `torchaudio`
3. Changed SocketIO initialization to use `threading` mode

### requirements.txt
1. Commented out `pydub` (optional dependency)
2. Commented out `eventlet` (not needed with threading mode)
3. Updated package versions for Python 3.13 compatibility

## How to Use

### Option 1: Use the Helper Scripts
```powershell
# Install dependencies
.\install_deps.ps1

# Start the app
.\start_app.ps1
```

### Option 2: Manual Setup
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the app
python app.py
```

## Testing

The app has been tested to:
- ✅ Import successfully without errors
- ✅ Handle missing `pydub` gracefully
- ✅ Use `torchaudio` for audio processing
- ✅ Work with threading mode for WebSockets

## Notes

- The app will show a warning about `pydub` not being available - this is expected and safe to ignore
- Google OAuth requires environment variables - if not set, you'll see a warning but the app will still work
- Model loading may take several minutes on first run (downloading from Hugging Face)

## Backward Compatibility

The code maintains backward compatibility:
- If `pydub` is available (e.g., on Python 3.11/3.12), it will be used as a fallback
- The threading mode works on all Python versions
- All functionality remains the same

