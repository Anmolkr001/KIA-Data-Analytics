import React, { useRef, useMemo, useState, useEffect } from "react";
import * as THREE from "three";

/* ═══════════════════════════════════════════════════
   FALLBACK CHECK — Detect if WebGL is available
   ═══════════════════════════════════════════════════ */
function isWebGLAvailable() {
  try {
    const canvas = document.createElement("canvas");
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
    );
  } catch {
    return false;
  }
}

/* ═══════════════════════════════════════════════════
   CSS-ONLY ANIMATED BACKGROUND (Always rendered)
   ═══════════════════════════════════════════════════ */
function CSSAnimatedBackground() {
  const particles = useMemo(() =>
    Array.from({ length: 60 }, (_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      size: Math.random() * 4 + 1,
      duration: Math.random() * 30 + 15,
      delay: Math.random() * 15,
      opacity: Math.random() * 0.5 + 0.1,
      color: i % 5 === 0 ? "#ea1537" : i % 5 === 1 ? "#3b82f6" : i % 5 === 2 ? "#f59e0b" : i % 5 === 3 ? "#8b5cf6" : "rgba(255,255,255,0.6)",
    })), []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
      {/* Animated perspective grid */}
      <div className="landing-grid-bg">
        <div className="landing-grid-lines" />
      </div>

      {/* Large gradient orbs */}
      <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full blur-[150px] gradient-orb-1"
        style={{ background: "radial-gradient(circle, rgba(234,21,55,0.12), transparent 70%)" }} />
      <div className="absolute -bottom-60 -left-40 w-[700px] h-[700px] rounded-full blur-[160px] gradient-orb-2"
        style={{ background: "radial-gradient(circle, rgba(59,130,246,0.1), transparent 70%)" }} />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full blur-[120px] gradient-orb-3"
        style={{ background: "radial-gradient(circle, rgba(139,92,246,0.08), transparent 70%)" }} />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full blur-[100px] gradient-orb-1"
        style={{ background: "radial-gradient(circle, rgba(245,158,11,0.06), transparent 70%)", animationDelay: "5s" }} />

      {/* Floating particles */}
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute rounded-full particle-drift"
          style={{
            left: p.left,
            top: p.top,
            width: `${p.size}px`,
            height: `${p.size}px`,
            backgroundColor: p.color,
            opacity: p.opacity,
            animationDuration: `${p.duration}s`,
            animationDelay: `${p.delay}s`,
          }}
        />
      ))}

      {/* Floating car segment silhouettes — CSS shapes */}
      <div className="car-segment-float car-segment-1" />
      <div className="car-segment-float car-segment-2" />
      <div className="car-segment-float car-segment-3" />
      <div className="car-segment-float car-segment-4" />
      <div className="car-segment-float car-segment-5" />
      <div className="car-segment-float car-segment-6" />
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   THREE.JS 3D SCENE WITH INTERACTION
   ═══════════════════════════════════════════════════ */
function ThreeScene({ isDragging, setIsDragging }) {
  const mountRef = useRef(null);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    let renderer, scene, camera, animationId;
    let segments = [];
    
    // Create master group for rotation/parallax interaction
    const masterGroup = new THREE.Group();

    // Interaction variables
    let mouseX = 0;
    let mouseY = 0;
    let dragRotation = { x: 0.1, y: -0.2 }; // default starting tilt
    let dragStart = { x: 0, y: 0 };
    let dragStartRotation = { x: 0, y: 0 };

    try {
      // Scene setup
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(55, container.clientWidth / container.clientHeight, 0.1, 50);
      camera.position.set(0, 0, 6.2);

      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
      });
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
      renderer.setClearColor(0x000000, 0);
      container.appendChild(renderer.domElement);

      // Handle context loss gracefully
      renderer.domElement.addEventListener("webglcontextlost", (e) => {
        e.preventDefault();
        setHasError(true);
        if (animationId) cancelAnimationFrame(animationId);
      });

      // Add masterGroup to scene
      scene.add(masterGroup);

      // Lighting
      const ambientLight = new THREE.AmbientLight(0x8090b0, 0.25);
      scene.add(ambientLight);

      const keyLight = new THREE.DirectionalLight(0xfff5e6, 1.3);
      keyLight.position.set(5, 6, 4);
      scene.add(keyLight);

      const fillLight = new THREE.DirectionalLight(0xa0c0ff, 0.6);
      fillLight.position.set(-4, 2, 3);
      scene.add(fillLight);

      const rimLight = new THREE.DirectionalLight(0xff4060, 0.7);
      rimLight.position.set(0, -2, -5);
      scene.add(rimLight);

      const redSpot = new THREE.PointLight(0xea1537, 1.0, 15, 2);
      redSpot.position.set(0, -5, 2);
      scene.add(redSpot);

      const blueSpot = new THREE.PointLight(0x3b82f6, 0.5, 12, 2);
      blueSpot.position.set(-6, 3, -2);
      scene.add(blueSpot);

      // --- CAR SEGMENT 1: LED Headlight ---
      const headlightGroup = new THREE.Group();
      const housingShape = new THREE.Shape();
      housingShape.moveTo(-0.8, -0.3);
      housingShape.lineTo(0.8, -0.2);
      housingShape.quadraticCurveTo(1.0, 0, 0.9, 0.3);
      housingShape.lineTo(0.3, 0.4);
      housingShape.quadraticCurveTo(-0.2, 0.45, -0.8, 0.2);
      housingShape.quadraticCurveTo(-1.0, 0, -0.8, -0.3);

      const housingMesh = new THREE.Mesh(
        new THREE.ExtrudeGeometry(housingShape, { depth: 0.35, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 3 }),
        new THREE.MeshStandardMaterial({ color: 0x1a1a2e, metalness: 0.9, roughness: 0.15 })
      );
      headlightGroup.add(housingMesh);

      // DRL strip
      const drlPts = [];
      for (let i = 0; i <= 20; i++) {
        const t = i / 20;
        drlPts.push(new THREE.Vector3(-0.6 + t * 1.4, -0.05 + Math.sin(t * Math.PI * 0.3) * 0.15, 0.36));
      }
      const drlMesh = new THREE.Mesh(
        new THREE.TubeGeometry(new THREE.CatmullRomCurve3(drlPts), 20, 0.025, 8, false),
        new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xa0d4ff, emissiveIntensity: 2.5, metalness: 0.1, roughness: 0.1 })
      );
      headlightGroup.add(drlMesh);

      // Glow plane
      const glowMesh = new THREE.Mesh(
        new THREE.PlaneGeometry(1.8, 0.4),
        new THREE.MeshBasicMaterial({ color: 0x4da8ff, transparent: true, opacity: 0.35, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false })
      );
      glowMesh.position.set(0.1, 0.02, 0.42);
      headlightGroup.add(glowMesh);

      headlightGroup.position.set(-3.5, 1.8, -1);
      headlightGroup.rotation.set(0.1, 0.5, -0.1);
      headlightGroup.scale.setScalar(1.6);
      masterGroup.add(headlightGroup);
      segments.push({ mesh: headlightGroup, speed: 0.003, bobSpeed: 0.5, bobAmp: 0.1, drl: drlMesh, glow: glowMesh });

      // --- CAR SEGMENT 2: Tiger-Nose Grille ---
      const grilleGroup = new THREE.Group();
      const grilleFrame = new THREE.Shape();
      grilleFrame.moveTo(-0.95, 0);
      grilleFrame.quadraticCurveTo(-0.95, 0.38, -0.5, 0.4);
      grilleFrame.lineTo(0.5, 0.4);
      grilleFrame.quadraticCurveTo(0.95, 0.38, 0.95, 0);
      grilleFrame.quadraticCurveTo(0.95, -0.38, 0.5, -0.4);
      grilleFrame.lineTo(-0.5, -0.4);
      grilleFrame.quadraticCurveTo(-0.95, -0.38, -0.95, 0);

      const grilleHole = new THREE.Path();
      grilleHole.moveTo(-0.82, 0);
      grilleHole.quadraticCurveTo(-0.82, 0.3, -0.42, 0.32);
      grilleHole.lineTo(0.42, 0.32);
      grilleHole.quadraticCurveTo(0.82, 0.3, 0.82, 0);
      grilleHole.quadraticCurveTo(0.82, -0.3, 0.42, -0.32);
      grilleHole.lineTo(-0.42, -0.32);
      grilleHole.quadraticCurveTo(-0.82, -0.3, -0.82, 0);
      grilleFrame.holes.push(grilleHole);

      const frameMesh = new THREE.Mesh(
        new THREE.ExtrudeGeometry(grilleFrame, { depth: 0.08, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.015, bevelSegments: 3 }),
        new THREE.MeshStandardMaterial({ color: 0xc0c0c0, metalness: 0.95, roughness: 0.08 })
      );
      grilleGroup.add(frameMesh);

      // Diamond pattern
      for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 7; c++) {
          const xOff = r % 2 === 0 ? 0 : 0.11;
          const x = -0.7 + c * 0.22 + xOff;
          const y = -0.2 + r * 0.14;
          if (Math.sqrt((x / 0.95) ** 2 + (y / 0.35) ** 2) < 0.85) {
            const diamond = new THREE.Mesh(
              new THREE.BoxGeometry(0.09, 0.09, 0.06),
              new THREE.MeshStandardMaterial({ color: 0x1a1a2e, metalness: 0.85, roughness: 0.2 })
            );
            diamond.position.set(x, y, 0.04);
            diamond.rotation.z = Math.PI / 4;
            grilleGroup.add(diamond);
          }
        }
      }

      // Red accent strip
      const accentStrip = new THREE.Mesh(
        new THREE.BoxGeometry(0.8, 0.02, 0.09),
        new THREE.MeshStandardMaterial({ color: 0xea1537, emissive: 0xea1537, emissiveIntensity: 0.8, metalness: 0.5, roughness: 0.3 })
      );
      accentStrip.position.set(0, 0.36, 0.04);
      grilleGroup.add(accentStrip);

      grilleGroup.position.set(3.2, -0.5, -2);
      grilleGroup.rotation.set(0, -0.3, 0.05);
      grilleGroup.scale.setScalar(1.8);
      masterGroup.add(grilleGroup);
      segments.push({ mesh: grilleGroup, speed: 0.004, bobSpeed: 0.3, bobAmp: 0.05 });

      // --- CAR SEGMENT 3: Alloy Wheel ---
      const wheelGroup = new THREE.Group();

      // Outer rim
      wheelGroup.add(new THREE.Mesh(
        new THREE.TorusGeometry(0.7, 0.08, 16, 48),
        new THREE.MeshStandardMaterial({ color: 0xb8b8c8, metalness: 0.95, roughness: 0.1 })
      ));

      // Tire
      wheelGroup.add(new THREE.Mesh(
        new THREE.TorusGeometry(0.82, 0.14, 16, 48),
        new THREE.MeshStandardMaterial({ color: 0x1a1a1e, metalness: 0.1, roughness: 0.85 })
      ));

      // Spokes
      for (let i = 0; i < 10; i++) {
        const angle = (i / 10) * Math.PI * 2;
        const x1 = Math.cos(angle) * 0.15, y1 = Math.sin(angle) * 0.15;
        const x2 = Math.cos(angle) * 0.58, y2 = Math.sin(angle) * 0.58;
        const spoke = new THREE.Mesh(
          new THREE.BoxGeometry(0.045, Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 0.06),
          new THREE.MeshStandardMaterial({ color: 0xa0a0b0, metalness: 0.93, roughness: 0.12 })
        );
        spoke.position.set((x1 + x2) / 2, (y1 + y2) / 2, 0);
        spoke.rotation.z = angle - Math.PI / 2;
        wheelGroup.add(spoke);
      }

      // Center hub
      const hub = new THREE.Mesh(
        new THREE.CylinderGeometry(0.15, 0.15, 0.1, 24),
        new THREE.MeshStandardMaterial({ color: 0xd0d0d8, metalness: 0.97, roughness: 0.05 })
      );
      wheelGroup.add(hub);

      // Brake caliper
      const caliper = new THREE.Mesh(
        new THREE.BoxGeometry(0.15, 0.08, 0.05),
        new THREE.MeshStandardMaterial({ color: 0xea1537, emissive: 0xea1537, emissiveIntensity: 0.4, metalness: 0.6, roughness: 0.3 })
      );
      caliper.position.set(0.35, 0.15, -0.02);
      wheelGroup.add(caliper);

      wheelGroup.position.set(-2.5, -2.2, -1.5);
      wheelGroup.rotation.set(0.3, 0.2, 0);
      wheelGroup.scale.setScalar(1.3);
      masterGroup.add(wheelGroup);
      segments.push({ mesh: wheelGroup, speed: 0.008, bobSpeed: 0.4, bobAmp: 0.08, isWheel: true });

      // --- CAR SEGMENT 4: Side Mirror ---
      const mirrorGroup = new THREE.Group();
      mirrorGroup.add(new THREE.Mesh(
        new THREE.CapsuleGeometry(0.2, 0.35, 8, 16),
        new THREE.MeshStandardMaterial({ color: 0x1a1a2e, metalness: 0.85, roughness: 0.15 })
      ));
      const mirrorFace = new THREE.Mesh(
        new THREE.CircleGeometry(0.17, 24),
        new THREE.MeshStandardMaterial({ color: 0xe0e8f0, metalness: 0.99, roughness: 0.02 })
      );
      mirrorFace.position.z = 0.18;
      mirrorGroup.add(mirrorFace);

      const stalk = new THREE.Mesh(
        new THREE.CapsuleGeometry(0.04, 0.3, 4, 8),
        new THREE.MeshStandardMaterial({ color: 0x1a1a2e, metalness: 0.8, roughness: 0.2 })
      );
      stalk.position.set(-0.25, -0.1, 0);
      stalk.rotation.z = -0.4;
      mirrorGroup.add(stalk);

      const indicator = new THREE.Mesh(
        new THREE.BoxGeometry(0.2, 0.02, 0.02),
        new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xf59e0b, emissiveIntensity: 1.5, metalness: 0.3, roughness: 0.3 })
      );
      indicator.position.set(0, -0.22, 0.12);
      indicator.rotation.x = 0.3;
      mirrorGroup.add(indicator);

      mirrorGroup.position.set(3.8, 2.5, -0.5);
      mirrorGroup.rotation.set(0, -0.6, 0.1);
      mirrorGroup.scale.setScalar(1.5);
      masterGroup.add(mirrorGroup);
      segments.push({ mesh: mirrorGroup, speed: 0.005, bobSpeed: 0.6, bobAmp: 0.06, indicator });

      // --- CAR SEGMENT 5: Exhaust Tips ---
      const exhaustGroup = new THREE.Group();
      const createPipe = (xOff) => {
        const g = new THREE.Group();
        g.add(new THREE.Mesh(
          new THREE.TorusGeometry(0.14, 0.025, 12, 24),
          new THREE.MeshStandardMaterial({ color: 0xd0d0d8, metalness: 0.97, roughness: 0.04 })
        ));
        const pipeBody = new THREE.Mesh(
          new THREE.CylinderGeometry(0.13, 0.11, 0.4, 24, 1, true),
          new THREE.MeshStandardMaterial({ color: 0x2a2a35, metalness: 0.85, roughness: 0.2, side: THREE.DoubleSide })
        );
        pipeBody.rotation.x = Math.PI / 2;
        g.add(pipeBody);
        g.position.x = xOff;
        return g;
      };
      exhaustGroup.add(createPipe(-0.18));
      exhaustGroup.add(createPipe(0.18));

      const basePlate = new THREE.Mesh(
        new THREE.BoxGeometry(0.6, 0.05, 0.25),
        new THREE.MeshStandardMaterial({ color: 0x1a1a22, metalness: 0.8, roughness: 0.25 })
      );
      basePlate.position.set(0, 0, -0.2);
      basePlate.rotation.x = Math.PI / 2;
      exhaustGroup.add(basePlate);

      // Heat glow
      const heat1 = new THREE.Mesh(
        new THREE.CircleGeometry(0.09, 16),
        new THREE.MeshBasicMaterial({ color: 0xea4a2a, transparent: true, opacity: 0.15, blending: THREE.AdditiveBlending, depthWrite: false })
      );
      heat1.position.set(-0.18, 0, -0.08);
      exhaustGroup.add(heat1);
      const heat2 = heat1.clone();
      heat2.position.x = 0.18;
      exhaustGroup.add(heat2);

      exhaustGroup.position.set(0.5, -3, -2.5);
      exhaustGroup.rotation.set(0.2, 0.4, 0);
      exhaustGroup.scale.setScalar(1.7);
      masterGroup.add(exhaustGroup);
      segments.push({ mesh: exhaustGroup, speed: 0.003, bobSpeed: 0.35, bobAmp: 0.06, heat1, heat2 });

      // --- Additional distant segments for depth ---
      const headlight2 = headlightGroup.clone();
      headlight2.position.set(5, 0.5, -5);
      headlight2.rotation.set(0, 1.2, 0);
      headlight2.scale.setScalar(0.9);
      masterGroup.add(headlight2);
      segments.push({ mesh: headlight2, speed: 0.002, bobSpeed: 0.45, bobAmp: 0.12 });

      const wheel2 = wheelGroup.clone();
      wheel2.position.set(-5, 3, -4);
      wheel2.rotation.set(0.5, 0, 0.3);
      wheel2.scale.setScalar(0.7);
      masterGroup.add(wheel2);
      segments.push({ mesh: wheel2, speed: 0.006, bobSpeed: 0.35, bobAmp: 0.1, isWheel: true });

      // --- Ambient particles ---
      const particleCount = 150;
      const positions = new Float32Array(particleCount * 3);
      const colors = new Float32Array(particleCount * 3);
      for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 20;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 14;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 12;
        const cc = Math.random();
        if (cc < 0.3) { colors[i * 3] = 0.92; colors[i * 3 + 1] = 0.08; colors[i * 3 + 2] = 0.22; }
        else if (cc < 0.5) { colors[i * 3] = 0.23; colors[i * 3 + 1] = 0.51; colors[i * 3 + 2] = 0.96; }
        else { colors[i * 3] = 0.7; colors[i * 3 + 1] = 0.7; colors[i * 3 + 2] = 0.8; }
      }
      const particleGeom = new THREE.BufferGeometry();
      particleGeom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      particleGeom.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      const particlesMesh = new THREE.Points(particleGeom, new THREE.PointsMaterial({
        size: 0.05, vertexColors: true, transparent: true, opacity: 0.6,
        sizeAttenuation: true, depthWrite: false, blending: THREE.AdditiveBlending,
      }));
      masterGroup.add(particlesMesh);

      // --- Interactive event listeners ---
      const handleMouseMove = (e) => {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
      };

      const handleMouseDown = (e) => {
        setIsDragging(true);
        dragStart.x = e.clientX;
        dragStart.y = e.clientY;
        dragStartRotation.x = dragRotation.x;
        dragStartRotation.y = dragRotation.y;
      };

      const handleWindowMouseUp = () => {
        setIsDragging(false);
      };

      const handleWindowMouseMove = (e) => {
        if (!isDragging) return;
        const deltaX = e.clientX - dragStart.x;
        const deltaY = e.clientY - dragStart.y;
        
        // Horizontal dragging spins around Y-axis, Vertical dragging tilts X-axis
        dragRotation.y = dragStartRotation.y + deltaX * 0.007;
        dragRotation.x = dragStartRotation.x + deltaY * 0.007;

        // Limit vertical tilt to prevent turning completely upside down
        dragRotation.x = Math.max(-0.6, Math.min(0.6, dragRotation.x));
      };

      window.addEventListener("mousemove", handleMouseMove);
      container.addEventListener("mousedown", handleMouseDown);
      window.addEventListener("mouseup", handleWindowMouseUp);
      window.addEventListener("mousemove", handleWindowMouseMove);

      // --- Animation loop ---
      const clock = new THREE.Clock();
      const animate = () => {
        animationId = requestAnimationFrame(animate);
        const elapsed = clock.getElapsedTime();

        segments.forEach((seg) => {
          if (seg.isWheel) {
            seg.mesh.rotation.z += seg.speed;
          } else {
            seg.mesh.rotation.y += seg.speed;
          }
          seg.mesh.rotation.x = Math.sin(elapsed * seg.bobSpeed) * seg.bobAmp;
          // Subtle vertical float
          seg.mesh.position.y += Math.sin(elapsed * 0.5 + segments.indexOf(seg)) * 0.0003;

          // Pulse DRL
          if (seg.drl) {
            seg.drl.material.emissiveIntensity = 2 + Math.sin(elapsed * 2) * 0.8;
          }
          if (seg.glow) {
            seg.glow.material.opacity = 0.3 + Math.sin(elapsed * 2) * 0.15;
          }
          // Blink indicator
          if (seg.indicator) {
            seg.indicator.material.emissiveIntensity = Math.sin(elapsed * 4) > 0.3 ? 1.5 : 0.2;
          }
          // Heat shimmer
          if (seg.heat1) {
            seg.heat1.material.opacity = 0.1 + Math.sin(elapsed * 3) * 0.08;
          }
          if (seg.heat2) {
            seg.heat2.material.opacity = 0.1 + Math.cos(elapsed * 3.5) * 0.08;
          }
        });

        // Rotate particles slowly
        particlesMesh.rotation.y = elapsed * 0.02;

        // Calculate target rotation combining manual dragging & mouse parallax
        const targetRotX = dragRotation.x + (mouseY * 0.18);
        const targetRotY = dragRotation.y + (mouseX * 0.18);

        // Smoothly LERP the master group rotation
        masterGroup.rotation.x = THREE.MathUtils.lerp(masterGroup.rotation.x, targetRotX, 0.06);
        masterGroup.rotation.y = THREE.MathUtils.lerp(masterGroup.rotation.y, targetRotY, 0.06);

        renderer.render(scene, camera);
      };
      animate();

      // Resize handler
      const handleResize = () => {
        if (!container || !renderer) return;
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      };
      window.addEventListener("resize", handleResize);

      return () => {
        window.removeEventListener("mousemove", handleMouseMove);
        container.removeEventListener("mousedown", handleMouseDown);
        window.removeEventListener("mouseup", handleWindowMouseUp);
        window.removeEventListener("mousemove", handleWindowMouseMove);
        window.removeEventListener("resize", handleResize);

        if (animationId) cancelAnimationFrame(animationId);
        if (renderer) {
          renderer.dispose();
          if (renderer.domElement && container.contains(renderer.domElement)) {
            container.removeChild(renderer.domElement);
          }
        }
        // Dispose geometries and materials
        scene.traverse((obj) => {
          if (obj.geometry) obj.geometry.dispose();
          if (obj.material) {
            if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
            else obj.material.dispose();
          }
        });
      };
    } catch (err) {
      console.warn("Three.js scene error:", err);
      setHasError(true);
    }
  }, [isDragging]);

  if (hasError) return null;

  return (
    <div
      ref={mountRef}
      className={`absolute inset-0 z-10 ${isDragging ? "cursor-grabbing" : "cursor-grab"}`}
      style={{
        pointerEvents: "auto",
      }}
    />
  );
}

/* ═══════════════════════════════════════════════════
   CANVAS WRAPPER — Exported component
   ═══════════════════════════════════════════════════ */
export default function ThreeBackground() {
  const [webglOk, setWebglOk] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    setWebglOk(isWebGLAvailable());
  }, []);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        zIndex: 0,
      }}
      className="select-none"
    >
      {/* CSS animated background is always rendered as foundation */}
      <CSSAnimatedBackground />

      {/* Interactive Three.js WebGL scene layered on top if GPU available */}
      {webglOk && <ThreeScene isDragging={isDragging} setIsDragging={setIsDragging} />}
    </div>
  );
}
