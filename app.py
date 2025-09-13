import os
import torch
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import io
import base64
import logging
import tempfile
from pydub import AudioSegment
import json
from transformers import (
    pipeline,
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
    AutoModelForSeq2SeqLM,
    AutoTokenizer
)
import torchaudio
import wave
import soundfile as sf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'fallback-dev-key-12345')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize models
asr_pipeline = None
translation_pipelines = {}
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

def load_models():
    global asr_pipeline, translation_pipelines
    
    try:
        # Load speech recognition model
        logger.info("Loading ASR model...")
        
        # Use a smaller model for better performance
        model_id = "openai/whisper-base"
        
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

    # Load translation models
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
            # Continue with other models even if one fails

def process_webm_audio(audio_data):
    """Process WebM audio data with improved error handling"""
    try:
        # Create a temporary file with a unique name to avoid conflicts
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp:
            tmp_name = tmp.name
            tmp.write(audio_data)
            tmp.flush()
        
        # Close the file explicitly to release the handle
        tmp.close()
        
        # Process the audio file
        try:
            # Method 1: Try using pydub with webm
            audio = AudioSegment.from_file(tmp_name, format="webm")
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # Export to a different temporary file to avoid conflicts
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_tmp:
                wav_name = wav_tmp.name
                audio.export(wav_name, format="wav")
            
            # Read the WAV file using soundfile
            samples, sample_rate = sf.read(wav_name, dtype='float32')
            
            # Clean up temporary files
            try:
                os.unlink(tmp_name)
                os.unlink(wav_name)
            except:
                pass  # Ignore cleanup errors
            
            return samples, sample_rate
            
        except Exception as e:
            logger.warning(f"Pydub method failed: {e}")
            
            # Method 2: Try using torchaudio directly
            try:
                waveform, sample_rate = torchaudio.load(tmp_name)
                waveform = waveform.mean(dim=0)  # Convert to mono if stereo
                samples = waveform.numpy().astype(np.float32)
                
                # Resample if needed
                if sample_rate != 16000:
                    resampler = torchaudio.transforms.Resample(
                        orig_freq=sample_rate, 
                        new_freq=16000
                    )
                    samples = resampler(torch.from_numpy(samples)).numpy()
                
                # Clean up temporary file
                try:
                    os.unlink(tmp_name)
                except:
                    pass
                
                return samples, 16000
                
            except Exception as e2:
                logger.warning(f"Torchaudio method failed: {e2}")
                
                # Final fallback: try to read as raw data
                try:
                    with open(tmp_name, 'rb') as f:
                        # Try to read as raw PCM (last resort)
                        raw_data = f.read()
                    
                    # Assume 16-bit PCM at 16kHz (common for browser audio)
                    samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Clean up temporary file
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
        # Ensure temporary files are cleaned up
        try:
            os.unlink(tmp_name)
        except:
            pass
        raise e

def transcribe_audio(audio_data, sample_rate=16000):
    """Transcribe audio using Hugging Face ASR pipeline"""
    if asr_pipeline is None:
        return "ASR model not available"
    
    try:
        # Ensure proper length and type
        if len(audio_data) == 0:
            return "No audio data"
        
        # Generate a temporary WAV file for the pipeline
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_name = tmp.name
            
            # Save audio data as WAV file
            sf.write(tmp_name, audio_data, sample_rate, format='WAV')
        
        try:
            # Transcribe using the pipeline
            result = asr_pipeline(
                tmp_name,
                generate_kwargs={"language": "english"},
            )
            
            transcribed_text = result.get("text", "").strip()
            return transcribed_text if transcribed_text else "No speech detected"
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(tmp_name)
            except:
                pass
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"Transcription error: {str(e)}"

def translate_text(text, target_lang):
    """Translate text using Hugging Face translation pipeline"""
    if not text or target_lang not in translation_pipelines:
        return ""
    
    try:
        # Clean text for translation
        clean_text = text.strip()
        if not clean_text or clean_text.lower() in ['no speech detected', 'asr model not available']:
            return ""
            
        # Translate using the pipeline
        result = translation_pipelines[target_lang](clean_text)
        translated_text = result[0]['translation_text'] if result else ""
        return translated_text
        
    except Exception as e:
        logger.error(f"Translation error for {target_lang}: {e}")
        return f"Translation error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
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
        # Check if ASR model is available
        if asr_pipeline is None:
            emit('error', {'message': 'ASR model not loaded. Please check server logs.'})
            return
        
        # Extract audio data from base64
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        target_lang = data.get('target_lang', '')
        
        if len(audio_data) < 100:  # Minimum audio data check
            emit('transcription_result', {
                'original': 'Audio too short',
                'translated': '',
                'language': target_lang,
                'success': False
            })
            return
        
        # Process audio data
        samples, sample_rate = process_webm_audio(audio_data)
        
        # Transcribe audio
        transcribed_text = transcribe_audio(samples, sample_rate)
        
        if transcribed_text and not transcribed_text.startswith("Transcription error"):
            logger.info(f"Transcribed: {transcribed_text}")
            
            # Translate if target language is specified and available
            translated_text = ""
            if target_lang and target_lang in translation_pipelines:
                translated_text = translate_text(transcribed_text, target_lang)
                if translated_text and not translated_text.startswith("Translation error"):
                    logger.info(f"Translated to {target_lang}: {translated_text}")
            
            # Send results back to client
            emit('transcription_result', {
                'original': transcribed_text,
                'translated': translated_text,
                'language': target_lang,
                'success': True
            })
        else:
            emit('transcription_result', {
                'original': transcribed_text,
                'translated': '',
                'language': target_lang,
                'success': False
            })
            
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}")
        emit('error', {'message': f'Processing error: {str(e)}'})

if __name__ == '__main__':
    logger.info("Loading models...")
    load_models()
    
    # Check if models loaded successfully
    if asr_pipeline is None:
        logger.error("Critical: ASR model failed to load. Server cannot function.")
    else:
        logger.info(f"Loaded {len(translation_pipelines)} translation models")
        
        # List available languages
        available_langs = list(translation_pipelines.keys())
        if available_langs:
            logger.info(f"Available translation languages: {', '.join(available_langs)}")
        else:
            logger.warning("No translation models loaded. Only transcription will work.")
    
    logger.info("Starting server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)