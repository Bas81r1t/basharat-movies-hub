#!/usr/bin/env bash

# Install dependencies
pip install -r requirements.txt

# Collect static files for CSS etc.
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate
