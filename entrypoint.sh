#!/bin/sh
python manage.py migrate
python manage.py collectstatic --no-input --clear
gunicorn config.wsgi:application --bind 0.0.0.0:8000
