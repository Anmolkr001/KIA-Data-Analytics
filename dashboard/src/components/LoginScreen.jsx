import React, { useState, useEffect } from "react";
import { Lock, User, Eye, EyeOff, AlertCircle, ArrowRight } from "lucide-react";
import HeroBackground from "./HeroBackground";
import ModelSlider from "./ModelSlider";
import Car360Viewer from "./Car360Viewer";
import { kiaModels } from "../data/kiaModels";

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
  const [shake, setShake] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [selected360Model, setSelected360Model] = useState(null);

  // Sync 360 viewer modal with browser history
  useEffect(() => {
    const onPopState = () => {
      const hash = window.location.hash;
      if (hash.startsWith("#model-")) {
        const modelId = hash.replace("#model-", "");
        const found = kiaModels.find((m) => m.id === modelId);
        if (found) setSelected360Model(found);
      } else {
        setSelected360Model(null);
      }
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const handleSelectModel = (model) => {
    setSelected360Model(model);
    window.history.pushState({ modal: model.id }, "", `#model-${model.id}`);
  };

  const handleCloseModal = () => {
    setSelected360Model(null);
    if (window.location.hash.startsWith("#model-")) {
      window.history.back();
    }
  };

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
    <div
      className="login-root"
      style={{
        position: "relative",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        alignItems: "center",
        overflowY: "auto",
        overflowX: "hidden",
        padding: "20px 16px 20px",
        background: "transparent",
      }}
    >
      {/* Fullscreen Hero Background Studio with Soft Gradient Overlay */}
      <HeroBackground src="/hero-bg.jpg" alt="Kia EV6 Exclusive Studio Background" />

      {/* Showroom Top Nav Bar */}
      <div
        style={{
          width: "100%",
          maxWidth: "1200px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          zIndex: 20,
          padding: "4px 8px 12px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            style={{
              fontSize: "11px",
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              color: "rgba(255,255,255,0.7)",
              fontFamily: "'Outfit', sans-serif",
              fontWeight: 700,
            }}
          >
            KIA Digital Showroom
          </span>
          <span
            style={{
              fontSize: "10px",
              padding: "2px 8px",
              borderRadius: "12px",
              background: "rgba(234, 0, 41, 0.2)",
              color: "#ff4d6d",
              border: "1px solid rgba(234, 0, 41, 0.35)",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
            }}
          >
            Bhubaneswar
          </span>
        </div>
      </div>

      {/* Top Flex Spacer */}
      <div style={{ flex: "1 0 10px", minHeight: "10px" }} aria-hidden="true" />

      {/* Login Card — Exactly as originally designed */}
      <div
        className={`login-card ${mounted ? "login-card--visible" : ""} ${shake ? "login-shake" : ""}`}
        style={{ margin: "auto 0" }}
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

      {/* Spacer between card and slider */}
      <div style={{ flex: "1 0 24px", minHeight: "24px" }} aria-hidden="true" />

      {/* Horizontal Model Slider (Embla Carousel) */}
      <div style={{ width: "100%", zIndex: 10 }}>
        <ModelSlider models={kiaModels} onSelectModel={handleSelectModel} />
      </div>

      {/* 360-Degree Interactive Viewer Modal */}
      {selected360Model && (
        <Car360Viewer
          model={selected360Model}
          models={kiaModels}
          onClose={handleCloseModal}
          onSelectModel={handleSelectModel}
        />
      )}
    </div>
  );
}
