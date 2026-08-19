MAKEFLAGS += --silent
include .env
export $(shell sed 's/=.*//' .env)

# Run docker compose ==========================================================

docker-compose-up:
ifeq ($(build),true)
	docker-compose build --no-cache
	docker-compose up
else
	docker-compose up
endif

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f

# Bash commands ===============================================================

bash-adk-ui:
	docker-compose exec adk-ui bash
