/* =========================================================
   Belis — Dairesel Proje Galerisi (CircularGallery portu)
   React Bits "CircularGallery" bileşeninin bağımsız (vanilla)
   sürümü. ogl kütüphanesi CDN üzerinden ES modülü olarak gelir.
   Başarıyla açılırsa eski kart kaydırıcısını gizler; açılamazsa
   (eski tarayıcı, WebGL yok, file:// önizleme) eski kaydırıcı
   aynen çalışmaya devam eder.
   ========================================================= */
import { Camera, Mesh, Plane, Program, Renderer, Texture, Transform } from 'https://cdn.jsdelivr.net/npm/ogl@1.0.11/+esm';

function lerp(a, b, t) { return a + (b - a) * t; }
function debounce(fn, wait) {
  let t; return function (...args) { clearTimeout(t); t = setTimeout(() => fn.apply(this, args), wait); };
}

function getFontSize(font) {
  const m = font.match(/(\d+)px/); return m ? parseInt(m[1], 10) : 30;
}

function createTextTexture(gl, text, font, color) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.font = font;
  const w = Math.ceil(ctx.measureText(text).width);
  const h = Math.ceil(getFontSize(font) * 1.2);
  canvas.width = w + 24; canvas.height = h + 24;
  ctx.font = font;
  ctx.fillStyle = color;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillText(text, canvas.width / 2, canvas.height / 2);
  const texture = new Texture(gl, { generateMipmaps: false });
  texture.image = canvas;
  return { texture, width: canvas.width, height: canvas.height };
}

class Title {
  constructor({ gl, plane, text, textColor, font }) {
    this.gl = gl; this.plane = plane;
    const { texture, width, height } = createTextTexture(gl, text, font, textColor);
    const geometry = new Plane(gl);
    const program = new Program(gl, {
      vertex: `
        attribute vec3 position; attribute vec2 uv;
        uniform mat4 modelViewMatrix; uniform mat4 projectionMatrix;
        varying vec2 vUv;
        void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
      fragment: `
        precision highp float;
        uniform sampler2D tMap; varying vec2 vUv;
        void main(){ vec4 c = texture2D(tMap, vUv); if (c.a < 0.1) discard; gl_FragColor = c; }`,
      uniforms: { tMap: { value: texture } },
      transparent: true
    });
    this.mesh = new Mesh(gl, { geometry, program });
    const aspect = width / height;
    const textHeight = plane.scale.y * 0.15;
    this.mesh.scale.set(textHeight * aspect, textHeight, 1);
    this.mesh.position.y = -plane.scale.y * 0.5 - textHeight * 0.5 - 0.05;
    this.mesh.setParent(plane);
  }
}

class Media {
  constructor(opts) {
    Object.assign(this, opts); // geometry, gl, image, index, length, scene, screen, text, viewport, bend, textColor, borderRadius, font, href
    this.extra = 0;
    this.createShader();
    this.createMesh();
    this.title = new Title({ gl: this.gl, plane: this.plane, text: this.text, textColor: this.textColor, font: this.font });
    this.onResize();
  }
  createShader() {
    const texture = new Texture(this.gl, { generateMipmaps: true });
    this.program = new Program(this.gl, {
      depthTest: false, depthWrite: false,
      vertex: `
        precision highp float;
        attribute vec3 position; attribute vec2 uv;
        uniform mat4 modelViewMatrix; uniform mat4 projectionMatrix;
        uniform float uTime; uniform float uSpeed;
        varying vec2 vUv;
        void main(){
          vUv = uv;
          vec3 p = position;
          p.z = (sin(p.x * 4.0 + uTime) * 1.5 + cos(p.y * 2.0 + uTime) * 1.5) * (0.1 + uSpeed * 0.5);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
        }`,
      fragment: `
        precision highp float;
        uniform vec2 uImageSizes; uniform vec2 uPlaneSizes;
        uniform sampler2D tMap; uniform float uBorderRadius;
        varying vec2 vUv;
        float roundedBoxSDF(vec2 p, vec2 b, float r){
          vec2 d = abs(p) - b;
          return length(max(d, vec2(0.0))) + min(max(d.x, d.y), 0.0) - r;
        }
        void main(){
          vec2 ratio = vec2(
            min((uPlaneSizes.x / uPlaneSizes.y) / (uImageSizes.x / uImageSizes.y), 1.0),
            min((uPlaneSizes.y / uPlaneSizes.x) / (uImageSizes.y / uImageSizes.x), 1.0)
          );
          vec2 uv = vec2(
            vUv.x * ratio.x + (1.0 - ratio.x) * 0.5,
            vUv.y * ratio.y + (1.0 - ratio.y) * 0.5
          );
          vec4 color = texture2D(tMap, uv);
          float d = roundedBoxSDF(vUv - 0.5, vec2(0.5 - uBorderRadius), uBorderRadius);
          float alpha = 1.0 - smoothstep(-0.002, 0.002, d);
          gl_FragColor = vec4(color.rgb, alpha);
        }`,
      uniforms: {
        tMap: { value: texture },
        uPlaneSizes: { value: [0, 0] },
        uImageSizes: { value: [0, 0] },
        uSpeed: { value: 0 },
        uTime: { value: 100 * Math.random() },
        uBorderRadius: { value: this.borderRadius }
      },
      transparent: true
    });
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = this.image;
    img.onload = () => {
      texture.image = img;
      this.program.uniforms.uImageSizes.value = [img.naturalWidth, img.naturalHeight];
    };
  }
  createMesh() {
    this.plane = new Mesh(this.gl, { geometry: this.geometry, program: this.program });
    this.plane.setParent(this.scene);
  }
  update(scroll, direction) {
    this.plane.position.x = this.x - scroll.current - this.extra;
    const x = this.plane.position.x;
    const H = this.viewport.width / 2;
    if (this.bend === 0) {
      this.plane.position.y = 0; this.plane.rotation.z = 0;
    } else {
      const B = Math.abs(this.bend);
      const R = (H * H + B * B) / (2 * B);
      const ex = Math.min(Math.abs(x), H);
      const arc = R - Math.sqrt(R * R - ex * ex);
      if (this.bend > 0) {
        this.plane.position.y = -arc;
        this.plane.rotation.z = -Math.sign(x) * Math.asin(ex / R);
      } else {
        this.plane.position.y = arc;
        this.plane.rotation.z = Math.sign(x) * Math.asin(ex / R);
      }
    }
    this.speed = scroll.current - scroll.last;
    this.program.uniforms.uTime.value += 0.04;
    this.program.uniforms.uSpeed.value = this.speed;
    const planeOffset = this.plane.scale.x / 2;
    const viewportOffset = this.viewport.width / 2;
    this.isBefore = this.plane.position.x + planeOffset < -viewportOffset;
    this.isAfter = this.plane.position.x - planeOffset > viewportOffset;
    if (direction === 'right' && this.isBefore) { this.extra -= this.widthTotal; this.isBefore = this.isAfter = false; }
    if (direction === 'left' && this.isAfter) { this.extra += this.widthTotal; this.isBefore = this.isAfter = false; }
  }
  onResize({ screen, viewport } = {}) {
    if (screen) this.screen = screen;
    if (viewport) this.viewport = viewport;
    this.scale = this.screen.height / 1500;
    this.plane.scale.y = (this.viewport.height * (900 * this.scale)) / this.screen.height;
    this.plane.scale.x = (this.viewport.width * (700 * this.scale)) / this.screen.width;
    this.program.uniforms.uPlaneSizes.value = [this.plane.scale.x, this.plane.scale.y];
    this.padding = 2;
    this.width = this.plane.scale.x + this.padding;
    this.widthTotal = this.width * this.length;
    this.x = this.width * this.index;
  }
}

class CircularGalleryApp {
  constructor(container, { items, bend = 2.2, textColor = '#003B6F', borderRadius = 0.05, font = 'bold 28px Inter', scrollSpeed = 2, scrollEase = 0.06 } = {}) {
    this.container = container;
    this.scrollSpeed = scrollSpeed;
    this.scroll = { ease: scrollEase, current: 0, target: 0, last: 0, position: 0 };
    this.lastInteract = Date.now();
    this.onCheckDebounce = debounce(() => this.onCheck(), 200);
    this.createRenderer();
    this.createCamera();
    this.scene = new Transform();
    this.onResize();
    this.planeGeometry = new Plane(this.gl, { heightSegments: 50, widthSegments: 100 });
    this.createMedias(items, bend, textColor, borderRadius, font);
    this.update = this.update.bind(this);
    this.update();
    this.addEventListeners();
  }
  createRenderer() {
    // Mobilde WebGL render etme
    if (window.matchMedia('(max-width: 767px)').matches) {
      this.gl = null;
      this.renderer = null;
      return;
    }
    this.renderer = new Renderer({ alpha: true, antialias: true, dpr: Math.min(window.devicePixelRatio || 1, 2) });
    this.gl = this.renderer.gl;
    this.gl.clearColor(0, 0, 0, 0);
    this.container.appendChild(this.gl.canvas);
  }
  createCamera() {
    this.camera = new Camera(this.gl);
    this.camera.fov = 45;
    this.camera.position.z = 20;
  }
  createMedias(items, bend, textColor, borderRadius, font) {
    this.mediasImages = items.concat(items); // sonsuz döngü hissi için iki tur
    this.medias = this.mediasImages.map((data, index) => new Media({
      geometry: this.planeGeometry, gl: this.gl, image: data.image, index,
      length: this.mediasImages.length, scene: this.scene, screen: this.screen,
      text: data.text, viewport: this.viewport, bend, textColor, borderRadius, font, href: data.href
    }));
  }
  /* --- Etkileşim (yalnızca kapsayıcıya bağlı; sayfa kaydırmasını bozmaz) --- */
  onDown(e) {
    this.isDown = true;
    this.moved = 0;
    this.scroll.position = this.scroll.current;
    this.start = e.touches ? e.touches[0].clientX : e.clientX;
    this.lastInteract = Date.now();
  }
  onMove(e) {
    if (!this.isDown) return;
    const x = e.touches ? e.touches[0].clientX : e.clientX;
    const distance = (this.start - x) * (this.scrollSpeed * 0.025);
    this.moved = Math.max(this.moved, Math.abs(this.start - x));
    this.scroll.target = this.scroll.position + distance;
    this.lastInteract = Date.now();
  }
  onUp() {
    if (!this.isDown) return;
    this.isDown = false;
    this.lastInteract = Date.now();
    // Sürükleme yoksa (dokunma/tıklama) projeler sayfasına git
    if (this.moved < 8) { window.location.href = 'projeler.html'; return; }
    this.onCheck();
  }
  onWheel(e) {
    // Yalnızca yatay tekerlek/kaydırma hareketine tepki ver — dikey sayfa kaydırması aynen çalışsın
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
      e.preventDefault();
      this.scroll.target += (e.deltaX > 0 ? this.scrollSpeed : -this.scrollSpeed) * 0.2;
      this.lastInteract = Date.now();
      this.onCheckDebounce();
    }
  }
  onKeyDown(e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); this.nudge(1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); this.nudge(-1); }
  }
  nudge(dir) {
    const w = this.medias && this.medias[0] ? this.medias[0].width : 4;
    this.scroll.target += dir * w;
    this.lastInteract = Date.now();
    this.onCheckDebounce();
  }
  onCheck() {
    if (!this.medias || !this.medias[0]) return;
    const width = this.medias[0].width;
    const itemIndex = Math.round(Math.abs(this.scroll.target) / width);
    const item = width * itemIndex;
    this.scroll.target = this.scroll.target < 0 ? -item : item;
  }
  onResize() {
    this.screen = { width: this.container.clientWidth, height: this.container.clientHeight };
    this.renderer.setSize(this.screen.width, this.screen.height);
    this.camera.perspective({ aspect: this.screen.width / this.screen.height });
    const fov = (this.camera.fov * Math.PI) / 180;
    const height = 2 * Math.tan(fov / 2) * this.camera.position.z;
    this.viewport = { width: height * this.camera.aspect, height };
    if (this.medias) this.medias.forEach(m => m.onResize({ screen: this.screen, viewport: this.viewport }));
  }
  update() {
    // Mobilde çalışma
    if (!this.renderer || !this.gl) return;
    // Boştayken yavaşça kendi kendine dönsün (hareket azaltma tercihi hariç)
    if (!this.isDown && !this.reduceMotion && Date.now() - this.lastInteract > 3000) {
      this.scroll.target += 0.006;
    }
    this.scroll.current = lerp(this.scroll.current, this.scroll.target, this.scroll.ease);
    const direction = this.scroll.current > this.scroll.last ? 'right' : 'left';
    if (this.medias) this.medias.forEach(m => m.update(this.scroll, direction));
    this.renderer.render({ scene: this.scene, camera: this.camera });
    this.scroll.last = this.scroll.current;
    this.raf = window.requestAnimationFrame(this.update);
  }
  addEventListeners() {
    const c = this.container;
    this.reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.boundResize = debounce(() => this.onResize(), 150);
    window.addEventListener('resize', this.boundResize);
    c.addEventListener('mousedown', e => this.onDown(e));
    window.addEventListener('mousemove', e => this.onMove(e));
    window.addEventListener('mouseup', () => this.onUp());
    c.addEventListener('touchstart', e => this.onDown(e), { passive: true });
    c.addEventListener('touchmove', e => this.onMove(e), { passive: true });
    c.addEventListener('touchend', () => this.onUp());
    c.addEventListener('wheel', e => this.onWheel(e), { passive: false });
    c.addEventListener('keydown', e => this.onKeyDown(e));
  }
}

/* ================= Başlatma ================= */
const PROJECT_ITEMS = [
  { image: 'assets/proje_finans_merkezi.jpg', text: 'Finans Merkezi' },
  { image: 'assets/proje_altinbas_kampus.jpg', text: 'Altınbaş Üniversitesi' },
  { image: 'assets/proje_trendyol_spine.jpg', text: 'Trendyol Spine Tower' },
  { image: 'assets/proje_datacasa_dh2.jpg', text: 'Datacasa Veri Merkezi' },
  { image: 'assets/proje_peker_tower.jpg', text: 'Peker Tower' },
  { image: 'assets/proje_mvk_golf.jpg', text: 'MVK Golf Kulübü' }
];

function initGallery() {
  const el = document.getElementById('circular-gallery');
  const fallback = document.getElementById('project-carousel');
  if (!el) return;

  // Mobilde WebGL galerisi yerine fallback carousel'ı kullan
  const isMobile = window.matchMedia('(max-width: 767px)').matches;
  if (isMobile) {
    if (fallback) fallback.classList.remove('hidden', 'carousel-hidden');
    return;
  }

  try {
    // Inter fontu hazır olduktan sonra başlat (etiketler doğru fontla çizilsin)
    const ready = (document.fonts && document.fonts.load)
      ? Promise.race([document.fonts.load('bold 28px Inter'), new Promise(r => setTimeout(r, 1500))])
      : Promise.resolve();
    ready.then(() => {
      const app = new CircularGalleryApp(el, {
        items: PROJECT_ITEMS,
        bend: 2.2,
        textColor: '#003B6F',
        borderRadius: 0.05,
        font: 'bold 28px Inter',
        scrollSpeed: 2,
        scrollEase: 0.06
      });
      // Başarılı: galeriyi göster, eski kaydırıcıyı gizle
      el.classList.add('loaded');
      if (fallback) fallback.classList.add('carousel-hidden');
      requestAnimationFrame(() => app.onResize());
      // Mevcut ok butonlarını galeriye bağla
      const prev = document.getElementById('slider-prev-btn');
      const next = document.getElementById('slider-next-btn');
      if (prev) prev.addEventListener('click', () => app.nudge(-1));
      if (next) next.addEventListener('click', () => app.nudge(1));
    });
  } catch (err) {
    // WebGL yoksa eski kaydırıcı görünür kalır
    if (fallback) fallback.classList.remove('carousel-hidden');
    console.warn('CircularGallery başlatılamadı, kart kaydırıcısı kullanılacak.', err);
  }
}

// Mobilde hiç yükleme
const isMobile = window.matchMedia('(max-width: 767px)').matches;
if (isMobile) {
  // Mobilde: Fallback carousel göster, WebGL gizle
  const carousel = document.getElementById('project-carousel');
  const gallery = document.getElementById('circular-gallery');
  if (carousel) carousel.style.display = 'block';
  if (gallery) gallery.style.display = 'none';
} else {
  // Desktop: WebGL galerisi yükle, fallback carousel gizle
  const carousel = document.getElementById('project-carousel');
  if (carousel) carousel.style.display = 'none';
  const target = document.getElementById('projelerimiz-slider');
  if ('IntersectionObserver' in window && target) {
    const io = new IntersectionObserver((entries, obs) => {
      if (entries.some(e => e.isIntersecting)) { obs.disconnect(); initGallery(); }
    }, { rootMargin: '300px' });
    io.observe(target);
  } else {
    initGallery();
  }
}
