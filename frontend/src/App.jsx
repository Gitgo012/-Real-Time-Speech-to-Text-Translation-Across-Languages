import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useState, useEffect } from "react";
import SignUp from "./pages/SignUp";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import GoogleCallback from "./pages/GoogleCallback";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in by trying to access dashboard
    // Since backend doesn't have API endpoint, we'll handle auth in Dashboard component
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/signup"
          element={
            user ? <Navigate to="/dashboard" /> : <SignUp onSignUp={setUser} />
          }
        />
        <Route
          path="/login"
          element={
            user ? <Navigate to="/dashboard" /> : <Login onLogin={setUser} />
          }
        />
        <Route
          path="/google_callback"
          element={<GoogleCallback onLogin={setUser} />}
        />
        <Route
          path="/dashboard"
          element={
            user ? (
              <Dashboard user={user} onLogout={() => setUser(null)} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route
          path="/"
          element={<Navigate to={user ? "/dashboard" : "/login"} />}
        />
      </Routes>
    </Router>
  );
}

export default App;
