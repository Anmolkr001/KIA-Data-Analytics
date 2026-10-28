/**
 * Kia India Lineup Dataset
 * Used by ModelSlider and Car360Viewer components on the Landing / Login Page.
 */

// Helper to generate 36 frame paths for 360 viewer
export function generate360Frames(modelFolder, count = 36) {
  const frames = [];
  for (let i = 1; i <= count; i++) {
    const padded = String(i).padStart(2, "0");
    frames.push(`/models/${modelFolder}/${padded}.jpg`);
  }
  return frames;
}

export const kiaModels = [
  {
    id: "ev6",
    name: "Kia EV6",
    tagline: "Fully Electric. Fully Inspired.",
    category: "Electric Crossover",
    image: "/models/ev6.jpg",
    has360: true,
    frameCount: 36,
    frames: generate360Frames("ev6", 36),
    specs: {
      range: "708 km (ARAI)",
      acceleration: "0-100 km/h in 5.2s",
      powertrain: "AWD / RWD Dual Motor",
      charging: "10-80% in 18 mins (350kW)",
    },
    accentColor: "#54A24B",
  },
  {
    id: "seltos",
    name: "Kia Seltos",
    tagline: "The Badass. Reborn.",
    category: "Mid-size SUV",
    image: "/models/seltos.jpg",
    has360: false, // Falling back to coming soon
    frameCount: 0,
    frames: [],
    specs: {
      engine: "Smartstream 1.5L Turbo GDi",
      power: "160 PS / 253 Nm",
      safety: "Level 2 ADAS (17 Autonomous Features)",
      seating: "5-Seater Premium Cabin",
    },
    accentColor: "#E45756",
  },
  {
    id: "sonet",
    name: "Kia Sonet",
    tagline: "The Wild. Reborn.",
    category: "Compact SUV",
    image: "/models/sonet.jpg",
    has360: false,
    frameCount: 0,
    frames: [],
    specs: {
      engine: "1.0L Turbo GDi / 1.5L CRDi",
      power: "120 PS / 172 Nm",
      safety: "Level 1 ADAS with 10 Features",
      transmission: "7-DCT / 6-iMT / 6-AT",
    },
    accentColor: "#FF6B6B",
  },
  {
    id: "carens",
    name: "Kia Carens",
    tagline: "From a Different World.",
    category: "Recreational Vehicle",
    image: "/models/carens.jpg",
    has360: false,
    frameCount: 0,
    frames: [],
    specs: {
      seating: "6 & 7 Seater Configurations",
      safety: "6 Airbags Standard Across All Trims",
      comfort: "One-Touch Electric Tumble 2nd Row",
      sunroof: "SkyLight Sunroof with Ambient Mood",
    },
    accentColor: "#4D96FF",
  },
  {
    id: "carens-clavis",
    name: "Kia Carens Clavis",
    tagline: "Born Electric, Built for Family.",
    category: "Next-Gen Electric RV",
    image: "/models/carens-clavis.jpg",
    has360: false,
    frameCount: 0,
    frames: [],
    specs: {
      powertrain: "Dedicated Pure Electric Architecture",
      range: "Up to 500 km Estimated Range",
      cockpit: "Panoramic Dual 12.3-inch Curved Displays",
      utility: "V2L (Vehicle-to-Load) Power Source",
    },
    accentColor: "#00D2D3",
  },
  {
    id: "syros",
    name: "Kia Syros",
    tagline: "The Progressive Compact SUV.",
    category: "Urban Compact SUV",
    image: "/models/syros.jpg",
    has360: false,
    frameCount: 0,
    frames: [],
    specs: {
      design: "Progressive EV-Inspired Silhouette",
      connectivity: "Kia Connect 2.0 with OTA Updates",
      cabin: "Lounge-Style Flexible Modular Seating",
      safety: "Full 360-degree Surround Camera",
    },
    accentColor: "#FD7272",
  },
  {
    id: "ev9",
    name: "Kia EV9",
    tagline: "Here to Reshape the Way We Move.",
    category: "Flagship Electric Luxury SUV",
    image: "/models/ev9.jpg",
    has360: false,
    frameCount: 0,
    frames: [],
    specs: {
      battery: "99.8 kWh 800V Ultra-Fast Architecture",
      range: "561 km (WLTP Expected)",
      seating: "Swiveling 2nd Row Executive Lounge",
      drive: "Dual Motor AWD (384 PS)",
    },
    accentColor: "#5F27CD",
  },
  {
    id: "carnival",
    name: "Kia Carnival",
    tagline: "The Grand Utility Vehicle.",
    category: "Ultra-Luxury Limousine",
    image: "/models/carnival.jpg",
    has360: false,
    frameCount: 0,
    frames: [],
    specs: {
      engine: "2.2L Smartstream Turbo Diesel",
      luxury: "VIP Lounge Seats with Leg Extenders",
      sound: "Bose 12-Speaker Premium Surround Audio",
      doors: "Dual Power Sliding Smart Doors",
    },
    accentColor: "#EECA3B",
  },
];

export default kiaModels;
