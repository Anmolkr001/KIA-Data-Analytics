import React, { useState, useRef, useEffect, useCallback } from "react";
import Papa from "papaparse";
import {
  Upload,
  Play,
  AlertCircle,
  BarChart3,
  ArrowRight,
  MousePointerClick,
  FileSpreadsheet,
  Menu,
  X,
  Sparkles,
  Users,
  MapPin,
  ArrowLeft,
  Bot,
} from "lucide-react";
import { sampleCRMData } from "../utils/sampleData";

/* ═══════════════════════════════════════════════════
   KIA Logo — Modern connected wordmark SVG
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
   ScrollReveal Component Helper
   ═══════════════════════════════════════════════════ */
function ScrollReveal({ children, delay = 0 }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => setIsVisible(true), delay);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [delay]);

  return (
    <div
      ref={ref}
      className={`transition-all duration-1000 ease-out transform ${
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
      }`}
    >
      {children}
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   Typewriter Hook
   ═══════════════════════════════════════════════════ */
function useTypewriter(phrases, typingSpeed = 80, deletingSpeed = 40, pauseTime = 2000) {
  const [text, setText] = useState("");
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentPhrase = phrases[phraseIndex];
    let timeout;

    if (!isDeleting && text === currentPhrase) {
      timeout = setTimeout(() => setIsDeleting(true), pauseTime);
    } else if (isDeleting && text === "") {
      setIsDeleting(false);
      setPhraseIndex((prev) => (prev + 1) % phrases.length);
    } else {
      timeout = setTimeout(
        () => {
          setText(
            isDeleting
              ? currentPhrase.substring(0, text.length - 1)
              : currentPhrase.substring(0, text.length + 1)
          );
        },
        isDeleting ? deletingSpeed : typingSpeed
      );
    }

    return () => clearTimeout(timeout);
  }, [text, isDeleting, phraseIndex, phrases, typingSpeed, deletingSpeed, pauseTime]);

  return text;
}

/* ═══════════════════════════════════════════════════
   Simple Ripple Button Helper
   ═══════════════════════════════════════════════════ */
function RippleButton({ children, onClick, className = "", disabled = false, type = "button", id }) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`group relative overflow-hidden transition-all ${className}`}
      id={id}
    >
      {children}
    </button>
  );
}

/* ═══════════════════════════════════════════════════
   Simple Navbar
   ═══════════════════════════════════════════════════ */
function LandingNavbar({ onScrollTo, onBack, onOpenChat }) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { label: "Features", id: "features" },
    { label: "Models", id: "models" },
    { label: "Dashboard", id: "hero" },
  ];

  return (
    <nav
      className={`landing-navbar ${scrolled ? "landing-navbar--scrolled" : ""}`}
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="landing-navbar-inner">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="landing-logo-mark">
            <div className="landing-logo-mark-pulse" />
          </div>
          <KiaLogo className="landing-logo-wordmark" />
          <div className="landing-navbar-divider" />
          <span className="landing-navbar-tagline text-nowrap">Data Analytics</span>
        </div>

        {/* Desktop links */}
        <div className="landing-navbar-links">
          {onBack && (
            <button
              onClick={onBack}
              className="landing-navbar-link inline-flex items-center gap-1.5 font-bold text-white hover:text-kia-red cursor-pointer"
              title="Return to Showroom & Login"
            >
              <ArrowLeft size={14} className="text-kia-red" />
              <span>Back to Showroom</span>
            </button>
          )}
          {onOpenChat && (
            <button
              onClick={onOpenChat}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-kia-red/30 to-kia-red/20 hover:from-kia-red/50 hover:to-kia-red/30 border border-kia-red/50 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-kia-red cursor-pointer shadow-sm active:scale-95"
              title="Ask AI questions about your dealership dataset"
            >
              <Bot size={14} className="text-kia-red" />
              <span className="font-outfit font-bold hidden sm:inline">Ask AI Copilot</span>
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-kia-red opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-kia-red"></span>
              </span>
            </button>
          )}
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => onScrollTo(link.id)}
              className="landing-navbar-link"
            >
              {link.label}
            </button>
          ))}
          <button
            onClick={() => onScrollTo("hero")}
            className="landing-navbar-cta"
          >
            Access Dashboard
          </button>
        </div>

        {/* Mobile menu button */}
        <button
          className="landing-navbar-mobile-toggle"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle navigation menu"
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="landing-navbar-mobile-menu">
          {onBack && (
            <button
              onClick={() => { onBack(); setMobileOpen(false); }}
              className="landing-navbar-mobile-link inline-flex items-center gap-2 font-bold text-white"
            >
              <ArrowLeft size={14} className="text-kia-red" />
              <span>Back to Showroom</span>
            </button>
          )}
          {onOpenChat && (
            <button
              onClick={() => { onOpenChat(); setMobileOpen(false); }}
              className="landing-navbar-mobile-link inline-flex items-center gap-2 font-bold text-white"
            >
              <Bot size={14} className="text-kia-red" />
              <span>Ask AI Copilot</span>
            </button>
          )}
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => { onScrollTo(link.id); setMobileOpen(false); }}
              className="landing-navbar-mobile-link"
            >
              {link.label}
            </button>
          ))}
          <button
            onClick={() => { onScrollTo("hero"); setMobileOpen(false); }}
            className="landing-navbar-cta w-full justify-center"
          >
            Access Dashboard
          </button>
        </div>
      )}
    </nav>
  );
}

/* ═══════════════════════════════════════════════════
   MAIN COMPONENT — CSVLoader (Simple Landing page)
   ═══════════════════════════════════════════════════ */
export default function CSVLoader({ onDataLoaded, onBack, onOpenChat }) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);
  const [mounted, setMounted] = useState(false);

  const heroRef = useRef(null);
  const featuresRef = useRef(null);
  const modelsRef = useRef(null);

  const typewriterText = useTypewriter(
    ["Lead Conversion Intelligence", "Funnel Performance Analytics", "Consultant KPI Dashboard", "Geographic Market Insights"],
    70,
    35,
    2200
  );

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const scrollToSection = useCallback((id) => {
    const refs = { hero: heroRef, features: featuresRef, models: modelsRef };
    refs[id]?.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  /* ——— CSV Processing ——— */
  const processFile = (file) => {
    if (!file) return;
    if (file.type !== "text/csv" && !file.name.endsWith(".csv")) {
      setError("Please upload a valid CSV file.");
      return;
    }
    setLoading(true);
    setError(null);

    const KEY_MAPPING = {
      "enquiry date": "Enquiry Date",
      "enquirydate": "Enquiry Date",
      "model": "Model",
      "vehiclemodel": "Model",
      "vehicle model": "Model",
      "enquiry status": "Enquiry Status",
      "enquirystatus": "Enquiry Status",
      "status": "Enquiry Status",
      "consultant name": "Consultant Name",
      "consultantname": "Consultant Name",
      "consultant": "Consultant Name",
      "sales consultant": "Consultant Name",
      "source": "Source",
      "lead source": "Source",
      "leadsource": "Source",
      "source channel": "Source",
      "sourcechannel": "Source",
      "city": "City",
      "state": "State",
      "customer type": "Customer Type",
      "customertype": "Customer Type",
      "type": "Type",
      "lead type": "Type",
      "leadtype": "Type",
      "td status": "TD Status",
      "tdstatus": "TD Status",
      "test drive status": "TD Status",
      "test drive date": "Test Drive Date",
      "testdrivedate": "Test Drive Date",
      "booking date": "Booking Date",
      "bookingdate": "Booking Date",
      "retail date": "Retail Date",
      "retaildate": "Retail Date",
      "enquiry stage": "Enquiry Stage",
      "enquirystage": "Enquiry Stage",
      "lost reason": "Lost Reason",
      "lostreason": "Lost Reason",
      "lost date": "Lost Date",
      "lostdate": "Lost Date"
    };

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      complete: (results) => {
        setLoading(false);
        if (results.errors.length > 0) console.warn("CSV Parsing warning:", results.errors);
        if (results.data?.length > 0) {
          const firstRow = results.data[0];
          const requiredKeys = ["Enquiry Date", "Model", "Enquiry Status"];
          const missingKeys = requiredKeys.filter(
            (key) => !Object.keys(firstRow).some((k) => k.toLowerCase().trim() === key.toLowerCase().trim())
          );
          if (missingKeys.length > 0) {
            setError(`Invalid CSV schema. Missing: ${missingKeys.join(", ")}. Please use the Lead Management CRM dataset.`);
            return;
          }
          
          // Normalize keys to ensure matching standard casing across the app
          const normalizedData = results.data.map(row => {
            const newRow = {};
            Object.keys(row).forEach(k => {
              const cleanKey = k.toLowerCase().trim();
              const standardKey = KEY_MAPPING[cleanKey] || k;
              newRow[standardKey] = row[k];
            });
            return newRow;
          });

          onDataLoaded(normalizedData);
        } else {
          setError("The uploaded CSV file is empty.");
        }
      },
      error: (err) => {
        setLoading(false);
        setError("Error parsing the CSV file: " + err.message);
      },
    });
  };

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e) => { e.preventDefault(); setIsDragging(false); setError(null); processFile(e.dataTransfer.files[0]); };
  const handleFileInput = (e) => { setError(null); processFile(e.target.files[0]); };
  const loadDemo = () => {
    setLoading(true);
    setTimeout(() => { onDataLoaded(sampleCRMData); setLoading(false); }, 800);
  };

  return (
    <div className="landing-root">

      {/* ═══ Exploded Car Background Image ═══ */}
      <div 
        className="landing-simple-bg"
        style={{ backgroundImage: "url('/kia-ev9-exploded.jpg')" }}
        aria-hidden="true"
      />

      {/* Dark gradient overlays for readability */}
      <div className="landing-overlay-gradient" aria-hidden="true" />
      <div className="landing-overlay-vignette" aria-hidden="true" />

      {/* ═══ Glassmorphism Navbar ═══ */}
      <LandingNavbar onScrollTo={scrollToSection} onBack={onBack} onOpenChat={onOpenChat} />

      {/* ═══ Scrollable Content ═══ */}
      <div className="relative z-10 flex flex-col min-h-screen">

        {/* ──── HERO SECTION ──── */}
        <section
          ref={heroRef}
          id="hero-section"
          className="landing-hero-section"
        >
          <div className={`landing-hero-content ${mounted ? "landing-hero-content--visible" : ""}`}>

            {/* Status badge */}
            <div className="landing-status-badge">
              <div className="landing-status-dot" />
              <span>KIA India — Bhubaneswar Dealership</span>
            </div>

            {/* Main heading */}
            <h1 className="landing-hero-title">
              <span className="landing-hero-title-static">KIA Data Analytics</span>
              <br />
              <span className="landing-hero-title-gradient">
                {typewriterText}
              </span>
              <span className="landing-cursor">|</span>
            </h1>

            {/* Subtitle */}
            <p className="landing-hero-subtitle">
              Transform raw dealership data into actionable intelligence.
              Upload your CRM export to unlock powerful real-time analytics.
            </p>

            {/* ═══ Glassmorphism Upload Card ═══ */}
            <div className="landing-glass-card">
              <div className="landing-glass-card-glow" aria-hidden="true" />

              {/* Upload zone */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`landing-upload-zone ${isDragging ? "landing-upload-zone--active" : ""}`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileInput}
                  accept=".csv"
                  className="hidden"
                  aria-label="Upload CSV file"
                  id="csv-file-input"
                />

                {loading ? (
                  <div className="flex flex-col items-center" role="status" aria-live="polite">
                    <div className="landing-loader mb-4">
                      <div className="landing-loader-ring" />
                      <div className="landing-loader-ring reverse" />
                      <FileSpreadsheet size={20} className="landing-loader-icon" />
                    </div>
                    <p className="text-sm text-white font-medium">Processing your data...</p>
                    <div className="landing-progress-bar mt-3">
                      <div className="landing-progress-fill" />
                    </div>
                    <span className="sr-only">Loading, please wait</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center text-center">
                    <div className="landing-upload-icon">
                      <Upload className="text-kia-red" size={26} />
                      <div className="landing-upload-icon-ring" />
                    </div>
                    <p className="text-base font-bold text-white mb-1.5">
                      Drop your CRM export here
                    </p>
                    <p className="text-xs text-[var(--color-kia-muted)] flex items-center gap-2">
                      <MousePointerClick size={12} className="text-kia-red" />
                      or{" "}
                      <span className="text-kia-red hover:underline font-semibold cursor-pointer">
                        browse files
                      </span>{" "}
                      — supports .csv format
                    </p>
                  </div>
                )}
              </div>

              {/* Error message */}
              {error && (
                <div className="mt-4 p-3 rounded-lg bg-kia-red/10 border border-kia-red/20 flex items-start gap-3 animate-fade-in-up" role="alert">
                  <AlertCircle className="text-kia-red shrink-0 mt-0.5" size={16} />
                  <p className="text-xs text-kia-red leading-relaxed">{error}</p>
                </div>
              )}

              {/* Divider */}
              <div className="relative flex py-5 items-center">
                <div className="flex-grow border-t border-white/10" />
                <span className="flex-shrink mx-4 text-[10px] font-bold text-[var(--color-kia-muted)] uppercase tracking-[0.2em]">
                  or try the demo
                </span>
                <div className="flex-grow border-t border-white/10" />
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 items-center justify-center">
                <RippleButton
                  onClick={loadDemo}
                  disabled={loading}
                  className="landing-cta-primary"
                  aria-label="Access Dashboard — Load interactive demo dataset"
                  id="access-dashboard-btn"
                >
                  <span className="landing-cta-bg" />
                  <span className="relative z-10 flex items-center gap-3">
                    <BarChart3 size={18} />
                    Access Dashboard
                    <ArrowRight size={14} className="transition-transform group-hover:translate-x-1" />
                  </span>
                </RippleButton>

                <RippleButton
                  onClick={loadDemo}
                  disabled={loading}
                  className="landing-cta-secondary"
                  aria-label="Launch interactive demo"
                  id="demo-btn"
                >
                  <span className="relative z-10 flex items-center gap-3">
                    <Play size={14} />
                    Launch Demo
                  </span>
                </RippleButton>
              </div>

              <p className="text-[11px] text-[var(--color-kia-muted)] mt-4 text-center flex items-center justify-center gap-1.5">
                <Sparkles size={10} className="text-kia-orange" />
                20 leads across Sonet, Seltos, Carens & Syros — fully interactive
              </p>
            </div>

          </div>

          {/* Scroll indicator */}
          <div className={`landing-scroll-cue ${mounted ? "landing-scroll-cue--visible" : ""}`}>
            <span className="text-[10px] text-[var(--color-kia-muted)] tracking-widest uppercase">Explore</span>
            <div className="landing-scroll-indicator">
              <div className="landing-scroll-dot" />
            </div>
          </div>
        </section>

        {/* ──── STATS BAR ──── */}
        <ScrollReveal>
          <section className="py-10 px-4 border-y border-white/5 bg-black/20">
            <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
              {[
                { value: "3.5x", label: "TD conversion catalyst" },
                { value: "24.5%", label: "Average booking-to-delivery" },
                { value: "15 Mins", label: "Lead response time SLA" },
                { value: "8+", label: "Sourcing channels analyzed" }
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <p className="text-3xl md:text-4xl font-extrabold font-outfit text-white mb-2 bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">{stat.value}</p>
                  <p className="text-xs text-[var(--color-kia-muted)] uppercase tracking-wider">{stat.label}</p>
                </div>
              ))}
            </div>
          </section>
        </ScrollReveal>

        {/* ──── FEATURES SECTION ──── */}
        <ScrollReveal>
          <section ref={featuresRef} id="features-section" className="py-16 px-4 max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <p className="text-[10px] uppercase tracking-[0.3em] text-kia-red font-bold mb-3">Key Features</p>
              <h2 className="text-2xl md:text-3xl font-extrabold font-outfit text-white">
                Analytics Built for Bhubaneswar CRM
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  title: "Real-time Funnel Analysis",
                  desc: "Instantly trace lead states from initial enquiry to final retail delivery. Highlight drops and leakage bottlenecks.",
                  icon: BarChart3,
                  color: "#ea1537"
                },
                {
                  title: "Consultant KPIs",
                  desc: "Compare team conversion rates, response timelines, and booking volumes. Identify top consultants and coaches.",
                  icon: Users,
                  color: "#10b981"
                },
                {
                  title: "Market Intelligence",
                  desc: "Map leads geographically by city and state. Target high-converting postal districts and referral partners.",
                  icon: MapPin,
                  color: "#3b82f6"
                }
              ].map((feat, i) => (
                <div key={i} className="landing-glass-card text-left flex flex-col items-start gap-4">
                  <div className="p-3 rounded-xl bg-white/5 border border-white/10" style={{ color: feat.color }}>
                    <feat.icon size={22} />
                  </div>
                  <h3 className="text-lg font-bold text-white font-outfit">{feat.title}</h3>
                  <p className="text-xs text-[var(--color-kia-muted)] leading-relaxed">{feat.desc}</p>
                </div>
              ))}
            </div>
          </section>
        </ScrollReveal>

        {/* ──── MODELS SECTION ──── */}
        <ScrollReveal>
          <section ref={modelsRef} id="models-section" className="py-16 px-4 border-t border-white/5">
            <div className="text-center mb-10">
              <p className="text-[10px] uppercase tracking-[0.3em] text-kia-red font-bold mb-3">KIA Lineup</p>
              <h2 className="text-2xl md:text-3xl font-extrabold font-outfit text-white">
                Tracking Every Model
              </h2>
            </div>
            <div className="max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
              {[
                { name: "SELTOS", tagline: "The Badass SUV", color: "#ea1537" },
                { name: "SONET", tagline: "Wild by Design", color: "#f59e0b" },
                { name: "CARENS", tagline: "Inspire Everyday", color: "#3b82f6" },
                { name: "SYROS", tagline: "The Bold New SUV", color: "#10b981" },
                { name: "EV6", tagline: "Opposites United", color: "#8b5cf6" },
              ].map((car) => (
                <div key={car.name} className="landing-model-card" style={{ "--accent": car.color }}>
                  <p className="text-xl font-extrabold font-outfit" style={{ color: car.color }}>
                    {car.name}
                  </p>
                  <p className="text-[10px] text-[var(--color-kia-muted)] mt-1">{car.tagline}</p>
                </div>
              ))}
            </div>
          </section>
        </ScrollReveal>

        {/* ──── FINAL CTA ──── */}
        <ScrollReveal>
          <section className="py-16 px-4">
            <div className="max-w-3xl mx-auto text-center">
              <div className="landing-final-cta">
                <div className="landing-final-cta-glow" aria-hidden="true" />
                <h2 className="text-2xl md:text-3xl font-extrabold font-outfit text-white mb-4 relative z-10">
                  Ready to transform your{" "}
                  <span className="bg-gradient-to-r from-kia-red to-kia-orange bg-clip-text text-transparent">
                    dealership data
                  </span>
                  ?
                </h2>
                <p className="text-sm text-[var(--color-kia-muted)] mb-8 relative z-10 max-w-md mx-auto">
                  Upload your CSV or explore the demo to see the full power of the analytics dashboard.
                </p>
                <RippleButton
                  onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                  className="landing-cta-primary relative z-10"
                >
                  <span className="landing-cta-bg" />
                  <span className="relative z-10 flex items-center gap-3">
                    <Upload size={16} />
                    Get Started Now
                    <ArrowRight size={14} />
                  </span>
                </RippleButton>
              </div>
            </div>
          </section>
        </ScrollReveal>

        {/* ──── Footer ──── */}
        <footer className="relative z-10 border-t border-white/5 py-6 px-6">
          <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <KiaLogo className="h-6 text-white/50" />
              <div className="w-px h-4 bg-white/10" />
              <p className="text-[10px] text-[var(--color-kia-muted)] tracking-wider">
                Movement that inspires
              </p>
            </div>
            <div className="flex items-center gap-2">
              {["React", "Vite", "Recharts", "CRM-Analytics"].map((tech) => (
                <span
                  key={tech}
                  className="landing-tech-badge"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </footer>

      </div>

    </div>
  );
}
