import React, { useState, useEffect, useCallback } from "react";
import useEmblaCarousel from "embla-carousel-react";
import Autoplay from "embla-carousel-autoplay";
import { ChevronLeft, ChevronRight, RotateCw, ArrowUpRight, Sparkles } from "lucide-react";
import { kiaModels } from "../data/kiaModels";
import "./ModelSlider.css";

/**
 * ModelSlider — Horizontal carousel showcasing Kia India models
 * Features Embla carousel with touch swipe, mouse drag, autoplay (pauses on hover),
 * prev/next buttons, and click-to-open 360° viewer modal.
 */
export default function ModelSlider({ models = kiaModels, onSelectModel }) {
  const [emblaRef, emblaApi] = useEmblaCarousel(
    {
      loop: true,
      align: "start",
      skipSnaps: false,
      dragFree: false,
    },
    [
      Autoplay({
        delay: 3500,
        stopOnInteraction: false,
        stopOnMouseEnter: true,
      }),
    ]
  );

  const [prevBtnDisabled, setPrevBtnDisabled] = useState(false);
  const [nextBtnDisabled, setNextBtnDisabled] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [scrollSnaps, setScrollSnaps] = useState([]);

  const scrollPrev = useCallback(() => {
    if (emblaApi) emblaApi.scrollPrev();
  }, [emblaApi]);

  const scrollNext = useCallback(() => {
    if (emblaApi) emblaApi.scrollNext();
  }, [emblaApi]);

  const scrollTo = useCallback(
    (index) => {
      if (emblaApi) emblaApi.scrollTo(index);
    },
    [emblaApi]
  );

  const onSelect = useCallback(() => {
    if (!emblaApi) return;
    setSelectedIndex(emblaApi.selectedScrollSnap());
    setPrevBtnDisabled(!emblaApi.canScrollPrev());
    setNextBtnDisabled(!emblaApi.canScrollNext());
  }, [emblaApi]);

  useEffect(() => {
    if (!emblaApi) return;
    onSelect();
    setScrollSnaps(emblaApi.scrollSnapList());
    emblaApi.on("select", onSelect);
    emblaApi.on("reInit", onSelect);
    return () => {
      emblaApi.off("select", onSelect);
      emblaApi.off("reInit", onSelect);
    };
  }, [emblaApi, onSelect]);

  return (
    <section className="model-slider-wrapper" aria-label="Kia India Vehicle Lineup">
      {/* Slider Header */}
      <div className="model-slider-header">
        <div className="model-slider-title-group">
          <span className="model-slider-badge">
            <Sparkles size={11} />
            Showroom Lineup
          </span>
          <div>
            <h2 className="model-slider-title">Explore Kia Vehicles</h2>
            <p className="model-slider-subtitle">Click any model to launch interactive 360° studio rotation</p>
          </div>
        </div>

        {/* Carousel Navigation Arrows */}
        <div className="model-slider-controls">
          <button
            type="button"
            onClick={scrollPrev}
            className="model-slider-nav-btn"
            aria-label="Previous vehicle model"
            title="Previous"
            disabled={prevBtnDisabled}
          >
            <ChevronLeft size={18} />
          </button>
          <button
            type="button"
            onClick={scrollNext}
            className="model-slider-nav-btn"
            aria-label="Next vehicle model"
            title="Next"
            disabled={nextBtnDisabled}
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      {/* Embla Viewport */}
      <div className="model-slider-viewport" ref={emblaRef}>
        <div className="model-slider-container">
          {models.map((model) => (
            <div className="model-slide" key={model.id}>
              <div
                className="model-card"
                role="button"
                tabIndex={0}
                onClick={() => onSelectModel && onSelectModel(model)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    if (onSelectModel) onSelectModel(model);
                  }
                }}
                aria-label={`View 360 degree details for ${model.name}`}
              >
                {/* 360 Degree Pill Badge */}
                <div className="model-card-badge-360">
                  <RotateCw size={11} />
                  <span>360° Studio</span>
                </div>

                {/* Car Image Preview */}
                <div className="model-card-img-wrapper">
                  <img
                    src={model.image}
                    alt={model.name}
                    className="model-card-img"
                    loading="lazy"
                    decoding="async"
                    onError={(e) => {
                      console.error(`image missing: ${model.image}`);
                      e.target.style.display = "none";
                    }}
                  />
                </div>

                {/* Model Metadata */}
                <span className="model-card-category">{model.category || "Kia SUV"}</span>
                <h3 className="model-card-name">{model.name}</h3>
                <p className="model-card-tagline">{model.tagline}</p>

                {/* Action CTA */}
                <div className="model-card-action">
                  <span className="model-card-action-text">
                    <span>Interactive 360°</span>
                  </span>
                  <div className="model-card-action-icon" aria-hidden="true">
                    <ArrowUpRight size={13} />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pagination Dots */}
      <div className="model-slider-dots" role="tablist" aria-label="Model slides">
        {scrollSnaps.map((_, index) => (
          <button
            key={index}
            type="button"
            role="tab"
            aria-selected={index === selectedIndex}
            onClick={() => scrollTo(index)}
            className={`model-slider-dot ${index === selectedIndex ? "model-slider-dot--active" : ""}`}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </section>
  );
}
