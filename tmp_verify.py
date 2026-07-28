import urllib.request

resp = urllib.request.urlopen('http://127.0.0.1:8000/')
html = resp.read().decode('utf-8')

checks = [
    'animated-bg',
    'animatedBgToggle',
    'darkModeToggle',
    'navbar-center',
    'nav-toggle-btn',
    'animated-bg.js',
    'animated-bg.css',
    'dark-mode',
]
for c in checks:
    found = c in html
    status = 'FOUND' if found else 'MISSING'
    print(c + ': ' + status)
