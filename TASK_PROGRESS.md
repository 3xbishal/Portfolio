# Portfolio Frontend Fix & Completion Plan

## Issues Found:

### CSS Issues:
1. `--muted` color set to `#000000` in light mode (too dark, should be gray)
2. `animated-bg.css` - `.nav-toggle-btn:hover` transform has `translate(-50%, -50%)` which breaks positioning
3. `.hero-text` CSS class defined but never applied in templates
4. Project images have `max-width: 280px` - too small for card layout
5. Footer social links missing text-decoration fix
6. Footer text color hardcoded to `#000000` instead of using CSS variables
7. Experience timeline missing dark-mode adaptations for the line and dots
8. Section repeating same CSS across style.css and animated-bg.css (dark-mode body definition duplicated)
9. `.header .nav-link.active::after` / hover::after has `left/right: 0.85rem` - too much inset

### Missing Template Sections:
1. **Home page**: Missing **Services** section (services are passed to context but not rendered)
2. **Home page**: Missing **Testimonials** section (testimonials passed to context but not rendered)
3. No testimonial carousel partial component
4. No services card partial component

### Template Issues:
1. `base.html` body has class `portfolio-body` which has no CSS styling
2. `_header.html` doesn't render properly on mobile (animated bg toggle + dark mode buttons use absolute centering which conflicts with navbar layout)

### Missing Features:
1. No active nav detection JavaScript for updating header dynamically
2. Image lazy loading classes not implemented (JS looks for `img.lazy` but no images have that class)