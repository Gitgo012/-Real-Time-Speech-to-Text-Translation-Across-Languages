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
├── Jenkinsfile           # Jenkins CI/CD pipeline
├── JENKINS_SETUP.md      # Jenkins configuration guide
├── TESTING_README.md     # Testing setup and guide
└── README.md
```

---

## Testing & CI/CD

### Unit Testing

We use **pytest** for backend testing and **Vitest** for frontend testing.

#### Backend Tests
```bash
pytest tests/ -v --cov=. --cov-report=html
```

#### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### Jenkins Pipeline

A complete CI/CD pipeline is configured in `Jenkinsfile` with the following stages:
- **Checkout** - Clone repository
- **Dependency Installation** - Python and npm packages
- **Code Quality** - Linting and formatting checks
- **Unit Tests** - Backend (pytest) and Frontend (vitest)
- **Security Scanning** - CVE checks
- **Docker Build** - Container image creation
- **Validation** - docker-compose configuration

#### Quick Setup (Windows)
```powershell
.\setup-jenkins.bat
```

#### Quick Setup (Linux/Mac)
```bash
chmod +x setup-jenkins.sh
./setup-jenkins.sh
```

#### Manual Jenkins Setup
1. Navigate to `http://localhost:8090`
2. Create new Pipeline job
3. Configure to use this repository's `Jenkinsfile`
4. See `JENKINS_SETUP.md` for detailed instructions

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


