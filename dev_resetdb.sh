#!/bin/bash

find . -name "*.pyc" -exec rm {} \;
rm db.sqlite3
rm -rf ../outside/QuizApe/uploads
mkdir -p ../outside/QuizApe/uploads

cp data/company_logo.png ../outside/QuizApe/uploads

# django db and test data process
python manage.py wipe_migrations
python manage.py makemigrations core
python manage.py migrate

echo "=== Creating Test Data ==="
python manage.py create_test_data
