export PYTHONPATH=./

build:
	docker-compose -f quizzing/quiz/infrastructure/container/docker-compose.yml build

run:
	docker-compose -f quizzing/quiz/infrastructure/container/docker-compose.yml up -d

generate-migrations:
	docker-compose -f quizzing/quiz/infrastructure/container/docker-compose.yml run --rm quiz alembic revision --autogenerate -m "$(MSG)"

migrate:
	docker-compose -f quizzing/quiz/infrastructure/container/docker-compose.yml run --rm quiz alembic upgrade head

stop:
	docker-compose -f quizzing/quiz/infrastructure/container/docker-compose.yml stop

redeploy: build migrate run logs

logs:
	docker-compose -f quizzing/quiz/infrastructure/container/docker-compose.yml logs -f

psql:
	docker-compose -f quizzing/quiz/infrastructure/container/docker-compose.yml run --rm db psql -p 5432 -U quizzing -h db