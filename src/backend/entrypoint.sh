#!/bin/bash
source /app/.env

PYTHON_PATH=$(python -c 'import sys; print(sys.executable)')
$PYTHON_PATH manage.py makemigrations app
$PYTHON_PATH manage.py makemigrations
$PYTHON_PATH manage.py migrate app
$PYTHON_PATH manage.py migrate

$PYTHON_PATH manage.py runserver 0.0.0.0:8000