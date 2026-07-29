/* ==========================================================================
   Parallax Portfolio Page — Advanced Scroll-Driven Interactive Engine
   Scenes: Hero (3D mouse+scroll) → Build (stack) → Open (doors) →
           Visit (horizontal) → Skills (orbit) → Journey (timeline) →
           Services/Testimonials (reveal) + Scroll progress + Scene nav
   ========================================================================== */

(function () {
    'use strict';

    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    document.addEventListener('DOMContentLoaded', function () {
        var page = document.querySelector('.parallax-page');
        if (!page) return;

        // ------------------------------------------------------------------
        // Element references
        // ------------------------------------------------------------------
        var progressFill = document.getElementById('scrollProgressFill');
        var sceneNavDots = document.querySelectorAll('.scene-nav-dot');
        var scenes = {
            hero: document.getElementById('scene-hero'),
            build: document.getElementById('scene-build'),
            open: document.getElementById('scene-open'),
            visit: document.getElementById('scene-visit'),
            skills: document.getElementById('scene-skills'),
            journey: document.getElementById('scene-journey')
        };

        // Hero 3D
        var heroStage = document.getElementById('hero3dStage');
        var heroLayers = document.querySelectorAll('.hero-layer');
        var heroContent = document.getElementById('heroContent');
        var heroScrollCue = document.getElementById('heroScrollCue');

        // Build
        var buildBlocks = document.querySelectorAll('.build-block');
        var buildProgressLabel = document.getElementById('buildProgressLabel');

        // Open
        var doorLeft = document.getElementById('doorLeft');
        var doorRight = document.getElementById('doorRight');
        var openRevealContent = document.querySelector('.open-reveal-content');

        // Visit
        var visitTrack = document.getElementById('visitTrack');
        var visitProgressFill = document.getElementById('visitProgressFill');

        // Skills orbit
        var skillsStage = document.getElementById('skillsOrbitStage');
        var skillsCore = document.getElementById('skillsOrbitCore');
        var orbitRing1 = document.getElementById('orbitRing1');
        var orbitRing2 = document.getElementById('orbitRing2');
        var skillItems = document.querySelectorAll('.skill-orbit-item');

        // Journey
        var journeyTimeline = document.getElementById('journeyTimeline');
        var journeyItems = document.querySelectorAll('[data-journey-item]');
        var journeyFillInner = null;

        // Reveal cards
        var serviceCards = document.querySelectorAll('[data-service-card]');
        var testimonialCards = document.querySelectorAll('[data-testimonial-card]');

        // ------------------------------------------------------------------
        // Helpers
        // ------------------------------------------------------------------
        function clamp(v, min, max) {
            return Math.min(Math.max(v, min), max);
        }

        function lerp(a, b, t) {
            return a + (b - a) * t;
        }

        function mapRange(value, inMin, inMax, outMin, outMax) {
            if (inMax === inMin) return outMin;
            return outMin + ((value - inMin) * (outMax - outMin)) / (inMax - inMin);
        }

        // Progress of scroll within a section (0 = section top at viewport top,
        // 1 = section bottom at viewport bottom)
        function sectionProgress(section) {
            if (!section) return 0;
            var rect = section.getBoundingClientRect();
            var scrollable = section.offsetHeight - window.innerHeight;
            if (scrollable <= 0) return 0;
            return clamp(-rect.top / scrollable, 0, 1);
        }

        // ------------------------------------------------------------------
        // Position skill orbit items in two concentric rings
        // ------------------------------------------------------------------
        function positionSkillItems() {
            if (!skillItems.length || !skillsStage) return;
            var stageRect = skillsStage.getBoundingClientRect();
            var centerX = stageRect.width / 2;
            var centerY = stageRect.height / 2;
            var total = skillItems.length;

            var minDim = Math.min(stageRect.width, stageRect.height);
            var radius1 = minDim * 0.28;
            var radius2 = minDim * 0.45;

            if (orbitRing1) {
                orbitRing1.style.width = (radius1 * 2) + 'px';
                orbitRing1.style.height = (radius1 * 2) + 'px';
            }
            if (orbitRing2) {
                orbitRing2.style.width = (radius2 * 2) + 'px';
                orbitRing2.style.height = (radius2 * 2) + 'px';
            }

            var half = Math.ceil(total / 2);

            skillItems.forEach(function (item, i) {
                var ring = i < half ? 1 : 2;
                var ringIndex = ring === 1 ? i : i - half;
                var ringCount = ring === 1 ? half : total - half;
                var radius = ring === 1 ? radius1 : radius2;
                var angle = (ringIndex / ringCount) * Math.PI * 2 - Math.PI / 2;

                var x = centerX + Math.cos(angle) * radius;
                var y = centerY + Math.sin(angle) * radius;

                item.style.left = x + 'px';
                item.style.top = y + 'px';
            });
        }

        // ------------------------------------------------------------------
        // Determine which scene is currently active for nav dots
        // ------------------------------------------------------------------
        function updateActiveScene() {
            var viewportCenter = window.innerHeight / 2;
            var currentScene = 'hero';

            Object.keys(scenes).forEach(function (key) {
                var section = scenes[key];
                if (!section) return;
                var rect = section.getBoundingClientRect();
                if (rect.top <= viewportCenter && rect.bottom >= viewportCenter) {
                    currentScene = key;
                }
            });

            sceneNavDots.forEach(function (dot) {
                if (dot.dataset.scene === currentScene) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        }

        // ------------------------------------------------------------------
        // Main scroll update (rAF throttled)
        // ------------------------------------------------------------------
        var ticking = false;
        var mouseX = 0, mouseY = 0;
        var targetMouseX = 0, targetMouseY = 0;

        function updateScroll() {
            var scrollY = window.pageYOffset;
            var viewportH = window.innerHeight;
            var docHeight = document.documentElement.scrollHeight - viewportH;

            // --- Scroll progress bar ---
            if (progressFill) {
                var docProgress = docHeight > 0 ? clamp(scrollY / docHeight, 0, 1) : 0;
                progressFill.style.width = (docProgress * 100) + '%';
            }

            // --- Scene nav active dot ---
            updateActiveScene();

            // --- Hero 3D parallax (scroll + mouse) ---
            if (heroStage && !prefersReducedMotion) {
                var heroProgress = sectionProgress(scenes.hero);
                mouseX = lerp(mouseX, targetMouseX, 0.08);
                mouseY = lerp(mouseY, targetMouseY, 0.08);

                heroLayers.forEach(function (layer) {
                    var depth = parseFloat(layer.dataset.depth) || 0.05;
                    var scrollOffset = heroProgress * 100 * depth * 10;
                    var mouseOffsetX = mouseX * 40 * depth * 10;
                    var mouseOffsetY = mouseY * 40 * depth * 10;
                    layer.style.transform =
                        'translate3d(' + (mouseOffsetX - scrollOffset * 0.3) + 'px, ' +
                        (mouseOffsetY + scrollOffset) + 'px, 0)';
                });

                if (heroContent) {
                    var heroFade = clamp(1 - heroProgress * 1.8, 0, 1);
                    var heroY = heroProgress * -80;
                    heroContent.style.opacity = heroFade;
                    heroContent.style.transform = 'translate3d(0, ' + heroY + 'px, 0)';
                }
                if (heroScrollCue) {
                    heroScrollCue.style.opacity = clamp(1 - heroProgress * 3, 0, 1);
                }
            }

            // --- Build scene: blocks rise & stack ---
            if (scenes.build && buildBlocks.length && !prefersReducedMotion) {
                var buildProg = sectionProgress(scenes.build);
                var buildActive = clamp(buildProg / 0.8, 0, 1);

                buildBlocks.forEach(function (block) {
                    var riseAt = parseFloat(block.dataset.rise) || 0;
                    var blockProg = clamp(mapRange(buildActive, riseAt, riseAt + 0.2, 0, 1), 0, 1);
                    var yOffset = (1 - blockProg) * 120;
                    var rotation = (1 - blockProg) * -8;
                    block.style.transform = 'translateY(' + yOffset + 'vh) rotate(' + rotation + 'deg)';
                    block.style.opacity = blockProg;
                });

                if (buildProgressLabel) {
                    buildProgressLabel.textContent = Math.round(buildActive * 100) + '%';
                }
            }

            // --- Open scene: doors split ---
            if (scenes.open && doorLeft && doorRight && !prefersReducedMotion) {
                var openProg = sectionProgress(scenes.open);
                var doorProg = clamp(openProg / 0.6, 0, 1);
                // Ease-in-out for smoother door movement
                var easedDoor = doorProg < 0.5
                    ? 2 * doorProg * doorProg
                    : 1 - Math.pow(-2 * doorProg + 2, 2) / 2;

                doorLeft.style.transform = 'translateX(' + (-easedDoor * 100) + '%)';
                doorRight.style.transform = 'translateX(' + (easedDoor * 100) + '%)';

                if (openRevealContent) {
                    var revealProg = clamp(mapRange(openProg, 0.3, 0.8, 0, 1), 0, 1);
                    openRevealContent.style.opacity = revealProg;
                    openRevealContent.style.transform = 'scale(' + lerp(0.9, 1, revealProg) + ')';
                }
            }

            // --- Visit scene: horizontal scroll ---
            if (scenes.visit && visitTrack && !prefersReducedMotion) {
                var visitProg = sectionProgress(scenes.visit);
                var trackWidth = visitTrack.scrollWidth;
                var viewportWidth = window.innerWidth;
                var maxTranslate = trackWidth - viewportWidth + (viewportWidth * 0.1);
                if (maxTranslate < 0) maxTranslate = 0;
                var translateX = -visitProg * maxTranslate;
                visitTrack.style.transform = 'translate3d(' + translateX + 'px, 0, 0)';

                if (visitProgressFill) {
                    visitProgressFill.style.width = (visitProg * 100) + '%';
                }
            }

            // --- Skills orbit: assemble on scroll into view ---
            if (skillsStage && !prefersReducedMotion) {
                var skillsRect = skillsStage.getBoundingClientRect();
                var skillsCenterY = skillsRect.top + skillsRect.height / 2;
                var viewportCenter = viewportH / 2;
                var distFromCenter = Math.abs(skillsCenterY - viewportCenter);
                var maxDist = viewportH * 0.8;
                var skillsProg = clamp(1 - distFromCenter / maxDist, 0, 1);

                if (skillsCore) {
                    skillsCore.style.transform = 'scale(' + skillsProg + ')';
                }
                if (orbitRing1) {
                    orbitRing1.style.opacity = skillsProg * 0.4;
                    orbitRing1.style.transform = 'scale(' + lerp(0.7, 1, skillsProg) + ')';
                }
                if (orbitRing2) {
                    orbitRing2.style.opacity = skillsProg * 0.3;
                    orbitRing2.style.transform = 'scale(' + lerp(0.7, 1, skillsProg) + ')';
                }

                skillItems.forEach(function (item, i) {
                    var itemStart = (i / skillItems.length) * 0.5;
                    var itemProg = clamp(mapRange(skillsProg, itemStart, itemStart + 0.4, 0, 1), 0, 1);
                    item.style.transform = 'translate(-50%, -50%) scale(' + itemProg + ')';
                    item.style.opacity = itemProg;
                });
            }

            // --- Journey timeline: progress line fill + item reveals ---
            if (journeyTimeline && !prefersReducedMotion) {
                var journeyRect = journeyTimeline.getBoundingClientRect();
                var journeyProg = clamp(
                    mapRange(journeyRect.top, viewportH, -journeyRect.height * 0.3, 0, 1),
                    0, 1
                );

                if (journeyFillInner) {
                    journeyFillInner.style.height = (journeyProg * 100) + '%';
                }

                journeyItems.forEach(function (item) {
                    var itemRect = item.getBoundingClientRect();
                    // Toggle so items re-animate when scrolled back into view
                    if (itemRect.top < viewportH * 0.85 && itemRect.bottom > 0) {
                        item.classList.add('in-view');
                        item.style.opacity = '1';
                        item.style.transform = 'translateX(0)';
                    } else {
                        item.classList.remove('in-view');
                        item.style.opacity = '0';
                        item.style.transform = 'translateX(-30px)';
                    }
                });
            }

            // --- Services & Testimonials reveal ---
            serviceCards.forEach(function (card) {
                var cardRect = card.getBoundingClientRect();
                // Toggle so cards re-animate when scrolled back into view
                if (cardRect.top < viewportH * 0.85 && cardRect.bottom > 0) {
                    card.classList.add('in-view');
                } else {
                    card.classList.remove('in-view');
                }
            });

            testimonialCards.forEach(function (card) {
                var cardRect = card.getBoundingClientRect();
                if (cardRect.top < viewportH * 0.85 && cardRect.bottom > 0) {
                    card.classList.add('in-view');
                } else {
                    card.classList.remove('in-view');
                }
            });

            ticking = false;
        }

        // ------------------------------------------------------------------
        // Scroll & mouse handlers
        // ------------------------------------------------------------------
        function onScroll() {
            if (!ticking) {
                window.requestAnimationFrame(updateScroll);
                ticking = true;
            }
        }

        function onMouseMove(e) {
            if (prefersReducedMotion) return;
            targetMouseX = (e.clientX / window.innerWidth - 0.5) * 2;
            targetMouseY = (e.clientY / window.innerHeight - 0.5) * 2;
        }

        // ------------------------------------------------------------------
        // Smooth scroll for scene nav dots
        // ------------------------------------------------------------------
        sceneNavDots.forEach(function (dot) {
            dot.addEventListener('click', function (e) {
                e.preventDefault();
                var target = document.querySelector(dot.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        // ------------------------------------------------------------------
        // Journey progress line — inject fill element (can't style ::after via JS)
        // ------------------------------------------------------------------
        if (journeyTimeline) {
            var progressLineEl = journeyTimeline.querySelector('.journey-progress-line');
            if (progressLineEl) {
                journeyFillInner = document.createElement('div');
                journeyFillInner.className = 'journey-progress-fill-inner';
                journeyFillInner.style.cssText =
                    'position:absolute;top:0;left:0;width:100%;height:0%;' +
                    'background:linear-gradient(180deg,var(--accent),var(--accent-hover));' +
                    'border-radius:2px;transition:height 0.1s linear;will-change:height;';
                progressLineEl.appendChild(journeyFillInner);
            }
        }

        // ------------------------------------------------------------------
        // Move fixed elements to <body> to escape page-content-wrapper
        // stacking context (z-index:10) so they sit above the header (z-index:100)
        // ------------------------------------------------------------------
        var progressBar = document.getElementById('scrollProgressBar');
        var sceneNav = document.getElementById('sceneNav');
        if (progressBar) document.body.appendChild(progressBar);
        if (sceneNav) document.body.appendChild(sceneNav);

        // ------------------------------------------------------------------
        // Generic scroll reveal — re-triggers every time elements enter/leave
        // Apply [data-reveal] to any content element for a scroll-in animation.
        // Variants: data-reveal="left|right|scale|fade"
        // Stagger:  data-reveal-delay="1..6"
        // ------------------------------------------------------------------
        var revealEls = document.querySelectorAll('[data-reveal]');
        if (revealEls.length) {
            if ('IntersectionObserver' in window && !prefersReducedMotion) {
                var revealObserver = new IntersectionObserver(function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('is-visible');
                        } else {
                            entry.target.classList.remove('is-visible');
                        }
                    });
                }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
                revealEls.forEach(function (el) { revealObserver.observe(el); });
            } else {
                // Reduced motion / no observer support: show immediately
                revealEls.forEach(function (el) { el.classList.add('is-visible'); });
            }
        }

        // ------------------------------------------------------------------
        // Initialize
        // ------------------------------------------------------------------
        positionSkillItems();
        updateScroll();

        window.addEventListener('scroll', onScroll, { passive: true });
        window.addEventListener('mousemove', onMouseMove, { passive: true });
        window.addEventListener('resize', function () {
            positionSkillItems();
            updateScroll();
        }, { passive: true });

        // Re-run on load (images may change layout)
        window.addEventListener('load', function () {
            positionSkillItems();
            updateScroll();
        });
    });
})();