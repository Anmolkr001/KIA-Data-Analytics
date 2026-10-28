import React, { useState } from "react";
import "./HeroBackground.css";

/**
 * HeroBackground — Fullscreen studio background with soft luxury gradient overlay
 * Uses /hero-bg.jpg centered on the car with a gentle readability gradient.
 */
export default function HeroBackground({ src = "/hero-bg.jpg", alt = "Kia EV6 Exclusive Studio Background" }) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="hero-bg-container" aria-hidden="true">
      <img
        src={src}
        alt={alt}
        className="hero-bg-image"
        style={{ opacity: loaded ? 1 : 0 }}
        onLoad={() => setLoaded(true)}
        onError={() => {
          console.error(`image missing: ${src}`);
        }}
        loading="eager"
        decoding="async"
      />
      {/* Light gradient only behind the login card for readability */}
      <div className="hero-bg-overlay" />
    </div>
  );
}

