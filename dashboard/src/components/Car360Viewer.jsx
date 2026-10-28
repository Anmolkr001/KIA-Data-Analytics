import React, { useState, useEffect, useRef, useCallback } from "react";
import { X, Play, Pause, ChevronLeft, ChevronRight, RotateCcw, AlertCircle, Sparkles } from "lucide-react";
import "./Car360Viewer.css";

const DRAG_SENSITIVITY = 9; // Pixels dragged per frame rotation

/**
 * Car360Viewer — Interactive 360-degree image-sequence rotation modal.
 * Supports mouse & touch horizontal dragging, automatic rotation, frame preloading,
 * and graceful fallback with a "360° view coming soon" notice.
 */
export default function Car360Viewer({ model, models = [], onClose, onSelectModel }) {
  if (!model) return null;

  const totalFrames = model.frames?.length || 0;
  const hasFrames = model.has360 && totalFrames > 0;

  const [currentFrame, setCurrentFrame] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [autoRotate, setAutoRotate] = useState(false);
  const [loadedFrames, setLoadedFrames] = useState(0);
  const [isLoading, setIsLoading] = useState(hasFrames);
  const [imageError, setImageError] = useState(false);

  const startXRef = useRef(0);
  const frameOnStartRef = useRef(0);
  const autoRotateIntervalRef = useRef(null);
  const stageRef = useRef(null);

  // Current model index among models array
  const currentIndex = models.findIndex((m) => m.id === model.id);
  const prevModel = currentIndex > 0 ? models[currentIndex - 1] : models[models.length - 1];
  const nextModel = currentIndex < models.length - 1 ? models[currentIndex + 1] : models[0];

  // Reset state on model change
  useEffect(() => {
    setCurrentFrame(0);
    setLoadedFrames(0);
    setIsLoading(hasFrames);
    setImageError(false);
    setAutoRotate(false);
  }, [model.id, hasFrames]);

  // Preload frames for the active model only
  useEffect(() => {
    if (!hasFrames) {
      setIsLoading(false);
      return;
    }

    let isMounted = true;
    let count = 0;
    const images = [];

    // Preload image sequence
    model.frames.forEach((frameUrl) => {
      const img = new Image();
      img.src = frameUrl;
      img.onload = () => {
        if (!isMounted) return;
        count += 1;
        setLoadedFrames(count);
        // Remove loading spinner once at least first 6 frames or all are loaded
        if (count >= Math.min(6, totalFrames)) {
          setIsLoading(false);
        }
      };
      img.onerror = () => {
        if (!isMounted) return;
        console.error(`image missing: ${frameUrl}`);
        count += 1;
        setLoadedFrames(count);
        if (count === totalFrames && loadedFrames === 0) {
          setImageError(true);
          setIsLoading(false);
        }
      };
      images.push(img);
    });

    return () => {
      isMounted = false;
    };
  }, [model.frames, hasFrames, totalFrames]);

  // Auto-rotate logic (advances 1 frame every 75ms)
  useEffect(() => {
    if (autoRotate && hasFrames && !isDragging) {
      autoRotateIntervalRef.current = setInterval(() => {
        setCurrentFrame((prev) => (prev + 1) % totalFrames);
      }, 75);
    } else {
      if (autoRotateIntervalRef.current) {
        clearInterval(autoRotateIntervalRef.current);
      }
    }
    return () => {
      if (autoRotateIntervalRef.current) {
        clearInterval(autoRotateIntervalRef.current);
      }
    };
  }, [autoRotate, hasFrames, isDragging, totalFrames]);

  // Keyboard navigation & Esc to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        onClose();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        setCurrentFrame((prev) => (prev - 1 + totalFrames) % totalFrames);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        setCurrentFrame((prev) => (prev + 1) % totalFrames);
      } else if (e.key === " ") {
        e.preventDefault();
        setAutoRotate((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose, totalFrames]);

  // Drag interaction handlers
  const handleDragStart = useCallback(
    (clientX) => {
      if (!hasFrames) return;
      setIsDragging(true);
      startXRef.current = clientX;
      frameOnStartRef.current = currentFrame;
    },
    [hasFrames, currentFrame]
  );

  const handleDragMove = useCallback(
    (clientX) => {
      if (!isDragging || !hasFrames) return;
      const deltaX = clientX - startXRef.current;
      const frameDelta = Math.floor(deltaX / DRAG_SENSITIVITY);
      
      // Dragging right rotates clockwise; dragging left rotates counter-clockwise
      const newFrame = (frameOnStartRef.current - frameDelta) % totalFrames;
      setCurrentFrame(newFrame >= 0 ? newFrame : newFrame + totalFrames);
    },
    [isDragging, hasFrames, totalFrames]
  );

  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Mouse event wrappers
  const onMouseDown = (e) => {
    e.preventDefault();
    handleDragStart(e.clientX);
  };

  const onMouseMove = (e) => {
    handleDragMove(e.clientX);
  };

  const onMouseUp = () => {
    handleDragEnd();
  };

  // Touch event wrappers
  const onTouchStart = (e) => {
    if (e.touches.length > 0) {
      handleDragStart(e.touches[0].clientX);
    }
  };

  const onTouchMove = (e) => {
    if (e.touches.length > 0) {
      handleDragMove(e.touches[0].clientX);
    }
  };

  const onTouchEnd = () => {
    handleDragEnd();
  };

  // Calculated degree of current view
  const currentDegree = hasFrames ? Math.round((currentFrame / totalFrames) * 360) : 0;

  return (
    <div
      className="viewer-360-backdrop"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`360 degree viewer for ${model.name}`}
    >
      <div
        className="viewer-360-modal"
        onClick={(e) => e.stopPropagation()} // Prevent backdrop close
      >
        {/* Modal Top Header */}
        <header className="viewer-360-header">
          <div className="viewer-360-title-area">
            <span className="viewer-360-brand-badge">KIA 360°</span>
            <div>
              <h2 className="viewer-360-title">{model.name}</h2>
              <p className="viewer-360-tagline">{model.tagline}</p>
            </div>
          </div>

          <div className="viewer-360-actions">
            {/* Prev Model Button */}
            {prevModel && (
              <button
                type="button"
                onClick={() => onSelectModel(prevModel)}
                className="viewer-360-nav-btn"
                title={`Previous Model: ${prevModel.name}`}
                aria-label={`Switch to ${prevModel.name}`}
              >
                <ChevronLeft size={16} />
                <span className="hidden sm:inline">{prevModel.name}</span>
              </button>
            )}

            {/* Next Model Button */}
            {nextModel && (
              <button
                type="button"
                onClick={() => onSelectModel(nextModel)}
                className="viewer-360-nav-btn"
                title={`Next Model: ${nextModel.name}`}
                aria-label={`Switch to ${nextModel.name}`}
              >
                <span className="hidden sm:inline">{nextModel.name}</span>
                <ChevronRight size={16} />
              </button>
            )}

            {/* Close Button */}
            <button
              type="button"
              onClick={onClose}
              className="viewer-360-close-btn"
              aria-label="Close 360 degree viewer"
              title="Close (Esc)"
            >
              <X size={18} />
            </button>
          </div>
        </header>

        {/* Floating Controls Bar */}
        <div className="viewer-360-controls-bar">
          {hasFrames && !imageError ? (
            <>
              <div className="viewer-360-hint-pill">
                <RotateCcw size={12} className="animate-spin-slow" />
                <span>Drag horizontally to rotate</span>
              </div>

              <div style={{ display: "flex", gap: "8px", pointerEvents: "auto" }}>
                <div className="viewer-360-degree-badge">
                  {currentDegree}° • Frame {currentFrame + 1}/{totalFrames}
                </div>

                <button
                  type="button"
                  onClick={() => setAutoRotate((prev) => !prev)}
                  className={`viewer-360-auto-rotate-btn ${autoRotate ? "viewer-360-auto-rotate-btn--active" : ""}`}
                  aria-label={autoRotate ? "Pause auto rotation" : "Start auto rotation"}
                >
                  {autoRotate ? <Pause size={13} /> : <Play size={13} />}
                  <span>{autoRotate ? "Pause" : "Auto Rotate"}</span>
                </button>
              </div>
            </>
          ) : (
            <div className="viewer-360-hint-pill">
              <Sparkles size={12} className="text-amber-400" />
              <span>Studio Showcase</span>
            </div>
          )}
        </div>

        {/* Main 360 Turntable Stage */}
        <div
          ref={stageRef}
          className={`viewer-360-stage ${isDragging ? "viewer-360-stage--dragging" : ""}`}
          onMouseDown={onMouseDown}
          onMouseMove={isDragging ? onMouseMove : undefined}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseUp}
          onTouchStart={onTouchStart}
          onTouchMove={onTouchMove}
          onTouchEnd={onTouchEnd}
        >
          {/* Turntable Floor Glow */}
          <div className="viewer-360-turntable-glow" />

          {/* Preloading Progress Indicator */}
          {isLoading && (
            <div className="viewer-360-loading">
              <div className="viewer-360-spinner" />
              <p className="viewer-360-loading-text">
                Loading 360° Studio Sequence ({loadedFrames}/{totalFrames})...
              </p>
            </div>
          )}

          {/* 360 Image Sequence Display */}
          {hasFrames && !imageError ? (
            <img
              src={model.frames[currentFrame]}
              alt={`${model.name} 360 degree view frame ${currentFrame + 1}`}
              className="viewer-360-frame-img"
              draggable={false}
            />
          ) : (
            /* Graceful Fallback if model has no 360 frames */
            <>
              <img
                src={model.image}
                alt={`${model.name} Studio View`}
                className="viewer-360-frame-img"
                draggable={false}
                onError={(e) => {
                  console.error(`image missing: ${model.image}`);
                  e.target.style.display = "none";
                }}
              />
              <div className="viewer-360-coming-soon">
                <div className="viewer-360-coming-soon-badge">
                  <AlertCircle size={14} />
                  <span>360° View Coming Soon</span>
                </div>
                <p className="viewer-360-coming-soon-text">
                  The complete 360° sequence is currently being prepared for <strong>{model.name}</strong>.
                </p>
                {/* Switch to EV6 demo button */}
                {model.id !== "ev6" && (
                  <button
                    type="button"
                    onClick={() => {
                      const ev6Model = models.find((m) => m.id === "ev6");
                      if (ev6Model && onSelectModel) onSelectModel(ev6Model);
                    }}
                    className="viewer-360-switch-demo-btn"
                  >
                    View Kia EV6 in 360° →
                  </button>
                )}
              </div>
            </>
          )}
        </div>

        {/* Modal Footer: Technical Specifications Strip */}
        <footer className="viewer-360-footer">
          {model.specs ? (
            <div className="viewer-360-specs-grid">
              {Object.entries(model.specs).map(([key, value]) => (
                <div className="viewer-360-spec-item" key={key}>
                  <span className="viewer-360-spec-key">{key}</span>
                  <span className="viewer-360-spec-val">{value}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="viewer-360-specs-grid">
              <div className="viewer-360-spec-item">
                <span className="viewer-360-spec-key">Category</span>
                <span className="viewer-360-spec-val">{model.category || "Premium Kia Lineup"}</span>
              </div>
            </div>
          )}

          <div className="viewer-360-esc-hint">
            <span>Press</span>
            <kbd className="viewer-360-kbd">Esc</kbd>
            <span>or click background to exit</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
