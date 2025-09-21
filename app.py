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
from transformers import pipeline, M2M100ForConditionalGeneration, M2M100Tokenizer
import torchaudio
import soundfile as sf
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_session import Session
from authlib.integrations.flask_client import OAuth

# Picked 20 diverse languages
AVAILABLE_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese (Simplified)": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Turkish": "tr",
    "Bengali": "bn",
    "Tamil": "ta",
    "Swahili": "sw",
    "Persian (Farsi)": "fa",
    "Vietnamese": "vi",
    "Indonesian": "id",
    "Thai": "th",
}

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
google = None

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    logger.warning("Google OAuth client id/secret not set. Google login will not work until env vars are provided.")
else:
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

# ----- Model setup -----
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

asr_pipeline = None
m2m_model = None
m2m_tokenizer = None

def load_models():
    global asr_pipeline, m2m_model, m2m_tokenizer
    try:
        logger.info("Loading ASR model (Whisper-medium)...")
        asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-medium",
            device=device,
            torch_dtype=torch_dtype,
            chunk_length_s=30
        )
        logger.info("ASR model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ASR model: {e}")
        asr_pipeline = None

    try:
        logger.info("Loading M2M100 multilingual translation model...")
        m2m_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M").to(device)
        m2m_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        logger.info("M2M100 model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load M2M100 model: {e}")
        m2m_model = None
        m2m_tokenizer = None

# ----- Audio processing -----
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
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        raise e

# ----- ASR -----
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
            result = asr_pipeline(tmp_name)
            transcribed_text = result.get("text", "").strip()
            detected_lang = result.get("language", "en")
            return transcribed_text if transcribed_text else "No speech detected", detected_lang
        finally:
            try:
                os.unlink(tmp_name)
            except:
                pass
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"Transcription error: {str(e)}", "en"

# ----- Translation -----
def translate_text(text, source_lang, target_lang_code):
    if not text or not m2m_model or not m2m_tokenizer:
        return ""
    try:
        m2m_tokenizer.src_lang = source_lang
        encoded = m2m_tokenizer(text, return_tensors="pt").to(device)
        generated_tokens = m2m_model.generate(
            **encoded,
            forced_bos_token_id=m2m_tokenizer.get_lang_id(target_lang_code)
        )
        translated_text = m2m_tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        return translated_text
    except Exception as e:
        logger.error(f"Translation error ({source_lang}->{target_lang_code}): {e}")
        return f"Translation error: {str(e)}"

# ----- Routes -----
@app.route('/')
def index():
    if "user" in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username").strip()
        password = request.form.get("password")
        if not username or not password:
            flash("Please fill all fields")
            return redirect(url_for('register'))
        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists")
            return redirect(url_for('register'))
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        mongo.db.users.insert_one({"username": username, "password": hashed, "auth_type": "basic"})
        flash("Registered. Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user = mongo.db.users.find_one({"username": username})
        if user and user.get("auth_type")=="basic" and bcrypt.check_password_hash(user.get("password",""), password):
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

@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        flash("Please login")
        return redirect(url_for('login'))
    return render_template("dashboard.html", username=session.get("user"))

@app.route('/debug/oauth')
def debug_oauth():
    debug_info = {
        'google_client_id_set': bool(GOOGLE_CLIENT_ID),
        'google_client_secret_set': bool(GOOGLE_CLIENT_SECRET),
        'google_oauth_configured': google is not None,
        'flask_secret_set': bool(app.config.get('SECRET_KEY')),
        'session_type': app.config.get('SESSION_TYPE'),
        'mongo_uri_set': bool(app.config.get('MONGO_URI')),
        'redirect_uri_example': url_for('google_callback', _external=True)
    }
    return f"<pre>{debug_info}</pre>"

@app.route('/google_login')
def google_login():
    if not google or not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        flash("Google login is not configured.", "error")
        return redirect(url_for('login'))
    redirect_uri = url_for('google_callback', _external=True)
    if '127.0.0.1' in redirect_uri:
        redirect_uri = redirect_uri.replace('127.0.0.1', 'localhost')
    return google.authorize_redirect(redirect_uri)

@app.route('/google_callback')
def google_callback():
    if not google:
        flash("Google login is not configured.", "error")
        return redirect(url_for('login'))
    try:
        token = google.authorize_access_token()
        user_info = google.get('userinfo', token=token).json()
        email = user_info.get('email')
        if not email:
            flash("No email provided by Google.", "error")
            return redirect(url_for('login'))
        user = mongo.db.users.find_one({"username": email})
        if not user:
            mongo.db.users.insert_one({
                "username": email, "name": user_info.get("name"), "email": email,
                "google_id": user_info.get("id"), "auth_type": "google", "profile": user_info
            })
        else:
            mongo.db.users.update_one({"_id": user["_id"]}, {"$set": {"google_id": user_info.get("id"), "profile": user_info}})
        session["user"] = email
        flash("Successfully logged in with Google!", "success")
        return redirect(url_for('dashboard'))
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        flash("Error during Google login.", "error")
        return redirect(url_for('login'))

# ----- SocketIO events -----
@socketio.on('connect')
def handle_connect():
    if "user" not in session:
        emit('error', {'message': 'Unauthorized - please login first'})
        disconnect()
        return
    logger.info(f'Client connected (user={session.get("user")})')
    emit('available_languages', {
    'languages': AVAILABLE_LANGUAGES,
    'asr_ready': asr_pipeline is not None
})
    emit('status', {'message': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    try:
        if asr_pipeline is None:
            emit('error', {'message': 'ASR model not loaded'})
            return
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        target_lang = data.get('target_lang', '')
        if len(audio_data) < 100:
            emit('transcription_result', {'original': 'Audio too short','translated': '', 'language': target_lang,'success': False})
            return
        samples, sample_rate = process_webm_audio(audio_data)
        transcribed_text, detected_lang = transcribe_audio(samples, sample_rate)
        translated_text = ""
        if target_lang and transcribed_text and not transcribed_text.startswith("Transcription error"):
            translated_text = translate_text(transcribed_text, detected_lang, target_lang)
        emit('transcription_result', {'original': transcribed_text,'translated': translated_text,'language': target_lang,'success': True})
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}")
        emit('error', {'message': f'Processing error: {str(e)}'})

# ----- Main -----
if __name__ == '__main__':
    logger.info("Loading models...")
    load_models()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
