import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";

function GoogleCallback({ onLogin }) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get("code");

        if (!code) {
          setError("No authorization code received from Google");
          setLoading(false);
          return;
        }

        // Send the code to backend API
        const response = await axios.post(
          "/api/google_callback",
          {
            code,
          },
          {
            withCredentials: true,
          }
        );

        if (response.data.success) {
          onLogin({ username: response.data.user });
          // Redirect straight to dashboard
          navigate("/dashboard", { replace: true });
        } else {
          setError(response.data.error || "Failed to login with Google");
        }
      } catch (err) {
        console.error("Google callback error:", err);
        setError(
          err.response?.data?.error ||
            "Error during Google login. Please try again."
        );
      } finally {
        setLoading(false);
      }
    };

    handleCallback();
  }, [searchParams, navigate, onLogin]);

  return (
    <div className="auth-container">
      <div className="auth-card">
        {loading && (
          <div style={{ textAlign: "center", padding: "2rem" }}>
            <div style={{ marginBottom: "1rem" }}>
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  border: "4px solid #f3f3f3",
                  borderTop: "4px solid #3498db",
                  borderRadius: "50%",
                  animation: "spin 1s linear infinite",
                  margin: "0 auto",
                }}
              />
            </div>
            <h2>Authenticating...</h2>
            <p>Redirecting to dashboard...</p>
          </div>
        )}
      </div>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default GoogleCallback;
