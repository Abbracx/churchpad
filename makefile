build:
	docker compose -f docker-compose.yml up --build -d --remove-orphans

up:
	docker compose -f docker-compose.yml up -d  --remove-orphans	

down:
	docker compose -f docker-compose.yml down

exec:
	docker compose -f docker-compose.yml exec -it web /bin/bash

# To check if the env variables has been loaded correctly!
config:
	docker compose -f docker-compose.yml config 

show-logs:
	docker compose -f docker-compose.yml logs

show-logs-db:
	docker compose -f docker-compose.yml logs postgres

show-logs-web:
	docker compose -f docker-compose.yml logs web

migrations:
	docker compose -f docker-compose.yml run --rm web python manage.py makemigrations

migrate:
	docker compose -f docker-compose.yml run --rm web python manage.py migrate

collectstatic:
	docker compose -f docker-compose.yml run --rm web python manage.py collectstatic --no-input --clear

superuser:
	docker compose -f docker-compose.yml run --rm web python manage.py createsuperuser

down-v:
	docker compose -f docker-compose.yml down -v

volume:
	docker volume inspect local_postgres_data

churchpad-db:
	docker compose -f docker-compose.yml exec postgres psql --username=postgres --dbname=churchpad-db

flake8:
	docker compose -f docker-compose.yml exec web flake8 .

black-check:
	docker compose -f docker-compose.yml exec web black --check --exclude=migrations --exclude=venv .

black-diff:
	docker compose -f docker-compose.yml exec web black --diff --exclude=migrations --exclude=venv .

black:
	docker compose -f docker-compose.yml exec web black --exclude=migrations --exclude=venv .

isort-check:
	docker compose -f docker-compose.yml exec web isort . --check-only --skip venv --skip migrations

isort-diff:
	docker compose -f docker-compose.yml exec web isort . --diff --skip venv --skip migrations

isort:
	docker compose -f docker-compose.yml exec web isort . --skip venv --skip migrations

cov:
	docker compose -f docker-compose.yml exec web pytest -p no:warnings --cov=. -v

cov-html:
	docker compose -f docker-compose.yml exec web pytest -p no:warnings --cov=. --cov-report html

test:
	docker compose -f docker-compose.yml exec web pytest -p no:warnings -v