# Django K8s Project Guide

## Commands

- Test: `make APP=app.tests.TestClass.test_method test` (single test format)
- Run dev server: `devenv processes up -d` - ALWAYS check if it's already running first.
- Migrate: `python manage.py makemigrations && python manage.py migrate`
- Build Docker: `make SHORT_SHA=<sha> build-docker-image`
- Deploy: `make IMAGE_TAG=<tag> ENVIRONMENT=<env> NAMESPACE=<ns> KUBECONFIG=<config> deploy`

## Dependency Management

- Uses `uv` for Python dependency management (pyproject.toml + uv.lock)
- Install dependencies: `uv sync`
- Add new dependency: `uv add <package>`
- Add dev dependency: `uv add --dev <package>`

## Architecture

- Django 5.2+ project with PostgreSQL database
- Apps: `myauth` (custom user), `post` (blog posts), `myutils` (shared behaviors), `core` (storage, etc)
- Kubernetes deployment with Helm charts in `chart/`
- AWS S3/Scaleway object storage for static/media files via django-storages
- Custom storage classes in `core/customstorage.py`

## Code Style

- Django conventions: PascalCase models, snake_case fields/methods
- Environment config via django-environ (prefix: DJANGO\_\*)
- Abstract model behaviors in `myutils.behaviors` (Timestampable, Permalinkable)
- Test files: `tests.py` in each app, inherit from `django.test.TestCase`
- String representations required for models (`__str__` method)
- Use `get_user_model()` for user model references
