import os
import torch
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit, disconnect
import io
import base64
import logging
import tempfile
from pydub import AudioSegment
import json
from transformers import pipeline
import torchaudio
import soundfile as sf
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_session import Session
from authlib.integrations.flask_client import OAuth

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Install it with: pip install python-dotenv")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'fallback-dev-key-12345')
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/realtimeASR")
app.config["SESSION_TYPE"] = "filesystem"

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
Session(app)

socketio = SocketIO(app, cors_allowed_origins="*")


# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", None)

# Initialize OAuth
oauth = OAuth(app)
google = None  # Initialize google variable

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    logger.warning("Google OAuth client id/secret not set. Google login will not work until env vars are provided.")
    logger.warning("Please create a .env file with your Google OAuth credentials.")
    logger.warning("See GOOGLE_OAUTH_SETUP.md for detailed instructions.")
else:
    logger.info("Google OAuth credentials found. Setting up Google login...")
    # Register Google OAuth client with manual endpoints (OAuth 2.0 only)
    google = oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        access_token_url="https://oauth2.googleapis.com/token",
        api_base_url="https://www.googleapis.com/oauth2/v2/",
        client_kwargs={"scope": "email profile"},
    )
    logger.info("Google OAuth client registered successfully")

# ----- Model & pipeline setup (unchanged logic) -----
asr_pipeline = None
translation_pipelines = {}
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

def load_models():
    global asr_pipeline, translation_pipelines
    try:
        logger.info("Loading ASR model...")
        model_id = "openai/whisper-medium"
        asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            torch_dtype=torch_dtype,
            device=device,
            chunk_length_s=30,
        )
        logger.info("ASR model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ASR model: {e}")
        asr_pipeline = None
        return

    model_configs = {
        'es': "Helsinki-NLP/opus-mt-en-es",
        'fr': "Helsinki-NLP/opus-mt-en-fr",
        'de': "Helsinki-NLP/opus-mt-en-de",
    }
    for lang, model_name in model_configs.items():
        try:
            logger.info(f"Loading {lang} translation model...")
            translation_pipelines[lang] = pipeline(
                "translation",
                model=model_name,
                device=device if device != "cpu" else -1,
                torch_dtype=torch_dtype
            )
            logger.info(f"Translation model for {lang} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load {lang} model: {e}")
            # continue

# ----- Audio processing & ASR functions (unchanged) -----
def process_webm_audio(audio_data):
    try:
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp:
            tmp_name = tmp.name
            tmp.write(audio_data)
            tmp.flush()
        tmp.close()
        try:
            audio = AudioSegment.from_file(tmp_name, format="webm")
            audio = audio.set_channels(1).set_frame_rate(16000)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_tmp:
                wav_name = wav_tmp.name
                audio.export(wav_name, format="wav")
            samples, sample_rate = sf.read(wav_name, dtype='float32')
            try:
                os.unlink(tmp_name)
                os.unlink(wav_name)
            except:
                pass
            return samples, sample_rate
        except Exception as e:
            logger.warning(f"Pydub method failed: {e}")
            try:
                waveform, sample_rate = torchaudio.load(tmp_name)
                waveform = waveform.mean(dim=0)
                samples = waveform.numpy().astype(np.float32)
                if sample_rate != 16000:
                    resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
                    samples = resampler(torch.from_numpy(samples)).numpy()
                try:
                    os.unlink(tmp_name)
                except:
                    pass
                return samples, 16000
            except Exception as e2:
                logger.warning(f"Torchaudio method failed: {e2}")
                try:
                    with open(tmp_name, 'rb') as f:
                        raw_data = f.read()
                    samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
                    try:
                        os.unlink(tmp_name)
                    except:
                        pass
                    return samples, 16000
                except Exception as e3:
                    logger.error(f"All audio processing methods failed: {e3}")
                    raise Exception(f"All audio processing methods failed: {e}, {e2}, {e3}")
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        try:
            os.unlink(tmp_name)
        except:
            pass
        raise e

def transcribe_audio(audio_data, sample_rate=16000):
    if asr_pipeline is None:
        return "ASR model not available"
    try:
        if len(audio_data) == 0:
            return "No audio data"
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_name = tmp.name
            sf.write(tmp_name, audio_data, sample_rate, format='WAV')
        try:
            result = asr_pipeline(tmp_name, generate_kwargs={"language": "english"})
            transcribed_text = result.get("text", "").strip()
            return transcribed_text if transcribed_text else "No speech detected"
        finally:
            try:
                os.unlink(tmp_name)
            except:
                pass
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"Transcription error: {str(e)}"

def translate_text(text, target_lang):
    if not text or target_lang not in translation_pipelines:
        return ""
    try:
        clean_text = text.strip()
        if not clean_text or clean_text.lower() in ['no speech detected', 'asr model not available']:
            return ""
        result = translation_pipelines[target_lang](clean_text)
        translated_text = result[0]['translation_text'] if result else ""
        return translated_text
    except Exception as e:
        logger.error(f"Translation error for {target_lang}: {e}")
        return f"Translation error: {str(e)}"


@app.route('/')
def index():
    if "user" in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username").strip()
        password = request.form.get("password")
        if not username or not password:
            flash("Please fill all fields")
            return redirect(url_for('register'))
        existing = mongo.db.users.find_one({"username": username})
        if existing:
            flash("Username already exists")
            return redirect(url_for('register'))
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        mongo.db.users.insert_one({
            "username": username,
            "password": hashed,
            "auth_type": "basic"
        })
        flash("Registered. Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user = mongo.db.users.find_one({"username": username})
        if user and user.get("auth_type") == "basic" and bcrypt.check_password_hash(user.get("password",""), password):
            session["user"] = username
            flash("Login successful")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("Logged out")
    return redirect(url_for('index'))

@app.route('/debug/oauth')
def debug_oauth():
    """Debug route to check OAuth configuration"""
    debug_info = {
        'google_client_id_set': bool(GOOGLE_CLIENT_ID),
        'google_client_secret_set': bool(GOOGLE_CLIENT_SECRET),
        'google_client_id_value': GOOGLE_CLIENT_ID[:10] + "..." if GOOGLE_CLIENT_ID else "Not set",
        'google_oauth_configured': google is not None,
        'flask_secret_set': bool(app.config.get('SECRET_KEY')),
        'session_type': app.config.get('SESSION_TYPE'),
        'mongo_uri_set': bool(app.config.get('MONGO_URI')),
        'redirect_uri_example': url_for('google_callback', _external=True)
    }
    return f"<pre>{debug_info}</pre>"

@app.route('/google_login')
def google_login():
    """Initiate Google OAuth login"""
    if not google or not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash("Google login is not configured. Please set up your Google OAuth credentials.", "error")
        return redirect(url_for('login'))
    
    # Normalize redirect URI to use localhost instead of 127.0.0.1
    redirect_uri = url_for('google_callback', _external=True)
    if '127.0.0.1' in redirect_uri:
        redirect_uri = redirect_uri.replace('127.0.0.1', 'localhost')
    
    logger.info(f"Redirect URI: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@app.route('/google_callback')
def google_callback():
    """Handle Google OAuth callback"""
    if not google:
        flash("Google login is not configured.", "error")
        return redirect(url_for('login'))
        
    try:
        token = google.authorize_access_token()
        logger.info(f"Received token: {token}")
        
        # Get user info from Google OAuth 2.0 API
        user_info = google.get('userinfo', token=token).json()
        logger.info(f"User info: {user_info}")
        
        if not user_info:
            flash("Failed to fetch user info from Google.", "error")
            return redirect(url_for('login'))
        
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0] if email else 'GoogleUser')
        google_id = user_info.get('id')
        
        if not email:
            flash("No email address provided by Google.", "error")
            return redirect(url_for('login'))
        
        # Check if user exists
        user = mongo.db.users.find_one({"username": email})
        if not user:
            # Create new user
            mongo.db.users.insert_one({
                "username": email,
                "name": name,
                "email": email,
                "google_id": google_id,
                "auth_type": "google",
                "profile": user_info
            })
            logger.info(f"Created new Google user: {email}")
        else:
            # Update existing user
            mongo.db.users.update_one(
                {"_id": user["_id"]}, 
                {"$set": {"google_id": google_id, "profile": user_info}}
            )
            logger.info(f"Updated existing Google user: {email}")
        
        session["user"] = email
        flash("Successfully logged in with Google!", "success")
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        flash("An error occurred during Google login. Please try again.", "error")
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        flash("Please login")
        return redirect(url_for('login'))
    username = session.get("user")
    return render_template("dashboard.html", username=username)

@socketio.on('connect')
def handle_connect():
    if "user" not in session:
        logger.info("Unauthorized socket connect attempt; disconnecting")
        emit('error', {'message': 'Unauthorized - please login first'})
        disconnect()
        return
    logger.info(f'Client connected (user={session.get("user")})')
    emit('status', {'message': 'Connected to server'})
    emit('available_languages', {
        'languages': list(translation_pipelines.keys()),
        'asr_ready': asr_pipeline is not None
    })

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    try:
        if asr_pipeline is None:
            emit('error', {'message': 'ASR model not loaded. Please check server logs.'})
            return
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        target_lang = data.get('target_lang', '')
        if len(audio_data) < 100:
            emit('transcription_result', {'original': 'Audio too short','translated': '','language': target_lang,'success': False})
            return
        samples, sample_rate = process_webm_audio(audio_data)
        transcribed_text = transcribe_audio(samples, sample_rate)
        if transcribed_text and not transcribed_text.startswith("Transcription error"):
            logger.info(f"Transcribed: {transcribed_text}")
            translated_text = ""
            if target_lang and target_lang in translation_pipelines:
                translated_text = translate_text(transcribed_text, target_lang)
                if translated_text and not translated_text.startswith("Translation error"):
                    logger.info(f"Translated to {target_lang}: {translated_text}")
            emit('transcription_result', {'original': transcribed_text,'translated': translated_text,'language': target_lang,'success': True})
        else:
            emit('transcription_result', {'original': transcribed_text,'translated': '','language': target_lang,'success': False})
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}")
        emit('error', {'message': f'Processing error: {str(e)}'})

# ----- Main entrypoint -----
if __name__ == '__main__':
    logger.info("Loading models...")
    load_models()
    if asr_pipeline is None:
        logger.error("Critical: ASR model failed to load. Server cannot function.")
    else:
        logger.info(f"Loaded {len(translation_pipelines)} translation models")
        available_langs = list(translation_pipelines.keys())
        if available_langs:
            logger.info(f"Available translation languages: {', '.join(available_langs)}")
        else:
            logger.warning("No translation models loaded. Only transcription will work.")
    logger.info("Starting server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
