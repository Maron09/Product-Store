# Define variables
DJANGO_MANAGE = python manage.py

# Run the Django development server
run:
	$(DJANGO_MANAGE) runserver 8001

# Apply migrations
migrate:
	$(DJANGO_MANAGE) migrate

# Make migrations
makemigrations:
	$(DJANGO_MANAGE) makemigrations

# Create a superuser
createsuperuser:
	$(DJANGO_MANAGE) createsuperuser

# Collect static files
collectstatic:
	$(DJANGO_MANAGE) collectstatic --noinput

# Run tests
test:
	$(DJANGO_MANAGE) test

# Clean up __pycache__ files
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Run shell
shell:
	$(DJANGO_MANAGE) shell
