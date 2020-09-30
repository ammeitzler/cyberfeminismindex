# Setup

1. Install dependencies:
    1. `pip install -r requirements.txt`

# Running locally
1. ./manage.py migrate
2. ./manage.py collectstatic
3. ./manage.py runserver
4. Make sure `redis` is running
	1. `redis-server`

- Visit `localhost:8000`

- Admin access from /admin

# Architecture

- Wagtail CMS using Django. Hosted on DigitalOcean over HTTPS with Nginx, Gunicorn and Redis

# Collaborators
- Mindy Seu, Charles Broskoski, Janine Rosen