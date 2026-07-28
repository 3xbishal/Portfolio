/* =============================================================================
   Animated Background — Floating Particles with Neural Connections
   ==============================================================================
   A lightweight, performant canvas-based particle system that creates a
   subtle "magic particles" / "neural network" ambient effect. Particles drift
   slowly across the viewport and form thin connections when they come near
   each other, evoking a living neural web.

   Features:
   - Canvas-based for high performance (single draw call per frame)
   - Responsive particle count based on viewport size
   - Mouse proximity interaction (particles flee from cursor)
   - Respects `prefers-reduced-motion` media query
   - Black particles on white background (white in dark mode)
   - Accessible toggle to disable/enable
   ============================================================================== */

(function () {
    'use strict';

    // ---- Configuration -------------------------------------------------------
    var CONFIG = {
        particleCount: 40,        // base number of particles
        maxParticleCount: 70,     // cap on very large screens
        minParticleCount: 20,     // floor on small screens
        particleSize: 1.8,        // base radius in px
        particleSizeVariance: 0.8, // random size variation
        speed: 0.25,              // drift speed multiplier
        connectDistance: 100,     // max distance for connection lines
        lineWidth: 0.5,           // connection line thickness
        opacity: 0.2,             // connection line opacity
        pulseIntensity: 0.1,      // subtle size pulse
        mouseRadius: 80,          // cursor influence radius
        mouseRepel: 0.5,          // cursor repulsion strength
        particleColor: '#000000', // black particles on white background
    };

    // ---- State ---------------------------------------------------------------
    var canvas, ctx;
    var particles = [];
    var mouse = { x: null, y: null, active: false };
    var width, height, dpr;
    var rafId = null;
    var isRunning = false;
    var resolvedColor = CONFIG.particleColor;

    // ---- Utilities -----------------------------------------------------------

    /**
     * Check if the user has requested reduced motion.
     */
    function prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    /**
     * Determine the appropriate particle count for the current viewport.
     */
    function getParticleCount() {
        var vw = window.innerWidth;
        if (vw < 576) return CONFIG.minParticleCount;
        if (vw > 1400) return CONFIG.maxParticleCount;
        var ratio = (vw - 576) / (1400 - 576);
        return Math.round(CONFIG.minParticleCount + ratio * (CONFIG.maxParticleCount - CONFIG.minParticleCount));
    }

    // ---- Particle ------------------------------------------------------------

    function Particle() {
        this.init();
    }

    Particle.prototype.init = function () {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        var angle = Math.random() * Math.PI * 2;
        var speed = CONFIG.speed * (0.5 + Math.random());
        this.vx = Math.cos(angle) * speed;
        this.vy = Math.sin(angle) * speed;
        this.size = CONFIG.particleSize + (Math.random() - 0.5) * CONFIG.particleSizeVariance;
        this.pulsePhase = Math.random() * Math.PI * 2;
        this.opacity = 0.4 + Math.random() * 0.3;
    };

    Particle.prototype.update = function () {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < -10) this.x = width + 10;
        if (this.x > width + 10) this.x = -10;
        if (this.y < -10) this.y = height + 10;
        if (this.y > height + 10) this.y = -10;

        if (mouse.active && mouse.x !== null && mouse.y !== null) {
            var dx = this.x - mouse.x;
            var dy = this.y - mouse.y;
            var dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < CONFIG.mouseRadius) {
                var force = (CONFIG.mouseRadius - dist) / CONFIG.mouseRadius;
                var repel = CONFIG.mouseRepel * force;
                this.x += (dx / dist) * repel;
                this.y += (dy / dist) * repel;
            }
        }
    };

    Particle.prototype.draw = function (ctx) {
        var pulse = 1 + Math.sin(this.pulsePhase + Date.now() * 0.002) * CONFIG.pulseIntensity;
        var size = this.size * pulse;

        ctx.beginPath();
        ctx.arc(this.x, this.y, size, 0, Math.PI * 2);
        ctx.fillStyle = resolvedColor;
        ctx.globalAlpha = this.opacity;
        ctx.fill();
        ctx.globalAlpha = 1;
    };

    // ---- Initialization ------------------------------------------------------

    function initCanvas() {
        canvas = document.createElement('canvas');
        canvas.className = 'animated-particles-canvas';
        canvas.setAttribute('aria-hidden', 'true');
        canvas.setAttribute('role', 'presentation');

        var container = document.querySelector('.animated-bg');
        if (container) {
            container.appendChild(canvas);
        } else {
            document.body.appendChild(canvas);
        }

        ctx = canvas.getContext('2d');
    }

    function resize() {
        if (!canvas) return;
        dpr = window.devicePixelRatio || 1;
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        if (ctx) {
            ctx.scale(dpr, dpr);
        }
    }

    function createParticles() {
        particles = [];
        var count = getParticleCount();
        for (var i = 0; i < count; i++) {
            particles.push(new Particle());
        }
    }

    function updateParticles() {
        for (var i = 0; i < particles.length; i++) {
            particles[i].update();
        }
    }

    function drawConnections() {
        if (!ctx) return;
        ctx.globalAlpha = CONFIG.opacity;
        ctx.lineWidth = CONFIG.lineWidth;
        ctx.strokeStyle = resolvedColor;
        ctx.lineCap = 'round';

        for (var i = 0; i < particles.length; i++) {
            for (var j = i + 1; j < particles.length; j++) {
                var p1 = particles[i];
                var p2 = particles[j];
                var dx = p1.x - p2.x;
                var dy = p1.y - p2.y;
                var dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.connectDistance) {
                    var alpha = 1 - (dist / CONFIG.connectDistance);
                    ctx.globalAlpha = CONFIG.opacity * alpha;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
        ctx.globalAlpha = 1;
    }

    function drawParticles() {
        if (!ctx) return;
        for (var i = 0; i < particles.length; i++) {
            particles[i].draw(ctx);
        }
    }

    function clearCanvas() {
        if (!ctx) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    function loop() {
        if (!isRunning) return;
        clearCanvas();
        updateParticles();
        drawConnections();
        drawParticles();
        rafId = requestAnimationFrame(loop);
    }

    function start() {
        if (isRunning) return;
        isRunning = true;
        loop();
    }

    function stop() {
        isRunning = false;
        if (rafId) {
            cancelAnimationFrame(rafId);
            rafId = null;
        }
    }

    /**
     * Clear all particles from the canvas (completely remove them).
     */
    function clearParticles() {
        stop();
        particles = [];
        clearCanvas();
    }

    /**
     * Restore particles after they've been cleared.
     */
    function restoreParticles() {
        if (particles.length > 0) return; // already have particles
        createParticles();
        start();
    }

    // ---- Mouse Events --------------------------------------------------------

    function onMouseMove(e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        mouse.active = true;
    }

    function onMouseLeave() {
        mouse.active = false;
        mouse.x = null;
        mouse.y = null;
    }

    // ---- Theme / Color -------------------------------------------------------

    /**
     * Update the particle color (e.g. for dark mode).
     * @param {string} color - CSS color string
     */
    function setColor(color) {
        resolvedColor = color;
    }

    /**
     * Check if dark mode is currently active.
     */
    function isDarkMode() {
        return document.body.classList.contains('dark-mode');
    }

    /**
     * Update particle color based on current theme.
     */
    function updateThemeColor() {
        if (isDarkMode()) {
            resolvedColor = '#ffffff';
        } else {
            resolvedColor = CONFIG.particleColor;
        }
    }

    // ---- Public API ----------------------------------------------------------

    /**
     * Initialize the animated background.
     */
    function init() {
        var container = document.querySelector('.animated-bg');
        if (!container) return;

        if (prefersReducedMotion()) {
            container.classList.add('reduced-motion');
            return;
        }

        resolvedColor = CONFIG.particleColor;

        initCanvas();
        resize();
        createParticles();

        window.addEventListener('resize', onResize);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseleave', onMouseLeave);

        start();
    }

    function onResize() {
        resize();
        var expected = getParticleCount();
        if (Math.abs(particles.length - expected) > 15) {
            createParticles();
        }
    }

    // ---- Module Export -------------------------------------------------------

    window.AnimatedBackground = {
        init: init,
        start: start,
        stop: stop,
        clearParticles: clearParticles,
        restoreParticles: restoreParticles,
        setColor: setColor,
        isDarkMode: isDarkMode,
        updateThemeColor: updateThemeColor,
        isRunning: function () { return isRunning; },
        destroy: function () {
            stop();
            window.removeEventListener('resize', onResize);
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseleave', onMouseLeave);
            if (canvas && canvas.parentNode) {
                canvas.parentNode.removeChild(canvas);
            }
        }
    };

    // ---- Auto-init on DOM ready ----------------------------------------------

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
