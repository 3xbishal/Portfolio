/* ==========================================================================
   Portfolio Custom JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {

    // --- Click Destroy Effect (fallback for browsers without :has() support) ---
    (function() {
        var destroyTargets = document.querySelectorAll('.card, .project-card, .service-card, .experience-item, .contact-info-item');
        destroyTargets.forEach(function(target) {
            target.addEventListener('mousedown', function(e) {
                // Skip if clicking a navigation link (href attribute)
                var closestLink = e.target.closest('a[href]');
                if (closestLink && closestLink.getAttribute('href') && !closestLink.getAttribute('href').startsWith('#') && closestLink.getAttribute('href') !== 'javascript:void(0)') {
                    return;
                }
                // Only trigger if clicking a button or .btn inside
                if (e.target.closest('button, .btn')) {
                    this.style.animation = 'none';
                    // Force reflow
                    void this.offsetHeight;
                    this.style.animation = 'destroyEffect 0.6s ease-out forwards';
                }
            });
        });
    })();

    // --- Initialize AOS (Animate On Scroll) ---
    if (typeof AOS !== 'undefined') {
        AOS.init({
            once: true,
            duration: 800,
            easing: 'ease-out-cubic',
            mirror: false,
        });
    }

    // --- Initialize Fancybox (Lightbox Gallery) ---
    if (typeof Fancybox !== 'undefined') {
        Fancybox.bind('[data-fancybox="gallery"]', {
            // Default options
        });
    }

    // --- Smooth scroll for anchor links ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // --- Auto-dismiss alerts after 5 seconds ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // --- Header background on scroll ---
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // --- Initialize tooltips ---
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // --- Initialize carousels ---
    const carouselList = [].slice.call(
        document.querySelectorAll('.carousel')
    );
    carouselList.map(function(carouselEl) {
        return new bootstrap.Carousel(carouselEl, {
            interval: 5000,
            pause: 'hover',
            wrap: true
        });
    });

    // --- Form validation enhancement ---
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // --- Lazy loading for images ---
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.classList.remove('lazy');
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    }


    // --- Back to top button ---
    const backToTopBtn = document.createElement('button');
    backToTopBtn.id = 'backToTop';
    backToTopBtn.className = 'btn btn-primary position-fixed bottom-0 end-0 m-4';
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopBtn.style.display = 'none';
    backToTopBtn.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopBtn);

    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    // --- Animated Background Toggle (Desktop + Mobile) ---
    (function () {
        var toggleBtns = [
            document.getElementById('animatedBgToggle'),
            document.getElementById('animatedBgToggleMobile')
        ].filter(Boolean);

        if (toggleBtns.length === 0) return;

        var isEnabled = true;

        function updateAllIcons(enabled) {
            toggleBtns.forEach(function(btn) {
                var icon = btn.querySelector('i');
                if (!icon) return;
                if (enabled) {
                    icon.className = 'fas fa-magic';
                    btn.title = 'Remove animated background';
                } else {
                    icon.className = 'fas fa-circle-xmark';
                    btn.title = 'Enable animated background';
                }
                btn.setAttribute('aria-pressed', String(enabled));
            });
        }

        function handleToggle() {
            isEnabled = !isEnabled;

            if (isEnabled) {
                if (window.AnimatedBackground) {
                    window.AnimatedBackground.restoreParticles();
                }
                var bg = document.querySelector('.animated-bg');
                if (bg) bg.classList.remove('reduced-motion');
            } else {
                if (window.AnimatedBackground) {
                    window.AnimatedBackground.clearParticles();
                }
            }

            updateAllIcons(isEnabled);
        }

        toggleBtns.forEach(function(btn) {
            btn.addEventListener('click', handleToggle);
        });

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            isEnabled = false;
            updateAllIcons(false);
        }
    })();

    // --- Dark Mode Toggle (Desktop + Mobile) ---
    (function () {
        var darkModeBtns = [
            document.getElementById('darkModeToggle'),
            document.getElementById('darkModeToggleMobile')
        ].filter(Boolean);

        if (darkModeBtns.length === 0) return;

        var isDark = localStorage.getItem('dark_mode') === 'true';

        function updateDarkModeUI(enabled) {
            darkModeBtns.forEach(function(btn) {
                var icon = btn.querySelector('i');
                if (!icon) return;
                if (enabled) {
                    icon.className = 'fas fa-sun';
                } else {
                    icon.className = 'fas fa-moon';
                }
                btn.setAttribute('aria-pressed', String(enabled));
                btn.classList.toggle('active', enabled);
            });
        }

        function applyDarkMode(enabled) {
            if (enabled) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('dark_mode', 'true');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('dark_mode', 'false');
            }
            updateDarkModeUI(enabled);

            if (window.AnimatedBackground) {
                window.AnimatedBackground.updateThemeColor();
            }
        }

        applyDarkMode(isDark);

        darkModeBtns.forEach(function(btn) {
            btn.addEventListener('click', function () {
                isDark = !isDark;
                applyDarkMode(isDark);
            });
        });
    })();

    // --- Admin sidebar toggle (mobile + collapse) ---
    const adminSidebarToggle = document.getElementById('adminSidebarToggle');
    const adminBackdrop = document.getElementById('adminBackdrop');
    if (adminSidebarToggle) {
        // restore state from localStorage
        if (localStorage.getItem('admin_sidebar_state') === 'collapsed') {
            document.body.classList.add('sidebar-collapsed');
            adminSidebarToggle.setAttribute('aria-expanded', 'true');
        }

        function openSidebar() {
            document.body.classList.add('sidebar-open');
            adminSidebarToggle.setAttribute('aria-expanded', 'true');
            const firstLink = document.querySelector('.admin-sidebar a, .admin-sidebar button');
            if (firstLink) firstLink.focus();
        }

        function closeSidebar() {
            document.body.classList.remove('sidebar-open');
            adminSidebarToggle.setAttribute('aria-expanded', 'false');
            adminSidebarToggle.focus();
        }

        adminSidebarToggle.addEventListener('click', function(e) {
            if (window.innerWidth < 992) {
                if (document.body.classList.contains('sidebar-open')) {
                    closeSidebar();
                } else {
                    openSidebar();
                }
            } else {
                const collapsed = document.body.classList.toggle('sidebar-collapsed');
                adminSidebarToggle.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
                if (collapsed) {
                    localStorage.setItem('admin_sidebar_state', 'collapsed');
                } else {
                    localStorage.removeItem('admin_sidebar_state');
                }
            }
        });

        // click outside -> close (on mobile)
        document.addEventListener('click', function(ev) {
            if (window.innerWidth < 992 && document.body.classList.contains('sidebar-open')) {
                const sidebar = document.querySelector('.admin-sidebar');
                const toggle = adminSidebarToggle;
                if (!sidebar.contains(ev.target) && !toggle.contains(ev.target)) {
                    closeSidebar();
                }
            }
        });

        // close when clicking backdrop
        if (adminBackdrop) {
            adminBackdrop.addEventListener('click', function() {
                closeSidebar();
            });
        }

        // close when clicking the sidebar's internal close button (mobile)
        const adminSidebarClose = document.getElementById('adminSidebarClose');
        if (adminSidebarClose) {
            adminSidebarClose.addEventListener('click', function() {
                closeSidebar();
            });
        }

        // close on link click (mobile)
        document.querySelectorAll('.admin-sidebar a').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    closeSidebar();
                }
            });
        });

        // keyboard accessibility: Esc to close, Ctrl/Cmd+M to toggle, focus trap for Tab
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'm') {
                e.preventDefault();
                if (document.body.classList.contains('sidebar-open')) closeSidebar(); else openSidebar();
                return;
            }
            if (e.key === 'Escape' || e.key === 'Esc') {
                if (document.body.classList.contains('sidebar-open')) {
                    closeSidebar();
                }
                return;
            }

            if (document.body.classList.contains('sidebar-open') && window.innerWidth < 992) {
                if (e.key === 'Tab') {
                    const focusable = Array.from(document.querySelectorAll('.admin-sidebar a, .admin-sidebar button, #adminSidebarToggle'))
                        .filter(el => el.offsetParent !== null);
                    if (focusable.length === 0) return;
                    const first = focusable[0];
                    const last = focusable[focusable.length - 1];
                    if (e.shiftKey && document.activeElement === first) {
                        e.preventDefault();
                        last.focus();
                    } else if (!e.shiftKey && document.activeElement === last) {
                        e.preventDefault();
                        first.focus();
                    }
                }
            }
        });

        // ensure overlay mode is cleared when resizing to desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 992) {
                document.body.classList.remove('sidebar-open');
            }
        });

        // Animate admin cards after the sidebar logic has initialized
        const adminCards = document.querySelectorAll('.admin-content .card');
        adminCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 60}ms`;
            card.classList.add('admin-reveal');
        });
    }

});
