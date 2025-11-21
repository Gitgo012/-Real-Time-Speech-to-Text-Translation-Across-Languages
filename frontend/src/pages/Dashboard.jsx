import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import io from "socket.io-client";
import axios from "axios";
import "./Dashboard.css";

function Dashboard({ user, onLogout }) {
  const [sourceLang, setSourceLang] = useState("en");
  const [targetLang, setTargetLang] = useState("es");
  const [isRecording, setIsRecording] = useState(false);
  const [originalText, setOriginalText] = useState(
    "Your original speech will appear here..."
  );
  const [translatedText, setTranslatedText] = useState(
    "Your translated speech will appear here..."
  );
  const [availableLanguages, setAvailableLanguages] = useState({});
  const [translationHistory, setTranslationHistory] = useState([]);
  const [status, setStatus] = useState("Ready to start");
  const [loading, setLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const socketRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const audioContextRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Wait a bit for session cookie to be set after login/register
    const connectSocket = async () => {
      // First, verify session is set
      try {
        const sessionCheck = await axios.get("/api/session_check");
        console.log("Session check:", sessionCheck.data);
        if (!sessionCheck.data.logged_in) {
          setStatus("Not logged in. Please login first.");
          return;
        }
      } catch (err) {
        console.error("Session check failed:", err);
        setStatus("Session check failed. Please refresh and login again.");
        return;
      }

      // Fetch translation history from database
      try {
        const historyResponse = await axios.get("/api/translation_history", {
          withCredentials: true,
        });
        if (historyResponse.data.history) {
          setTranslationHistory(historyResponse.data.history);
          console.log(
            "Loaded translation history:",
            historyResponse.data.history
          );
        }
      } catch (err) {
        console.error("Failed to fetch translation history:", {
          status: err.response?.status,
          data: err.response?.data,
          message: err.message,
        });
      }

      // Initialize WebSocket connection - use proxy through Vite
      const socketServerUrl = import.meta.env.VITE_SOCKET_URL || undefined;
      socketRef.current = io(socketServerUrl, {
        withCredentials: true,
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5,
      });

      socketRef.current.on("connect", () => {
        console.log("WebSocket connected");
        setStatus("Connected to server");
      });

      socketRef.current.on("disconnect", (reason) => {
        console.log("WebSocket disconnected:", reason);
        if (reason === "io server disconnect") {
          // Server disconnected, try to reconnect
          socketRef.current.connect();
        } else {
          setStatus("Disconnected from server");
        }
      });

      socketRef.current.on("connect_error", (error) => {
        console.error("WebSocket connection error:", error);
        setStatus("Connection error. Retrying...");
      });

      socketRef.current.on("available_languages", (data) => {
        console.log("Received available languages:", data);
        if (data && data.languages) {
          setAvailableLanguages(data.languages);
          // Set default target language if not set (use Spanish as default)
          setTargetLang((prev) => prev || "es");
          // Set default source language (English)
          setSourceLang((prev) => prev || "en");
        }
        if (!data.asr_ready) {
          setStatus("ASR model not ready. Please wait...");
        } else {
          setStatus("Ready to start");
        }
      });

      socketRef.current.on("transcription_result", (data) => {
        console.log("Received transcription result:", data);
        if (data.success) {
          setOriginalText(
            data.original || "Your original speech will appear here..."
          );
          setTranslatedText(
            data.translated || "Your translated speech will appear here..."
          );
          setLoading(false);
          setIsProcessing(false);
          setStatus("Processing complete");

          // Add to history and save to database
          if (data.original && data.translated) {
            const historyItem = {
              timestamp: new Date().toISOString(),
              sourceLang: sourceLang,
              targetLang: targetLang,
              original: data.original,
              translated: data.translated,
            };

            // Save to database
            axios
              .post("/api/translation_history", historyItem, {
                withCredentials: true,
              })
              .then((response) => {
                console.log("Translation saved successfully:", response.data);
              })
              .catch((err) => {
                console.error("Failed to save translation:", {
                  status: err.response?.status,
                  data: err.response?.data,
                  message: err.message,
                });
              });

            // Update local state
            setTranslationHistory((prev) =>
              [historyItem, ...prev].slice(0, 50)
            ); // Keep last 50
          }
        } else {
          setLoading(false);
          setIsProcessing(false);
          setStatus("Processing failed: " + data.original);
        }
      });

      socketRef.current.on("error", (data) => {
        console.error("WebSocket error:", data);
        setLoading(false);
        setIsProcessing(false);
        setStatus("Error: " + data.message);
      });
    };

    // Small delay to ensure session cookie is set
    const timer = setTimeout(connectSocket, 500);

    return () => {
      clearTimeout(timer);
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
      stopRecording();
    };
  }, []);

  const startRecording = async () => {
    if (isProcessing) {
      setStatus("Please wait for the current translation to finish.");
      return;
    }

    if (!targetLang || targetLang === "") {
      alert("Please select a target language first");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      streamRef.current = stream;
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      const source = audioContextRef.current.createMediaStreamSource(stream);
      const gainNode = audioContextRef.current.createGain();
      gainNode.gain.value = 0;
      source.connect(gainNode);

      const options = {
        mimeType: "audio/webm;codecs=opus",
        audioBitsPerSecond: 16000,
      };

      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        delete options.mimeType;
      }

      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;
      let chunks = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        setIsProcessing(true);
        setLoading(true);
        setStatus("Translating...");
        const blob = new Blob(chunks, { type: "audio/webm" });
        chunks = [];

        const reader = new FileReader();
        reader.onload = () => {
          if (socketRef.current && socketRef.current.connected) {
            socketRef.current.emit("audio_chunk", {
              audio: reader.result,
              target_lang: targetLang,
            });
          }
        };
        reader.readAsDataURL(blob);
      };

      mediaRecorder.start(1000);
      setIsRecording(true);
      setStatus("Recording...");
      setOriginalText("Listening...");
      setTranslatedText("Translating...");
    } catch (error) {
      console.error("Error starting recording:", error);
      setStatus("Error: " + error.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }

      setStatus("Recording stopped");
    }
  };

  const handleLogout = async () => {
    try {
      await axios.get("/logout", { withCredentials: true, maxRedirects: 0 });
      onLogout();
      navigate("/login");
    } catch (error) {
      // Even if there's an error, logout locally
      onLogout();
      navigate("/login");
    }
  };

  const clearHistory = () => {
    setTranslationHistory([]);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getLanguageName = (code) => {
    return (
      Object.keys(availableLanguages).find(
        (key) => availableLanguages[key] === code
      ) || code
    );
  };

  return (
    <div className="dashboard">
      {loading && (
        <div className="loader-popup">
          <div className="loader-card">
            <div className="spinner"></div>
            <p className="loader-text">{status || "Processing..."}</p>
          </div>
        </div>
      )}
      <div className="dashboard-header">
        <div className="header-left">
          <h1 className="app-title">🎤 Real-Time STT Translation</h1>
        </div>
        <div className="header-right">
          <button
            className="btn btn-secondary btn-logout"
            onClick={handleLogout}
          >
            Logout
          </button>
          <div className="user-profile">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z"
                fill="#000"
              />
            </svg>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-main">
          <div className="speech-section">
            <h2 className="section-title">Speech Input</h2>

            <div className="language-selectors">
              <div className="language-group">
                <label htmlFor="sourceLang">Source Language</label>
                <select
                  id="sourceLang"
                  className="select"
                  value={sourceLang}
                  onChange={(e) => setSourceLang(e.target.value)}
                  disabled={isRecording}
                >
                  {Object.keys(availableLanguages).length === 0 ? (
                    <option value="">Loading languages...</option>
                  ) : (
                    Object.entries(availableLanguages).map(([name, code]) => (
                      <option key={code} value={code}>
                        {name} {code === "en" ? "(US)" : ""}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div className="language-group">
                <label htmlFor="targetLang">Target Language</label>
                <select
                  id="targetLang"
                  className="select"
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  disabled={isRecording}
                >
                  {Object.keys(availableLanguages).length === 0 ? (
                    <option value="">Loading languages...</option>
                  ) : (
                    <>
                      <option value="">Select target language</option>
                      {Object.entries(availableLanguages).map(
                        ([name, code]) => (
                          <option key={code} value={code}>
                            {name}
                          </option>
                        )
                      )}
                    </>
                  )}
                </select>
              </div>
            </div>

            <div className="recording-controls">
              <button
                className={`btn ${isRecording ? "btn-stop" : "btn-primary"}`}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={!targetLang || isProcessing}
              >
                {isRecording ? "⏹ Stop Recording" : "▶ Start Recording"}
              </button>
            </div>

            <div className="text-panels">
              <div className="text-panel">
                <h3 className="panel-title">Original Text</h3>
                <div className="text-content original-text">{originalText}</div>
              </div>

              <div className="text-panel">
                <h3 className="panel-title">Translated Text</h3>
                <div className="text-content translated-text">
                  {translatedText}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="dashboard-sidebar">
          <div className="history-section">
            <div className="history-header">
              <h2 className="section-title">Translation History</h2>
              {translationHistory.length > 0 && (
                <button className="btn-clear" onClick={clearHistory}>
                  Clear History
                </button>
              )}
            </div>

            <div className="history-list">
              {translationHistory.length === 0 ? (
                <div className="history-empty">No translation history yet</div>
              ) : (
                translationHistory.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-meta">
                      <span className="history-date">
                        {formatDate(item.timestamp)}
                      </span>
                      <span className="history-lang">
                        {getLanguageName(item.sourceLang)} →{" "}
                        {getLanguageName(item.targetLang)}
                      </span>
                    </div>
                    <div className="history-text">
                      <div className="history-original">{item.original}</div>
                      <div className="history-translated">
                        {item.translated}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
