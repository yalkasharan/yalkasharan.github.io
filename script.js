/* ══════════════════════════════════════════════
   Sharan Yalka Portfolio — script.js
══════════════════════════════════════════════ */

/* ── Theme ─────────────────────────────────────── */
const root   = document.documentElement;
const toggle = document.getElementById("themeToggle");
const tIcon  = document.getElementById("themeIcon");

function getTheme() {
  const s = localStorage.getItem("theme");
  if (s === "dark" || s === "light") return s;
  return window.matchMedia("(prefers-color-scheme:light)").matches ? "light" : "dark";
}
function setTheme(t) {
  root.setAttribute("data-theme", t);
  localStorage.setItem("theme", t);
  if (tIcon) tIcon.textContent = t === "dark" ? "☾" : "☀";
}
setTheme(getTheme());
toggle?.addEventListener("click", () =>
  setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark")
);

/* ── Footer year ───────────────────────────────── */
document.querySelectorAll("#year").forEach(el => el.textContent = new Date().getFullYear());

/* ── Copy email ────────────────────────────────── */
const copyBtn = document.getElementById("copyEmailBtn");
const toast   = document.getElementById("toast");
copyBtn?.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(copyBtn.dataset.email);
    if (toast) { toast.textContent = "✔ Copied!"; setTimeout(() => toast.textContent = "", 2500); }
  } catch {
    if (toast) { toast.textContent = "sharanyalka21@gmail.com"; setTimeout(() => toast.textContent = "", 3500); }
  }
});

/* ── Mobile nav toggle ─────────────────────────── */
const navToggle = document.getElementById("navToggle");
const topnav    = document.getElementById("topnav");
navToggle?.addEventListener("click", () => {
  const open = topnav?.classList.toggle("open");
  navToggle.setAttribute("aria-expanded", open ? "true" : "false");
});
document.addEventListener("click", e => {
  if (topnav?.classList.contains("open") && !topnav.contains(e.target) && e.target !== navToggle) {
    topnav.classList.remove("open");
    navToggle?.setAttribute("aria-expanded", "false");
  }
});
// Close mobile nav when a link is clicked (anchor navigation)
document.querySelectorAll(".topnav-link").forEach(link => {
  link.addEventListener("click", () => {
    topnav?.classList.remove("open");
    navToggle?.setAttribute("aria-expanded", "false");
  });
});

/* ── Loader ─────────────────────────────────────── */
const loader = document.getElementById("loader");
if (loader) {
  function hideLoader() { loader.classList.add("hidden"); }
  if (document.readyState === "complete") {
    setTimeout(hideLoader, 700);
  } else {
    window.addEventListener("load", () => setTimeout(hideLoader, 700));
  }
  setTimeout(hideLoader, 2800);
}

/* ── Scroll progress bar ───────────────────────── */
const progressBar = document.getElementById("scroll-progress");
function updateProgress() {
  if (!progressBar) return;
  const scrollTop  = window.scrollY;
  const docHeight  = document.documentElement.scrollHeight - window.innerHeight;
  const pct        = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  progressBar.style.width = pct + "%";
}

/* ── Scroll to top button ──────────────────────── */
const scrollTopBtn = document.getElementById("scrollTopBtn");
function updateScrollTop() {
  if (!scrollTopBtn) return;
  if (window.scrollY > 400) {
    scrollTopBtn.classList.add("visible");
  } else {
    scrollTopBtn.classList.remove("visible");
  }
}
scrollTopBtn?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

/* ── Unified scroll handler ────────────────────── */
window.addEventListener("scroll", () => {
  updateProgress();
  updateScrollTop();
}, { passive: true });
updateProgress();
updateScrollTop();

/* ── Active nav link (scroll-based) ───────────── */
const sections = document.querySelectorAll("section[id]");
const navLinks  = document.querySelectorAll(".topnav-link");

const sectionObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      navLinks.forEach(link => {
        link.classList.toggle("active", link.getAttribute("href") === "#" + id);
      });
    }
  });
}, { threshold: 0.3, rootMargin: "-60px 0px -40% 0px" });

sections.forEach(s => sectionObs.observe(s));

/* ── Scroll reveal ─────────────────────────────── */
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add("in");
      revealObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.10, rootMargin: "0px 0px -40px 0px" });

document.querySelectorAll(".reveal, .reveal-left, .reveal-right").forEach(el => revealObs.observe(el));

document.querySelectorAll(".stagger").forEach(parent => {
  Array.from(parent.children).forEach(child => {
    if (!child.classList.contains("reveal")) {
      child.classList.add("reveal");
      revealObs.observe(child);
    }
  });
});

/* ── Skill bars ────────────────────────────────── */
const skillObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const fill = entry.target.querySelector(".skill-bar-fill");
      if (fill) {
        const pct = fill.getAttribute("data-pct") || "0";
        setTimeout(() => { fill.style.width = pct + "%"; }, 150);
      }
      skillObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll(".skill-bar-wrap").forEach((el, i) => {
  // Stagger skill bar animations
  const fill = el.querySelector(".skill-bar-fill");
  if (fill) fill.style.transitionDelay = (i * 0.08) + "s";
  skillObs.observe(el);
});

/* ── Counter animation ─────────────────────────── */
function animateCounter(el) {
  const target   = parseFloat(el.dataset.count || el.textContent);
  const suffix   = el.dataset.suffix || "";
  const prefix   = el.dataset.prefix || "";
  const duration = 1600;
  const start    = performance.now();
  const isFloat  = String(target).includes(".");

  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased    = 1 - Math.pow(1 - progress, 3);
    const value    = isFloat ? (eased * target).toFixed(1) : Math.round(eased * target);
    el.textContent = prefix + value + suffix;
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

const counterObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      counterObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll(".counter").forEach(el => counterObs.observe(el));

/* ── Hero canvas (data pipeline network) ───────── */
const canvas = document.getElementById("heroCanvas");
if (canvas && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const ctx = canvas.getContext("2d");
  let W, H, nodes = [], edges = [], particles = [], animId;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    W = canvas.width  = rect.width;
    H = canvas.height = rect.height || window.innerHeight;
    buildGraph();
  }

  function buildGraph() {
    nodes = [];
    const cols = Math.max(5, Math.floor(W / 140) + 2);
    const rows = Math.max(4, Math.floor(H / 130) + 2);

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const jitter = 35;
        nodes.push({
          x: (c / (cols - 1)) * W + (Math.random() - .5) * jitter,
          y: (r / (rows - 1)) * H + (Math.random() - .5) * jitter,
          r: Math.random() * 1.8 + 1.2,
          alpha: Math.random() * .35 + .15,
        });
      }
    }

    edges = [];
    const maxDist = Math.min(W, H) * 0.3;
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < maxDist && Math.random() > .55) {
          edges.push({ a: i, b: j });
        }
      }
    }

    particles = [];
    const numParticles = Math.min(edges.length, Math.floor(W / 40));
    const chosen = [...edges].sort(() => Math.random() - .5).slice(0, numParticles);
    chosen.forEach(edge => {
      particles.push({
        edge,
        t:     Math.random(),
        speed: (Math.random() * .0025 + .0008) * (Math.random() > .5 ? 1 : -1),
        size:  Math.random() * 2.2 + 1.2,
        blue:  Math.random() > .45,
      });
    });
  }

  function draw() {
    const dark = root.getAttribute("data-theme") !== "light";
    ctx.clearRect(0, 0, W, H);

    edges.forEach(({ a, b }) => {
      const na = nodes[a], nb = nodes[b];
      ctx.beginPath();
      ctx.moveTo(na.x, na.y);
      ctx.lineTo(nb.x, nb.y);
      ctx.strokeStyle = dark ? "rgba(53,208,255,0.06)" : "rgba(0,80,200,0.05)";
      ctx.lineWidth   = 1;
      ctx.stroke();
    });

    nodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = dark
        ? `rgba(53,208,255,${n.alpha})`
        : `rgba(0,80,200,${n.alpha * .6})`;
      ctx.fill();
    });

    particles.forEach(p => {
      const { a, b } = p.edge;
      const na = nodes[a], nb = nodes[b];
      p.t += p.speed;
      if (p.t > 1) p.t = 0;
      if (p.t < 0) p.t = 1;

      const x = na.x + (nb.x - na.x) * p.t;
      const y = na.y + (nb.y - na.y) * p.t;
      const [r2, g2, b2] = p.blue ? [53, 208, 255] : [167, 139, 250];
      const al = dark ? .85 : .55;

      ctx.beginPath();
      ctx.arc(x, y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${r2},${g2},${b2},${al})`;
      ctx.fill();

      const grd = ctx.createRadialGradient(x, y, 0, x, y, p.size * 5);
      grd.addColorStop(0, `rgba(${r2},${g2},${b2},0.22)`);
      grd.addColorStop(1, "rgba(0,0,0,0)");
      ctx.beginPath();
      ctx.arc(x, y, p.size * 5, 0, Math.PI * 2);
      ctx.fillStyle = grd;
      ctx.fill();
    });

    animId = requestAnimationFrame(draw);
  }

  resize();
  draw();

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      cancelAnimationFrame(animId);
      resize();
      draw();
    }, 200);
  });
}

/* ── Terminal line-by-line fade ─────────────────── */
const termLines = document.querySelectorAll(".t-line");
if (termLines.length) {
  termLines.forEach((line, i) => {
    line.style.opacity = "0";
    line.style.transition = "opacity .35s ease";
    setTimeout(() => { line.style.opacity = "1"; }, 900 + i * 180);
  });
}

/* ── Project card 3D tilt effect ───────────────── */
if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  document.querySelectorAll(".project-card, .project-featured").forEach(card => {
    card.addEventListener("mousemove", e => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width  - 0.5;
      const y = (e.clientY - rect.top)  / rect.height - 0.5;
      card.style.transform = `perspective(700px) rotateY(${x * 7}deg) rotateX(${-y * 5}deg) translateY(-5px)`;
      card.style.boxShadow = `${-x * 12}px ${-y * 10}px 36px rgba(53,208,255,${0.06 + Math.abs(x) * 0.1})`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
      card.style.boxShadow = "";
    });
  });
}

/* ── Smooth scroll for anchor nav links ─────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", e => {
    const id = anchor.getAttribute("href").slice(1);
    const target = document.getElementById(id);
    if (target) {
      e.preventDefault();
      const offset = 68; // topbar height
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: "smooth" });
    }
  });
});

/* ── DATA-THEMED SCROLL ANIMATIONS ──────────────── */

/* Typewriter on section headings */
if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  function typewriter(el, speed = 38) {
    const full = el.textContent.trim();
    el.textContent = "";
    const cursor = document.createElement("span");
    cursor.className = "typewriter-cursor";
    el.appendChild(cursor);
    let i = 0;
    const iv = setInterval(() => {
      if (i < full.length) {
        el.insertBefore(document.createTextNode(full[i++]), cursor);
      } else {
        clearInterval(iv);
        setTimeout(() => cursor.remove(), 1400);
      }
    }, speed);
  }

  const headObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const h = entry.target.querySelector("h2");
      if (h && !h.dataset.typed) {
        h.dataset.typed = "1";
        h.classList.add("glitch-active");
        setTimeout(() => typewriter(h), 200);
      }
      headObs.unobserve(entry.target);
    });
  }, { threshold: 0.45 });

  document.querySelectorAll(".section-head").forEach(s => headObs.observe(s));
}

/* Timeline dot ripple when entering view */
const tlRippleObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const dot = entry.target.querySelector(".tl-dot");
    if (dot && !dot.dataset.pinged) {
      dot.dataset.pinged = "1";
      setTimeout(() => dot.classList.add("ripple-active"), 260);
    }
    tlRippleObs.unobserve(entry.target);
  });
}, { threshold: 0.35 });
document.querySelectorAll(".tl-item").forEach(el => tlRippleObs.observe(el));

/* Pipeline strip — each node activates sequentially */
const pipelineStrip = document.querySelector(".pipeline-strip");
if (pipelineStrip) {
  const pipeObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("pipe-active");
        pipeObs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });
  pipeObs.observe(pipelineStrip);
}

/* Floating data bits — ambient data chars drifting upward per section */
if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const DATA_CHARS = ["0","1","10","01","▸","→","∑","λ","⊕","//","{}","[]","<>","##","∂","∇"];
  const seenSections = new Set();

  function spawnBit(parent) {
    const bit = document.createElement("span");
    bit.className = "data-bit";
    bit.textContent = DATA_CHARS[Math.floor(Math.random() * DATA_CHARS.length)];
    bit.style.left  = (5 + Math.random() * 88) + "%";
    bit.style.top   = (18 + Math.random() * 68) + "%";
    const dur = 2.2 + Math.random() * 2.4;
    bit.style.animationDuration = dur + "s";
    const isDark = root.getAttribute("data-theme") !== "light";
    bit.style.color = Math.random() > .5
      ? (isDark ? "rgba(53,208,255,.32)"  : "rgba(29,78,216,.40)")
      : (isDark ? "rgba(167,139,250,.28)" : "rgba(124,58,237,.36)");
    parent.appendChild(bit);
    setTimeout(() => bit.remove(), (dur + .4) * 1000);
  }

  const bitObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting || seenSections.has(entry.target)) return;
      seenSections.add(entry.target);
      for (let i = 0; i < 8; i++) {
        setTimeout(() => spawnBit(entry.target), i * 170);
      }
    });
  }, { threshold: 0.22 });

  document.querySelectorAll("section.section").forEach(s => bitObs.observe(s));
}

/* Skill bar shine sweep after fill animation completes */
const shimmerObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const fill = entry.target.querySelector(".skill-bar-fill");
    if (fill && !fill.dataset.shimmer) {
      fill.dataset.shimmer = "1";
      setTimeout(() => fill.classList.add("shimmer"), 1500);
    }
    shimmerObs.unobserve(entry.target);
  });
}, { threshold: 0.3 });
document.querySelectorAll(".skill-bar-wrap").forEach(el => shimmerObs.observe(el));
