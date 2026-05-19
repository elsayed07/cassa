.PHONY: dev up down logs build shell bash migrate migrations test test-cov lint format typecheck seed createsuperuser messages compilemessages prod-build prod-up prod-down clean install pre-commit

UV = py -3.14 -m uv
RUN = docker compose exec django

dev:
	docker compose up

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	$(RUN) python manage.py shell

bash:
	$(RUN) bash

migrate:
	$(RUN) python manage.py migrate

migrations:
	$(RUN) python manage.py makemigrations

test:
	$(RUN) python -m pytest -x -q

test-cov:
	$(RUN) python -m pytest --cov --cov-report=html -q

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format . && $(UV) run ruff check --fix .

typecheck:
	$(UV) run pyright

seed:
	$(RUN) python manage.py seed

createsuperuser:
	$(RUN) python manage.py createsuperuser

messages:
	$(RUN) python manage.py makemessages -l es -l fr -l de

compilemessages:
	$(RUN) python manage.py compilemessages

prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

clean:
	docker compose down -v --remove-orphans

install:
	$(UV) sync

pre-commit:
	$(UV) run pre-commit run --all-files
