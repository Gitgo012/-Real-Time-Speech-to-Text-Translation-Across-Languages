import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "./Login.css";

function Login({ onLogin }) {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Use form submission to match backend expectations
      const formDataToSend = new FormData();
      formDataToSend.append("username", formData.email);
      formDataToSend.append("password", formData.password);

      await axios.post("/login", formDataToSend, {
        withCredentials: true,
        headers: {
          "Content-Type": "multipart/form-data",
        },
        maxRedirects: 0,
        validateStatus: () => true,
      });

      // After attempting login, verify session on the backend
      const sessionRes = await axios.get("/api/session_check", {
        withCredentials: true,
      });

      if (sessionRes.data?.logged_in) {
        onLogin({ username: sessionRes.data.user });
        navigate("/dashboard");
      } else {
        setError("Invalid credentials. Please sign up first or try again.");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError(
        err.response?.data?.message ||
          "Login failed. Please check your credentials and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await axios.get("/api/google_auth_url");
      console.log("Auth URL response:", response.data);
      if (response.data.auth_url) {
        // Store the return path and redirect to Google's OAuth consent page
        sessionStorage.setItem("googleLoginAttempt", "true");
        window.location.href = response.data.auth_url;
      } else {
        setError(response.data.error || "Failed to get Google login URL");
      }
    } catch (err) {
      console.error("Google login error:", err);
      const errorMsg =
        err.response?.data?.error ||
        "Google login is not configured. Please contact support.";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleAppleLogin = () => {
    // Apple login implementation
    console.log("Apple login not implemented yet");
  };

  return (
    <div className="auth-container">
      <div className="auth-header">
        <h1 className="auth-title">Log In</h1>
      </div>
      <div className="auth-card">
        <div className="auth-icon">
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H11V21H5V3H13V9H21ZM19 11L15 15L13 13L11 15L15 19L23 11H19Z"
              fill="#000"
            />
          </svg>
        </div>
        <h2 className="auth-card-title">Welcome Back</h2>
        <p className="auth-card-subtitle">Sign in to your account</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              className="input"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <div className="form-group-header">
              <label htmlFor="password">Password</label>
              <Link to="/forgot-password" className="forgot-password">
                Forgot Password?
              </Link>
            </div>
            <input
              type="password"
              id="password"
              name="password"
              className="input"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="divider">
          <span>Or</span>
        </div>

        <div className="social-login">
          <button
            type="button"
            className="btn btn-social btn-google"
            onClick={handleGoogleLogin}
          >
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google
          </button>
          
        </div>

        <p className="auth-link">
          Don't have an account? <Link to="/signup">Sign Up</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
