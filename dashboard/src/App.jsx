import React, { useState, useMemo, useEffect } from "react";
import LoginScreen from "./components/LoginScreen";
import CSVLoader from "./components/CSVLoader";
import ExecutiveSummary from "./components/ExecutiveSummary";
import LeadFunnelStatus from "./components/LeadFunnelStatus";
import ConsultantPerformance from "./components/ConsultantPerformance";
import SourceEffectiveness from "./components/SourceEffectiveness";
import ModelInsights from "./components/ModelInsights";
import GeographicPerformance from "./components/GeographicPerformance";
import FunnelVelocity from "./components/FunnelVelocity";
import EnquiryAnalytics from "./components/EnquiryAnalytics";
import AskYourDataChat from "./components/AskYourDataChat";
import { filterData, getUniqueValues, getCityStateOptions } from "./utils/dataProcessor";
import { LogOut, Filter, Calendar, RotateCcw, BarChart3, Database, Sun, Moon, ArrowLeft, Bot, Sparkles } from "lucide-react";

// Dashboard Tabs definition
const TABS = [
  { id: "executive", label: "Executive Summary" },
  { id: "enquiry-analytics", label: "Enquiry Analytics" },
  { id: "funnel", label: "Lead Funnel & Status" },
  { id: "consultants", label: "Consultants Performance" },
  { id: "sources", label: "Channels Effectiveness" },
  { id: "products", label: "Model Insights" },
  { id: "geography", label: "Geographic Performance" },
  { id: "velocity", label: "Funnel Velocity" }
];

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return sessionStorage.getItem("kia-auth") === "true";
  });
  const [rawData, setRawData] = useState(null);

  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== "undefined") {
      const hash = window.location.hash.replace("#", "");
      if (TABS.some(t => t.id === hash)) return hash;
    }
    return "executive";
  });

  // Track tab history for in-app navigation
  const [tabHistory, setTabHistory] = useState(() => [activeTab]);
  const [historyIndex, setHistoryIndex] = useState(0);

  // Chatbox Copilot state
  const [chatOpen, setChatOpen] = useState(false);

  // Tab switch handler with browser history
  const handleTabChange = (newTab, pushState = true) => {
    if (newTab === activeTab) return;
    setActiveTab(newTab);
    if (pushState) {
      window.history.pushState({ type: "tab", tab: newTab }, "", `#${newTab}`);
      setTabHistory(prev => [...prev.slice(0, historyIndex + 1), newTab]);
      setHistoryIndex(prev => prev + 1);
    }
  };

  // Browser Back / Forward popstate listener
  useEffect(() => {
    const handlePopState = () => {
      const hash = window.location.hash.replace("#", "");
      if (TABS.some(t => t.id === hash)) {
        setActiveTab(hash);
        setTabHistory(prev => {
          const idx = prev.lastIndexOf(hash);
          if (idx !== -1) setHistoryIndex(idx);
          return prev;
        });
      } else if (hash === "upload") {
        setRawData(null);
      } else if (hash === "showroom" || hash === "login" || !hash) {
        if (!rawData) {
          setIsAuthenticated(false);
        } else {
          setRawData(null);
        }
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [rawData]);

  // Handle in-app "Back" button click
  const handleGoBack = () => {
    if (window.history.length > 1) {
      window.history.back();
    } else if (historyIndex > 0) {
      const prevTab = tabHistory[historyIndex - 1];
      setHistoryIndex(prev => prev - 1);
      setActiveTab(prevTab);
      window.location.hash = `#${prevTab}`;
    }
  };

  // Dark / Light Mode
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("kia-theme");
      return saved ? saved === "dark" : true;
    }
    return true;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add("theme-dark");
      root.classList.remove("theme-light");
    } else {
      root.classList.add("theme-light");
      root.classList.remove("theme-dark");
    }
    localStorage.setItem("kia-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  // Global Filters State
  const [filters, setFilters] = useState({
    startDate: "",
    endDate: "",
    model: "ALL",
    consultant: "ALL",
    source: "ALL",
    cityState: "ALL",
    leadType: "ALL"
  });

  // Extract filter dropdown options from raw data
  const filterOptions = useMemo(() => {
    if (!rawData) return { models: [], consultants: [], sources: [], cityStates: [], leadTypes: [] };
    
    // Normalize keys to standard headers for select extraction
    const models = getUniqueValues(rawData, "Model");
    const consultants = getUniqueValues(rawData, "Consultant Name");
    const sources = getUniqueValues(rawData, "Source");
    const cityStates = getCityStateOptions(rawData);
    const leadTypes = getUniqueValues(rawData, "Type");

    return { models, consultants, sources, cityStates, leadTypes };
  }, [rawData]);

  // Compute filtered dataset
  const filteredData = useMemo(() => {
    if (!rawData) return [];
    return filterData(rawData, filters);
  }, [rawData, filters]);

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      startDate: "",
      endDate: "",
      model: "ALL",
      consultant: "ALL",
      source: "ALL",
      cityState: "ALL",
      leadType: "ALL"
    });
  };

  // Unload CSV and return to upload screen
  const unloadData = () => {
    setRawData(null);
    resetFilters();
    setActiveTab("executive");
    window.history.pushState({ type: "upload" }, "", "#upload");
  };

  // Logout handler
  const handleLogout = () => {
    sessionStorage.removeItem("kia-auth");
    setIsAuthenticated(false);
    setRawData(null);
    resetFilters();
    setActiveTab("executive");
    window.history.pushState({ type: "showroom" }, "", "#showroom");
  };

  // Determine primary screen view
  let mainView = null;

  if (!isAuthenticated) {
    mainView = (
      <LoginScreen
        onLogin={() => {
          setIsAuthenticated(true);
          window.history.pushState({ type: "upload" }, "", "#upload");
        }}
        onOpenChat={() => setChatOpen(true)}
      />
    );
  } else if (!rawData) {
    mainView = (
      <CSVLoader
        onDataLoaded={(data) => {
          setRawData(data);
          window.history.pushState({ type: "tab", tab: "executive" }, "", "#executive");
        }}
        onBack={() => {
          sessionStorage.removeItem("kia-auth");
          setIsAuthenticated(false);
          window.history.pushState({ type: "showroom" }, "", "#showroom");
        }}
        onOpenChat={() => setChatOpen(true)}
      />
    );
  } else {
    mainView = (
      <div className={`min-h-screen flex flex-col font-sans transition-colors duration-300 ${darkMode ? "theme-dark bg-kia-dark text-kia-text" : "theme-light bg-kia-light-bg text-kia-light-text"}`}>
      
      {/* Accessibility: Skip-to-content link */}
      <a
        href="#main-content"
        className="sr-only sr-only-focusable"
        aria-label="Skip to main content"
      >
        Skip to main content
      </a>

      {/* Top Navbar */}
      <header className="sticky top-0 bg-kia-card/95 border-b border-kia-border z-40 px-4 md:px-6 py-3 md:py-4 flex flex-wrap items-center justify-between gap-2 backdrop-blur-md">
        <div className="flex items-center gap-3">
          {/* In-App Back Navigation Button */}
          <button
            onClick={handleGoBack}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white/90 bg-white/5 hover:bg-white/10 hover:text-white border border-kia-border rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-kia-red cursor-pointer shadow-sm active:scale-95"
            aria-label="Back to previous page"
            title="Go to previous page (Browser Back)"
          >
            <ArrowLeft size={14} className="text-kia-red" />
            <span className="font-outfit font-bold">Back</span>
          </button>

          <div className="h-8 w-8 rounded-lg bg-kia-red flex items-center justify-center text-white font-extrabold text-sm tracking-widest font-outfit">
            KIA
          </div>
          <div>
            <h1 className="text-lg font-bold text-[var(--color-kia-text)] tracking-tight font-outfit">
              Bhubaneswar Dealership Analytics
            </h1>
            <p className="text-[10px] text-kia-muted flex items-center gap-1.5 mt-0.5">
              <Database size={10} className="text-kia-green" />
              <span>Loaded: {rawData.length.toLocaleString()} leads</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Ask AI Copilot Button */}
          <button
            onClick={() => setChatOpen((prev) => !prev)}
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

          {/* Dark/Light Mode Toggle */}
          <button
            onClick={() => setDarkMode((prev) => !prev)}
            className="inline-flex items-center justify-center w-9 h-9 rounded-lg bg-white/5 hover:bg-white/10 border border-kia-border transition-all focus:outline-none focus:ring-2 focus:ring-kia-red"
            aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            title={darkMode ? "Light mode" : "Dark mode"}
          >
            {darkMode ? (
              <Sun size={16} className="text-kia-orange" />
            ) : (
              <Moon size={16} className="text-kia-blue" />
            )}
          </button>

          <button
            onClick={unloadData}
            className="inline-flex items-center gap-2 px-2 md:px-3 py-1.5 text-xs font-semibold text-kia-muted hover:text-white bg-white/5 hover:bg-white/10 border border-kia-border rounded-lg transition-all"
            title="Upload Another File"
          >
            <LogOut size={13} className="text-kia-red" />
            <span className="hidden md:inline">Upload Another File</span>
          </button>

          <button
            onClick={handleLogout}
            className="inline-flex items-center gap-2 px-2 md:px-3 py-1.5 text-xs font-semibold text-kia-muted hover:text-red-400 bg-white/5 hover:bg-red-500/10 border border-kia-border rounded-lg transition-all"
            title="Sign out"
          >
            <LogOut size={13} className="text-kia-red" />
            <span className="hidden md:inline">Sign Out</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
        <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6" tabIndex={-1}>
        
        {/* Global Filters Control Center */}
        <div className="p-5 rounded-xl bg-kia-card border border-kia-border shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-kia-border pb-2.5">
          <h3 className="text-sm font-bold text-[var(--color-kia-text)] flex items-center gap-2 uppercase tracking-wider">
              <Filter size={15} className="text-kia-red" />
              <span>Global Filter Center</span>
            </h3>
            <button
              onClick={resetFilters}
              className="inline-flex items-center gap-1.5 text-xs text-kia-muted hover:text-kia-red transition-colors"
            >
              <RotateCcw size={12} />
              <span>Reset Filters</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            
            {/* Filter: Model */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-kia-muted uppercase tracking-wider">Vehicle Model</label>
              <select
                value={filters.model}
                onChange={(e) => handleFilterChange("model", e.target.value)}
                className="w-full bg-kia-dark border border-kia-border rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-kia-red cursor-pointer"
              >
                {filterOptions.models.map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            {/* Filter: Consultant */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-kia-muted uppercase tracking-wider">Consultant</label>
              <select
                value={filters.consultant}
                onChange={(e) => handleFilterChange("consultant", e.target.value)}
                className="w-full bg-kia-dark border border-kia-border rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-kia-red cursor-pointer"
              >
                {filterOptions.consultants.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* Filter: Sourcing Channel */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-kia-muted uppercase tracking-wider">Source Channel</label>
              <select
                value={filters.source}
                onChange={(e) => handleFilterChange("source", e.target.value)}
                className="w-full bg-kia-dark border border-kia-border rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-kia-red cursor-pointer"
              >
                {filterOptions.sources.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            {/* Filter: Territory (City/State) */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-kia-muted uppercase tracking-wider">Territory (City)</label>
              <select
                value={filters.cityState}
                onChange={(e) => handleFilterChange("cityState", e.target.value)}
                className="w-full bg-kia-dark border border-kia-border rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-kia-red cursor-pointer"
              >
                {filterOptions.cityStates.map(cs => (
                  <option key={cs} value={cs}>{cs}</option>
                ))}
              </select>
            </div>

            {/* Filter: Date Range Start */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-kia-muted uppercase tracking-wider">Start Date</label>
              <div className="relative">
                <input
                  type="date"
                  value={filters.startDate}
                  onChange={(e) => handleFilterChange("startDate", e.target.value)}
                  className="w-full bg-kia-dark border border-kia-border rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-kia-red cursor-pointer"
                />
              </div>
            </div>

            {/* Filter: Date Range End */}
            <div className="flex flex-col gap-1">
              <label className="text-[10px] font-bold text-kia-muted uppercase tracking-wider">End Date</label>
              <div className="relative">
                <input
                  type="date"
                  value={filters.endDate}
                  onChange={(e) => handleFilterChange("endDate", e.target.value)}
                  className="w-full bg-kia-dark border border-kia-border rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-kia-red cursor-pointer"
                />
              </div>
            </div>

          </div>
        </div>

        {/* Tab Navigation Menu */}
        <div className="border-b border-kia-border">
          <nav
            className="flex flex-wrap -mb-px gap-2"
            role="tablist"
            aria-label="Dashboard sections"
          >
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                role="tab"
                id={`tab-${tab.id}`}
                aria-selected={activeTab === tab.id}
                aria-controls={`tabpanel-${tab.id}`}
                tabIndex={activeTab === tab.id ? 0 : -1}
                className={`py-3 px-4 text-xs md:text-sm font-semibold border-b-2 rounded-t-lg transition-all cursor-pointer ${
                  activeTab === tab.id
                    ? "border-kia-red text-kia-red bg-white/[0.02]"
                    : "border-transparent text-kia-muted hover:text-[var(--color-kia-text)] hover:border-kia-border"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Dynamic Display Panel */}
        <div
          className="min-h-[400px]"
          role="tabpanel"
          id={`tabpanel-${activeTab}`}
          aria-labelledby={`tab-${activeTab}`}
        >
          {filteredData.length === 0 ? (
            <div className="p-12 text-center rounded-xl bg-kia-card border border-kia-border flex flex-col items-center justify-center space-y-3">
              <RotateCcw className="text-kia-muted animate-spin" size={32} />
              <h4 className="text-lg font-bold text-[var(--color-kia-text)]">No Lead Records Match Current Filters</h4>
              <p className="text-xs text-kia-muted max-w-sm">
                Try widening your date ranges or resetting selected categories in the global filters panel.
              </p>
              <button
                onClick={resetFilters}
                className="mt-2 inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold bg-kia-red hover:bg-kia-red-hover text-white rounded-lg transition-all"
              >
                Reset Filter Choices
              </button>
            </div>
          ) : (
            <>
              {activeTab === "executive" && <ExecutiveSummary data={filteredData} />}
              {activeTab === "enquiry-analytics" && <EnquiryAnalytics data={filteredData} />}
              {activeTab === "funnel" && <LeadFunnelStatus data={filteredData} />}
              {activeTab === "consultants" && <ConsultantPerformance data={filteredData} />}
              {activeTab === "sources" && <SourceEffectiveness data={filteredData} />}
              {activeTab === "products" && <ModelInsights data={filteredData} />}
              {activeTab === "geography" && <GeographicPerformance data={filteredData} />}
              {activeTab === "velocity" && <FunnelVelocity data={filteredData} />}
            </>
          )}
        </div>

      </main>

      {/* Corporate Footer */}
      <footer className="bg-kia-card border-t border-kia-border px-6 py-4 mt-12 text-center">
        <p className="text-[10px] text-kia-muted tracking-widest uppercase">
          Lead Conversion Intelligence Dashboard &copy; 2026. Bhubaneswar Kia dealership.
        </p>
      </footer>
    </div>
  );
  }

  return (
    <>
      {mainView}

      {/* KIA AI Dealership Analytics Copilot Chatbox — Globally Accessible */}
      <AskYourDataChat
        rawData={rawData}
        isOpen={chatOpen}
        onOpen={() => setChatOpen(true)}
        onClose={() => setChatOpen(false)}
      />
    </>
  );
}
