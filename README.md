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
  - Skills with icons (no proficiency percentages)
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
├── .env                        # Environment variables (not in git)
├── .env.example                # Environment variables template
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create a Superuser

```bash
python manage.py createsuperuser
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

### 6. Access the Application

- **Portfolio Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Admin Panel Usage

After logging into the admin panel, you can manage all portfolio content:

1. **Profile** (Portfolio → Profiles): Add your personal info, social links, and upload a profile image/CV
2. **Skills** (Portfolio → Skills): Add individual skills with icons
3. **Projects** (Portfolio → Projects): Add portfolio projects with descriptions, images, and technologies
4. **Experience** (Portfolio → Experience): Add work experience entries
5. **Education** (Portfolio → Education): Add education history
6. **Testimonials** (Portfolio → Testimonials): Add client/colleague testimonials
7. **Services** (Portfolio → Services): Add services you offer
8. **Contact Messages** (Portfolio → Contact Messages): View and manage messages from the contact form

## Models Overview

| Model | Description |
|-------|-------------|
| `Profile` | Developer profile with contact info, social links, CV |
| `Skill` | Individual skill with icon (no proficiency level) |
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
- **MySQL** - Database (production)
- **Pillow** - Image handling
- **python-dotenv** - Environment variables
- **Gunicorn** - WSGI server
- **WhiteNoise** - Static file serving

## Customization

### Change the Color Scheme

Edit `static/css/style.css` and modify the gradient colors in the `.text-gradient`, `.btn-primary`, and `.btn-outline-primary` classes.

### Add New Pages

1. Create a view in `main/views.py`
2. Add a URL pattern in `main/urls.py`
3. Create a template in `templates/`

## Production Deployment (cPanel)

### Prerequisites

- cPanel hosting with Python app support (or SSH access)
- MySQL database created in cPanel
- Python 3.8+ installed

### Step 1: Upload Files

Upload all project files to your cPanel `public_html` folder or a subdirectory.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root with your production settings:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=your_cpanel_db_name
DB_USER=your_cpanel_db_user
DB_PASSWORD=your_cpanel_db_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 4: Configure Database

1. Create a MySQL database in cPanel
2. Update `.env` with your database credentials
3. Run migrations:
   ```bash
   python manage.py migrate
   ```

### Step 5: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Configure cPanel

1. **Python App**: Set up a Python app in cPanel with the correct Python version
2. **Application Entry Point**: `portfolio_project.wsgi:application`
3. **Application URL**: Set to your domain
4. **Passenger**: Enable if using Passenger WSGI

### Step 8: Set Permissions

```bash
chmod 755 manage.py
chmod -R 755 static/
chmod -R 755 media/
```

### Step 9: Test

Visit your domain and verify the site is working. Log into `/admin/` to manage content.

## License

This project is open source and available for personal and commercial use.