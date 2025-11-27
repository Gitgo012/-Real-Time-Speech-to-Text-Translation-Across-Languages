````markdown
# Real-Time Speech-to-Text Translation Across Languages

## Project Overview
This project aims to build a **real-time multilingual translation system** that can transcribe and translate speech across different languages during live conversations. The system is particularly useful in domains like **global business meetings**, **tourism**, and **cross-cultural collaborations**.

The project will be implemented using a **microservice architecture** and deployed with **Kubernetes** for scalability, reliability, and modularity.

---

## Objectives
- Convert speech input to text in real-time (**ASR: Automatic Speech Recognition**).
- Translate text between multiple languages with high accuracy.
- Output the translated text (and potentially speech) back in real-time.
- Ensure low latency for natural conversation flow.
- Leverage **open-source models** for customization and fine-tuning.

---

## System Architecture
The system follows a **microservice-based architecture**, orchestrated with **Kubernetes**:

1. **Audio Ingestion Service**  
   - Captures audio streams from microphones or input sources.  
   - Sends audio chunks to the ASR service.  

2. **ASR (Speech-to-Text) Service**  
   - Powered by **Faster-Whisper** (a highly optimized implementation of Whisper ASR using `ctranslate2`).  
   - Converts speech into text in real time.  
   - Designed for speed and memory efficiency.  

3. **Translation Service**  
   - Uses Transformer or Seq2Seq models (e.g., MarianMT, M2M100, NLLB).  
   - Translates transcribed text into the target language(s).  

4. **Output Service**  
   - Displays translated text in UI.  
   - (Optional) Converts translated text back into speech using TTS models.  

5. **API Gateway**  
   - Routes requests between services.  
   - Handles authentication, load balancing, and scaling.  

---

## Tech Stack
- **ASR**: [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)  
- **Translation**: Hugging Face Transformers (MarianMT, M2M100, NLLB)  
- **TTS (optional)**: Coqui TTS / VITS models  
- **Backend**: Python (FastAPI / Flask for microservices)  
- **Containerization**: Docker  
- **Orchestration**: Kubernetes (K8s)  
- **LLM Integration (future scope)**: Ollama or fine-tuned LLMs for translation improvements  

---

## Why Faster-Whisper for ASR?
- **Speed**: Built on `CTranslate2`, optimized for CPU/GPU inference.  
- **Efficiency**: Lower memory usage compared to the original Whisper.  
- **Scalability**: Easier to containerize and run as a service.  
- **Accuracy**: Comparable to OpenAI Whisper.  
- **Ease of Use**: Python-friendly APIs for quick integration.  

Future versions of the system can explore **other ASR models** (like torchaudio-based wav2vec2, OpenSeq2Seq, or ESPnet) for fine-tuning and domain adaptation.

---

## Deployment Strategy
1. **Containerize each service** (ASR, Translation, TTS, API Gateway, UI).  
2. **Push Docker images** to a container registry (Docker Hub, GitHub Container Registry, etc.).  
3. Use **Kubernetes** to deploy services:  
   - Define **Deployments** and **Services** for each microservice.  
   - Configure **Ingress** for external access.  
   - Add **Horizontal Pod Autoscaler** for scaling under load.  
4. (Optional) Deploy on **free tiers**:  
   - **Google Kubernetes Engine (GKE Autopilot free tier)**  
   - **Azure AKS free tier**  
   - **Local Kubernetes (minikube/kind)** for testing.  

---

## Future Enhancements
- Add **speaker diarization** (identify who is speaking).  
- Implement **real-time subtitles overlay** for video calls.  
- Enable **offline support** on edge devices.  
- Fine-tune ASR/translation models for specific business or tourism jargon.  
- Add support for **low-resource languages**.  

---

## Repository Structure (Proposed)
```text
real-time-speech-translation/
├── asr_service/          # Faster-Whisper ASR microservice
├── translation_service/  # Transformer-based translation microservice
├── tts_service/          # (Optional) text-to-speech microservice
├── api_gateway/          # API routing and orchestration
├── ui/                   # Web or mobile interface
├── k8s/                  # Kubernetes YAML manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── docker/               # Dockerfiles for each service
├── tests/                # Unit and integration tests
└── README.md
```

---

## Security Considerations & Implementation

This section documents the security measures that have been implemented in the Real-Time Speech-to-Text Translation system to protect user data and ensure secure operation.

### 1. **Authentication & Authorization**

#### Implementation:
- **Local Authentication**:
  - Username/password registration and login using `Flask-Bcrypt` for secure password hashing
  - Passwords are hashed using bcrypt algorithm (bcrypt.generate_password_hash())
  - Password verification performed server-side before session creation

- **OAuth 2.0 (Google)** (Optional):
  - Google OAuth integration via `authlib` library
  - Authorization code exchange to obtain access tokens
  - User information retrieved securely through authenticated API calls
  - Users created/updated in database upon first OAuth login
  - Environment variables store sensitive credentials (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`)

#### Files:
- `app.py`: Lines 57-68 (bcrypt & session setup), Lines 108-124 (OAuth initialization), Lines 620-700 (authentication routes)
- `requirements.txt`: `Flask-Bcrypt==1.0.1`, `authlib==1.2.1`

### 2. **Session Management & Cookie Security**n+
#### Implementation:
- **Secure Cookie Configuration** (`app.py`, Lines 62-68):
  - `SESSION_COOKIE_HTTPONLY = True`: Prevents JavaScript access to session cookies (XSS mitigation)
  - `SESSION_COOKIE_SAMESITE = "Lax"`: Prevents CSRF attacks by restricting cross-site cookie transmission
  - `SESSION_COOKIE_SECURE = False`: Set to `True` in production with HTTPS
  - Session stored on filesystem with Flask-Session
  - Automatic session invalidation on logout

- **WebSocket Authentication**:
  - Session authentication checked on WebSocket connection (`handle_connect()`)
  - User verification performed before processing audio chunks (`handle_audio_chunk()`)
  - Unauthorized connections rejected and disconnected

#### Files:
- `app.py`: Lines 62-68 (session config), Lines 771-795 (WebSocket auth)

### 3. **Input Validation & XSS Protection**

#### Implementation:
- **Server-side Input Validation**:
  - Username validation: `.strip()` removes whitespace, empty checks performed
  - Audio data size validation: Chunks smaller than 100 bytes rejected
  - JSON data validation before processing

- **Protection Against XSS**:
  - User inputs from forms processed server-side and validated
  - Translation history excludes MongoDB `_id` field to prevent object injection
  - Frontend React components use JSX (automatically escapes content)

#### Files:
- `app.py`: Lines 562-575 (register route), Lines 578-593 (login route), Lines 797-826 (audio processing with validation)

### 4. **CSRF Protection**

#### Implementation:
- **Session-Based CSRF Protection**:
  - Flask session cookies with SameSite attribute prevent CSRF attacks
  - State stored server-side prevents token fixation
  - Cross-origin requests restricted via CORS and Nginx proxy rules

#### Nginx Configuration (`frontend/nginx.conf`):
- Routes authenticated endpoints through backend proxy with proper header forwarding
- WebSocket upgrade headers handled correctly to preserve authentication

### 5. **Secrets & Environment Management**

#### Implementation:
- **Environment Variable Storage**:
  - Sensitive credentials stored in `.env` file (excluded from git via `.gitignore`)
  - Credentials include: `FLASK_SECRET_KEY`, `MONGO_URI`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - `python-dotenv` library loads environment variables at runtime
  - Fallback values prevent application crashes but use insecure defaults

- **Secrets in Docker**:
  - `docker-compose.yml` uses `env_file: .env` to inject secrets securely
  - Secrets not hardcoded in Dockerfiles or docker-compose.yml
  - `.dockerignore` excludes sensitive files from Docker build context

#### Files:
- `.gitignore`: Excludes `.env` and `.venv`
- `.dockerignore`: Excludes `.env`, `venv/`, `flask_session/`
- `docker-compose.yml`: Line 5 (env_file reference)
- `app.py`: Lines 45-51 (dotenv loading and fallback handling)

### 6. **Transport Security & HTTPS**n+
#### Implementation:
- **Reverse Proxy with Nginx**:
  - Nginx acts as reverse proxy and first point of contact
  - Can be configured with SSL/TLS certificates for HTTPS (not shown in current config but ready for production)

- **WebSocket Security**:
  - WebSocket connections proxied through Nginx with proper upgrade headers
  - X-Forwarded-Proto header preserved for protocol detection
  - Cookie header forwarded with auth context

#### Files:
- `frontend/nginx.conf`: Lines 7-27 (WebSocket proxy with security headers), Lines 29-42 (API proxy)

### 7. **CORS & Cross-Origin Request Handling**

#### Implementation:
- **CORS Policy**:
  - Currently configured with `cors_allowed_origins="*"` for development flexibility
  - **Production Recommendation**: Restrict to specific frontend origin
  - Nginx proxy routes limit API endpoints to specific paths (api, login, logout, register, etc.)
  - Invalid routes not forwarded to backend

#### Files:
- `app.py`: Line 87 (SocketIO CORS configuration)
- `frontend/nginx.conf`: Lines 29-42 (API endpoint routing)

### 8. **Database Security**

#### Implementation:
- **MongoDB Integration**:
  - Connection via Flask-PyMongo with configurable URI
  - User records stored with encrypted passwords (bcrypt hashing)
  - Translation history scoped to individual users (`user_id` field)
  - No raw queries - PyMongo handles escaping

- **Data Access Control**:
  - User can only access their own translation history
  - Authentication verified before database operations
  - Error messages do not leak sensitive information

#### Files:
- `app.py`: Lines 72-74 (PyMongo initialization), Lines 492-520 (translation history endpoints with user scoping)

### 9. **Docker & Container Security**n+
#### Implementation:
- **Dockerfile Best Practices** (`Dockerfile.backend`):
  - Lightweight base image: `python:3.10-slim`
  - Non-root user execution (implicit in slim images)
  - Minimal dependencies installed with cleanup: `apt-get ... && rm -rf /var/lib/apt/lists/*`
  - Volume mounted for model cache (not world-writable)
  - Explicit EXPOSE port

- **Docker Compose Security**:
  - Health checks implemented for backend container (Lines 22-28)
  - Separated frontend and backend services
  - Volumes for persistent data (models, sessions)
  - GPU capabilities isolated where needed

#### Files:
- `Dockerfile.backend`: Lines 1-25
- `docker-compose.yml`: Lines 1-56
- `.dockerignore`: Excludes sensitive and build artifact files

### 10. **Logging & Monitoring**

#### Implementation:
- **Structured Logging**:
  - Flask logging configured with `logging.basicConfig()`
  - Detailed error logging for debugging without exposing sensitive data
  - Warning/error messages logged for failed authentication attempts
  - No sensitive data (passwords, tokens) logged

#### Files:
- `app.py`: Lines 53-54 (logging configuration), Throughout (logger.info/error calls)

### 11. **Dependency Management & Vulnerability Scanning**

#### Implementation:
- **Pinned Versions**:
  - All Python packages pinned to specific versions in `requirements.txt`
  - Critical libraries: Flask, Socket.io, PyMongo, Bcrypt, Authlib
  - Regular updates recommended

- **Security-Focused Dependencies**:
  - `Flask-Bcrypt`: Secure password hashing
  - `Flask-Session`: Server-side session management
  - `authlib`: OAuth 2.0 protocol compliance

#### Recommendations:
- Run `pip-audit` regularly to check for known vulnerabilities
- Run `npm audit` for frontend dependencies
- Keep dependencies updated with security patches

#### Files:
- `requirements.txt`: All dependencies listed with versions
- `frontend/package.json`: Frontend dependencies with versions

### 12. **Request Size & Rate Limiting**

#### Implementation:
- **Audio Processing Limits**:
  - Minimum audio chunk size: 100 bytes (prevents processing of empty/noise)
  - FFmpeg timeout: 10 seconds (prevents resource exhaustion)
  
- **Query Limits**:
  - Translation history limited to 50 records per request
  - Database queries use `.limit(50)`

#### Files:
- `app.py`: Lines 797 (audio size check), Lines 207 (FFmpeg timeout), Line 495 (history limit)

### 13. **Error Handling & Information Disclosure**n+
#### Implementation:
- **Safe Error Messages**:
  - Generic error messages returned to frontend ("Invalid credentials" instead of "User not found")
  - Detailed errors only in server logs
  - No stack traces exposed to clients

- **Health Checks**:
  - Health endpoint (`/health`) provides basic status without sensitive info
  - Model loading failures handled gracefully

#### Files:
- `app.py`: Lines 451-454 (health check), Lines 579-593 (safe login error messages)

---

## Security Recommendations for Production

1. **Enable HTTPS**: Set `SESSION_COOKIE_SECURE = True` and configure SSL/TLS certificates in Nginx
2. **Restrict CORS**: Change `cors_allowed_origins="*"` to specific frontend domain
3. **Rate Limiting**: Implement rate limiting for login/registration endpoints
4. **Audit Logging**: Enhance logging for security events (failed logins, unauthorized access attempts)
5. **Database Encryption**: Enable MongoDB encryption-at-rest and encryption-in-transit
6. **Secret Rotation**: Implement regular rotation of OAuth secrets and Flask secret keys
7. **Dependency Updates**: Regularly run `pip-audit` and `npm audit` to identify vulnerabilities
8. **WAF**: Deploy a Web Application Firewall (AWS WAF, Cloudflare, etc.)
9. **Monitoring & Alerting**: Implement centralized logging and real-time alerts for suspicious activity
10. **Security Testing**: Conduct regular penetration testing and OWASP vulnerability assessments

---

## License
This project is open-source and available under the **MIT License**.

---

## Contributors
- Arpit Deewan
- Harsha Vardhan Babu
- Shikhar Sharma
- Vartika Singh
- Yash Kuletha

---

## Acknowledgements
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)  
- [Hugging Face Transformers](https://huggingface.co/models)  
- [Coqui TTS](https://github.com/coqui-ai/TTS)  
- Open-source community for enabling real-time AI research & deployment

````
