import React, { useState, useEffect } from "react";
import { Lock, User, Eye, EyeOff, AlertCircle, ArrowRight } from "lucide-react";

/* ═══════════════════════════════════════════════════
   KIA Logo — Reused from CSVLoader
   ═══════════════════════════════════════════════════ */
function KiaLogo({ className = "" }) {
  return (
    <svg
      viewBox="0 0 120 48"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="KIA logo"
    >
      <path d="M4 42V6h8v14.5L28.5 6H39L22 22.5 40 42H29L15.5 26.5 12 30v12H4z" fill="currentColor" />
      <path d="M46 42V6h8v36h-8z" fill="currentColor" />
      <path d="M62 42L80 6h4l18 36h-9l-3.5-7.5H74.5L71 42H62zm15.5-14h11L83.5 16.5h-.2L77.5 28z" fill="currentColor" />
    </svg>
  );
}

/* ═══════════════════════════════════════════════════
   CREDENTIALS
   ═══════════════════════════════════════════════════ */
const VALID_USERNAME = "Anmol@kia";
const VALID_PASSWORD = "Anmol@2008";

/* ═══════════════════════════════════════════════════
   LOGIN SCREEN COMPONENT
   ═══════════════════════════════════════════════════ */
export default function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [shake, setShake] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password.");
      triggerShake();
      return;
    }

    setIsLoading(true);

    // Simulate a brief auth delay for UX polish
    setTimeout(() => {
      if (username === VALID_USERNAME && password === VALID_PASSWORD) {
        sessionStorage.setItem("kia-auth", "true");
        onLogin();
      } else {
        setError("Invalid credentials. Please try again.");
        setIsLoading(false);
        triggerShake();
      }
    }, 800);
  };

  const triggerShake = () => {
    setShake(true);
    setTimeout(() => setShake(false), 500);
  };

  return (
    <div className="login-root">
      {/* Animated grid background */}
      <div className="landing-grid-bg" aria-hidden="true">
        <div className="landing-grid-lines" />
      </div>

      {/* Gradient orbs */}
      <div
        className="gradient-orb-1"
        aria-hidden="true"
        style={{
          position: "absolute",
          width: "500px",
          height: "500px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(234,21,55,0.12) 0%, transparent 70%)",
          top: "-10%",
          right: "-8%",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />
      <div
        className="gradient-orb-2"
        aria-hidden="true"
        style={{
          position: "absolute",
          width: "400px",
          height: "400px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%)",
          bottom: "-5%",
          left: "-5%",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* Login card */}
      <div
        className={`login-card ${mounted ? "login-card--visible" : ""} ${shake ? "login-shake" : ""}`}
      >
        {/* Logo + Header */}
        <div className="login-header">
          <div className="login-logo-container">
            <div className="login-logo-ring">
              <KiaLogo className="login-logo" />
            </div>
          </div>
          <h1 className="login-title">Data Analytics</h1>
          <p className="login-subtitle">Sign in to access the dashboard</p>
        </div>

        {/* Divider */}
        <div className="login-divider" />

        {/* Form */}
        <form onSubmit={handleSubmit} className="login-form" autoComplete="off">
          {/* Username */}
          <div className="login-field">
            <label htmlFor="login-username" className="login-label">
              Username
            </label>
            <div className="login-input-wrapper">
              <User size={15} className="login-input-icon" />
              <input
                id="login-username"
                type="text"
                value={username}
                onChange={(e) => { setUsername(e.target.value); setError(""); }}
                placeholder="Enter your username"
                className="login-input"
                autoFocus
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Password */}
          <div className="login-field">
            <label htmlFor="login-password" className="login-label">
              Password
            </label>
            <div className="login-input-wrapper">
              <Lock size={15} className="login-input-icon" />
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => { setPassword(e.target.value); setError(""); }}
                placeholder="Enter your password"
                className="login-input login-input--password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="login-eye-toggle"
                aria-label={showPassword ? "Hide password" : "Show password"}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="login-error" role="alert">
              <AlertCircle size={14} />
              <span>{error}</span>
            </div>
          )}

          {/* Submit button */}
          <button
            type="submit"
            className={`login-submit ${isLoading ? "login-submit--loading" : ""}`}
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="login-spinner" />
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight size={16} className="login-submit-arrow" />
              </>
            )}
          </button>
        </form>

        {/* Footer */}
        <p className="login-footer">
          Bhubaneswar Dealership &bull; Secure Access
        </p>
      </div>
    </div>
  );
}
