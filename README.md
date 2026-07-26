# Django Portfolio Project

A modern, template-based Django web developer portfolio with a fully-featured admin panel for content management.

## Features

- **Admin-Controlled Content**: All portfolio content is managed through Django's admin panel
- **Responsive Design**: Built with Bootstrap 5, fully responsive on all devices
- **Portfolio Pages**:
  - Home page with hero section, featured projects, skills, services, testimonials
  - About page with experience, education, and skills
  - Projects listing with pagination
  - Project detail pages with gallery
  - Contact page with form
- **Admin Panel**:
  - Profile management (single profile with social links, CV upload)
  - Skill categories and skills with proficiency levels
  - Projects with images, technologies, and gallery
  - Work experience with timeline
  - Education history
  - Testimonials
  - Contact messages with read/unread status
  - Services offered
- **Contact Form**: Visitors can send messages that are stored in the admin
- **Static & Media Files**: Profile images, project screenshots, CV uploads

## Project Structure

```
portfolio_project/
├── manage.py
├── portfolio_project/          # Project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── main/                       # Portfolio app
│   ├── __init__.py
│   ├── admin.py                # Admin panel configuration
│   ├── apps.py
│   ├── models.py               # Database models
│   ├── views.py                # Page views
│   ├── urls.py                 # URL routing
│   ├── forms.py                # Contact form
│   ├── context_processors.py   # Global template context
│   └── migrations/
├── templates/                  # HTML templates
│   ├── base.html               # Base template
│   ├── home.html
│   ├── about.html
│   ├── projects.html
│   ├── project_detail.html
│   ├── contact.html
│   └── partials/
│       ├── _header.html
│       └── _footer.html
├── static/                     # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── media/                      # User-uploaded files (created on first upload)
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create a Superuser

```bash
python manage.py createsuperuser
```

### 4. Start the Development Server

```bash
python manage.py runserver
```

### 5. Access the Application

- **Portfolio Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Admin Panel Usage

After logging into the admin panel, you can manage all portfolio content:

1. **Profile** (Portfolio → Profiles): Add your personal info, social links, and upload a profile image/CV
2. **Skill Categories** (Portfolio → Skill Categories): Create categories like "Frontend", "Backend", "Tools"
3. **Skills** (Portfolio → Skills): Add individual skills with proficiency percentages
4. **Projects** (Portfolio → Projects): Add portfolio projects with descriptions, images, and technologies
5. **Experience** (Portfolio → Experience): Add work experience entries
6. **Education** (Portfolio → Education): Add education history
7. **Testimonials** (Portfolio → Testimonials): Add client/colleague testimonials
8. **Services** (Portfolio → Services): Add services you offer
9. **Contact Messages** (Portfolio → Contact Messages): View and manage messages from the contact form

## Models Overview

| Model | Description |
|-------|-------------|
| `Profile` | Developer profile with contact info, social links, CV |
| `SkillCategory` | Category for grouping skills |
| `Skill` | Individual skill with proficiency level |
| `Project` | Portfolio project with images, links, technologies |
| `ProjectImage` | Additional gallery images for projects |
| `Experience` | Work experience with company, position, dates |
| `Education` | Education history with institution, degree, dates |
| `Testimonial` | Testimonial from client or colleague |
| `ContactMessage` | Message from contact form |
| `Service` | Service offered by the developer |

## Technologies Used

- **Django 4.2** - Backend framework
- **Bootstrap 5** - CSS framework
- **Font Awesome 6** - Icons
- **SQLite** - Database (default, can be changed to PostgreSQL)
- **Pillow** - Image handling

## Customization

### Change the Color Scheme

Edit `static/css/style.css` and modify the gradient colors in the `.text-gradient`, `.btn-primary`, and `.btn-outline-primary` classes.

### Add New Pages

1. Create a view in `main/views.py`
2. Add a URL pattern in `main/urls.py`
3. Create a template in `templates/`

### Deploy to Production

1. Set `DEBUG = False` in `settings.py`
2. Configure `ALLOWED_HOSTS`
3. Set a secure `SECRET_KEY`
4. Use a production database (PostgreSQL recommended)
5. Run `python manage.py collectstatic`
6. Use a WSGI server like Gunicorn

## License

This project is open source and available for personal and commercial use.
