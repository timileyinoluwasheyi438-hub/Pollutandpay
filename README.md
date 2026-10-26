# Pollute and Pay (Django)
```
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env.example | xargs)   # then put real values in your own .env / environment
python manage.py makemigrations core && python manage.py migrate
python manage.py createsuperuser && python manage.py runserver
```
- Google sign-in: create an OAuth client, redirect URI `http://localhost:8000/accounts/google/login/callback/`, put the id/secret in env.
- Paystack: set the webhook URL to `https://YOURDOMAIN/paystack/webhook/`.
- Production: `python manage.py collectstatic`, `gunicorn config.wsgi`, DEBUG=0.
- Text to replace before launch: reviews and blog snippets in `core/content.py`, contact details in `templates/core/base.html`.
