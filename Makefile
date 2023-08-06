# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

build:
	docker-compose build

up:
	docker-compose up -d app celery

down:
	docker-compose down --remove-orphans

test: up
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/

logs:
	docker-compose logs app | tail -100

black:
	black -l 86 $$(find * -name '*.py')

pysh:
	docker-compose run --rm --no-deps --entrypoint=python app /src/web/manage.py shell

bash:
	docker-compose run --rm --no-deps --entrypoint=/bin/bash app

createsuperuser:
	docker-compose run --rm --no-deps --entrypoint=python app /src/web/manage.py createsuperuser
