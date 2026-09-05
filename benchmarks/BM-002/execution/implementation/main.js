/* global THREE */
(function () {
  const canvas = document.getElementById("experience-canvas");
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0b0f);
  scene.fog = new THREE.FogExp2(0x0a0b0f, 0.045);

  const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0.6, 4.2);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  const instrumentGroup = new THREE.Group();
  scene.add(instrumentGroup);

  const points = [];
  for (let i = 0; i <= 20; i += 1) {
    const t = i / 20;
    const radius = 0.35 + Math.sin(t * Math.PI) * 0.22 + Math.sin(t * Math.PI * 3) * 0.04;
    points.push(new THREE.Vector2(radius, (t - 0.5) * 2.2));
  }
  const latheGeometry = new THREE.LatheGeometry(points, 64);
  const brassMaterial = new THREE.MeshStandardMaterial({
    color: 0xc8924e,
    metalness: 0.92,
    roughness: 0.28,
  });
  const instrument = new THREE.Mesh(latheGeometry, brassMaterial);
  instrumentGroup.add(instrument);

  const ringGeometry = new THREE.TorusGeometry(0.95, 0.025, 16, 80);
  const ringMaterial = new THREE.MeshStandardMaterial({
    color: 0x5eead4,
    metalness: 0.6,
    roughness: 0.35,
    emissive: 0x0a3330,
    emissiveIntensity: 0.35,
  });
  const halo = new THREE.Mesh(ringGeometry, ringMaterial);
  halo.rotation.x = Math.PI / 2.2;
  instrumentGroup.add(halo);

  const pedestal = new THREE.Mesh(
    new THREE.CylinderGeometry(0.55, 0.7, 0.12, 48),
    new THREE.MeshStandardMaterial({ color: 0x14161c, metalness: 0.4, roughness: 0.85 }),
  );
  pedestal.position.y = -1.15;
  instrumentGroup.add(pedestal);

  const keyLight = new THREE.DirectionalLight(0xfff0dd, 2.2);
  keyLight.position.set(3, 4, 2);
  scene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0x5eead4, 1.1);
  rimLight.position.set(-2, 1, -3);
  scene.add(rimLight);

  scene.add(new THREE.AmbientLight(0x404550, 0.45));

  const cameraKeyframes = [
    { t: 0, pos: [0.2, 0.5, 4.6], look: [0, 0, 0], state: "opening_establishing_state" },
    { t: 0.25, pos: [-1.2, 0.35, 3.4], look: [0, -0.1, 0], state: "opening_establishing_state" },
    { t: 0.5, pos: [0.8, 0.15, 2.2], look: [0, 0.05, 0], state: "product_reveal_or_focus_state" },
    { t: 0.75, pos: [-0.4, 0.55, 2.8], look: [0, 0.1, 0], state: "mid_experience_progression_state" },
    { t: 1, pos: [0, 0.75, 3.5], look: [0, 0, 0], state: "closing_or_cta_state" },
  ];

  function viewportProfile() {
    const w = window.innerWidth;
    if (w >= 1280) return "desktop";
    if (w >= 768) return "laptop";
    if (w >= 480) return "tablet";
    return "mobile";
  }

  const viewportOffsets = {
    desktop: { x: 0, y: 0, z: 0, subjectX: 0.55 },
    laptop: { x: 0, y: 0.05, z: 0.15, subjectX: 0.45 },
    tablet: { x: 0, y: 0.15, z: 0.35, subjectX: 0 },
    mobile: { x: 0, y: 0.25, z: 0.55, subjectX: 0 },
  };

  function recomposeCameraForViewport(profile) {
    const off = viewportOffsets[profile] || viewportOffsets.desktop;
    instrumentGroup.position.x = off.subjectX;
    return off;
  }

  let scrollProgress = 0;
  let targetProgress = 0;

  function computeScrollProgress() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    if (max <= 0) return 0;
    return Math.min(1, Math.max(0, window.scrollY / max));
  }

  function interpolateCamera(progress) {
    let a = cameraKeyframes[0];
    let b = cameraKeyframes[cameraKeyframes.length - 1];
    for (let i = 0; i < cameraKeyframes.length - 1; i += 1) {
      if (progress >= cameraKeyframes[i].t && progress <= cameraKeyframes[i + 1].t) {
        a = cameraKeyframes[i];
        b = cameraKeyframes[i + 1];
        break;
      }
    }
    const span = b.t - a.t || 1;
    const local = (progress - a.t) / span;
    const ease = local < 0.5 ? 2 * local * local : 1 - Math.pow(-2 * local + 2, 2) / 2;
    const profile = viewportProfile();
    const off = recomposeCameraForViewport(profile);
    camera.position.set(
      THREE.MathUtils.lerp(a.pos[0], b.pos[0], ease) + off.x,
      THREE.MathUtils.lerp(a.pos[1], b.pos[1], ease) + off.y,
      THREE.MathUtils.lerp(a.pos[2], b.pos[2], ease) + off.z,
    );
    camera.lookAt(
      THREE.MathUtils.lerp(a.look[0], b.look[0], ease),
      THREE.MathUtils.lerp(a.look[1], b.look[1], ease),
      THREE.MathUtils.lerp(a.look[2], b.look[2], ease),
    );
    instrumentGroup.rotation.y = progress * Math.PI * 0.35;
    return { activeState: ease < 0.5 ? a.state : b.state, profile };
  }

  function collectSceneLog(progress) {
    const { activeState, profile } = interpolateCamera(progress);
    return {
      progress,
      activeState,
      viewportProfile: profile,
      viewport_profiles: Object.fromEntries(
        Object.entries(viewportOffsets).map(([name, off]) => [name, { subjectX: off.subjectX, cameraZOffset: off.z }]),
      ),
      states: cameraKeyframes.map((k) => ({
        state_id: k.state,
        scroll_progress: k.t,
        camera_position: k.pos,
      })),
      camera_keyframes: cameraKeyframes,
      scroll_samples: cameraKeyframes.map((k) => ({ progress: k.t, state: k.state })),
      interaction_mapping: [
        { interaction: "scroll", maps_to: "camera_progression" },
        { interaction: "viewport_resize", maps_to: "recomposeCameraForViewport" },
      ],
    };
  }

  window.__SOLSTICE_SCENE__ = collectSceneLog(0);

  function onScroll() {
    targetProgress = computeScrollProgress();
    window.__SOLSTICE_SCENE__ = collectSceneLog(targetProgress);
  }

  window.addEventListener("scroll", onScroll, { passive: true });

  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    recomposeCameraForViewport(viewportProfile());
    window.__SOLSTICE_SCENE__ = collectSceneLog(scrollProgress);
  }

  window.addEventListener("resize", onResize);

  function animate() {
    requestAnimationFrame(animate);
    scrollProgress += prefersReducedMotion ? (targetProgress - scrollProgress) : (targetProgress - scrollProgress) * 0.08;
    if (prefersReducedMotion) scrollProgress = targetProgress;
    interpolateCamera(scrollProgress);
    renderer.render(scene, camera);
  }

  animate();

  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const open = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.querySelectorAll('.nav-links a[href^="#"]').forEach((link) => {
    link.addEventListener("click", () => links.classList.remove("is-open"));
  });

  onScroll();
})();
