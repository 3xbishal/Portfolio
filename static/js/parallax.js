/* ==========================================================================
   Parallax Portfolio Page — Scroll-based Parallax Interactions
   ========================================================================== */

(function () {
    'use strict';

    // Respect reduced motion preference
    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    document.addEventListener('DOMContentLoaded', function () {
        var page = document.querySelector('.parallax-page');
        if (!page) return;

        // Only apply JS parallax to decorative (non-interactive) elements.
        // Content reveal animations are handled by AOS via data-aos attributes.
        var bgLayers = document.querySelectorAll('.parallax-bg-layer');
        var geoShapes = document.querySelectorAll('.parallax-geo');
        var heroContent = document.querySelector('.parallax-hero-content');

        // Speed multipliers (lower = slower, appears further away)
        var speeds = {
            bgLayer1: 0.3,
            bgLayer2: 0.5,
            bgLayer3: 0.7,
            geo1: 0.4,
            geo2: 0.6,
            heroContent: 0.2
        };

        var ticking = false;

        function updateParallax() {
            var scrollY = window.pageYOffset;
            var viewportHeight = window.innerHeight;

            // Hero background layers — move at different speeds
            bgLayers.forEach(function (layer, index) {
                var speed = index === 0 ? speeds.bgLayer1 : (index === 1 ? speeds.bgLayer2 : speeds.bgLayer3);
                var yOffset = scrollY * speed;
                layer.style.transform = 'translate3d(0, ' + yOffset + 'px, 0)';
            });

            // Geometric shapes — move + rotate
            geoShapes.forEach(function (shape, index) {
                var speed = index === 0 ? speeds.geo1 : speeds.geo2;
                var yOffset = scrollY * speed;
                var rotation = scrollY * 0.05;
                shape.style.transform = 'translate3d(0, ' + yOffset + 'px, 0) rotate(' + rotation + 'deg)';
            });

            // Hero content fades and moves up as you scroll past the hero
            if (heroContent) {
                var heroOffset = scrollY * speeds.heroContent;
                var heroOpacity = Math.max(0, 1 - (scrollY / (viewportHeight * 0.6)));
                heroContent.style.transform = 'translate3d(0, ' + heroOffset + 'px, 0)';
                heroContent.style.opacity = heroOpacity;
            }

            ticking = false;
        }

        function onScroll() {
            if (!ticking && !prefersReducedMotion) {
                window.requestAnimationFrame(updateParallax);
                ticking = true;
            }
        }

        // Initial position
        updateParallax();

        // Scroll listener (passive for performance)
        window.addEventListener('scroll', onScroll, { passive: true });

        // Recalculate on resize
        window.addEventListener('resize', function () {
            updateParallax();
        }, { passive: true });
    });
})();