#!/bin/bash
source /backend/.env

# Run migrations
python manage.py makemigrations
python manage.py makemigrations app
python manage.py migratre app
python manage.py migrate

# Start the server
python manage.py runserver 0.0.0.0:8000
