import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import './SignUp.css';

function SignUp({ onSignUp }) {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      // Use form submission to match backend expectations
      const formDataToSend = new FormData();
      formDataToSend.append('username', formData.email);
      formDataToSend.append('password', formData.password);

      const response = await axios.post('/register', formDataToSend, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        maxRedirects: 0,
        validateStatus: (status) => status >= 200 && status < 400
      });

      // Automatically log the user in after successful signup
      try {
        const loginData = new FormData();
        loginData.append('username', formData.email);
        loginData.append('password', formData.password);

        await axios.post('/login', loginData, {
          withCredentials: true,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          maxRedirects: 0,
          validateStatus: (status) => status >= 200 && status < 400
        });

        onSignUp({ username: formData.email, fullName: formData.fullName });
        navigate('/dashboard');
      } catch (loginErr) {
        console.error('Auto login after signup failed:', loginErr);
        // Fallback: direct user to login page
        navigate('/login');
      }
    } catch (err) {
      if (err.response?.status === 302 || err.response?.status === 200) {
        // Redirect happened, go to login
        navigate('/login');
      } else {
        setError(err.response?.data?.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-header">
        <h1 className="auth-title">Sign Up</h1>
      </div>
      <div className="auth-card">
        <div className="auth-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H11V21H5V3H13V9H21ZM19 11L15 15L13 13L11 15L15 19L23 11H19Z" fill="#000"/>
          </svg>
        </div>
        <h2 className="auth-card-title">Create Account</h2>
        <p className="auth-card-subtitle">Join Real-Time STT Translation platform</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="fullName">Full name</label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              className="input"
              placeholder="Enter your full name"
              value={formData.fullName}
              onChange={handleChange}
              required
            />
          </div>

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
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              className="input"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm your password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              className="input"
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Signing Up...' : 'Sign Up'}
          </button>
        </form>

        <p className="auth-link">
          Already have an account? <Link to="/login">Log In</Link>
        </p>
      </div>
    </div>
  );
}

export default SignUp;

