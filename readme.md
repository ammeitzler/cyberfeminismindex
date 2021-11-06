# Setup

1. Install dependencies: 
    1. `pip install -r requirements.txt`

2. Check if your package-config is working:
    1. `pkg-config zlib --libs`
    2. `brew install zlib`
    3. `export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/local/Cellar/zlib/1.2.11/lib/pkgconfig/`

# Running locally
1. `./manage.py migrate`
2. `./manage.py collectstatic`
3. `./manage.py runserver`
4. In another terminal window, make sure `redis` is running
	1. `redis-server`

- Visit `localhost:8000`

- Admin access from /admin

# Architecture

- Wagtail CMS using Django. Hosted on DigitalOcean over HTTPS with Nginx, Gunicorn and Redis

# Collaborators
- Mindy Seu, Charles Broskoski, Janine Rosen
