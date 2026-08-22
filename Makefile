MAKEFLAGS += --silent
include .env
export $(shell sed 's/=.*//' .env)

# Run docker compose ==========================================================

docker-compose-up: chrome-debug
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

# Chrome ======================================================================

chrome-debug:
	open -na "Google Chrome" --args \
		--remote-debugging-port=$(SCENARIO_X_CHROME_DEBUGGING_PORT) \
		--enable-features=WebMCP,DevToolsWebMCPSupport \
		--enable-experimental-web-platform-features \
		--user-data-dir=/tmp/chrome-mcp-debug-profile \
		--no-first-run \
		--no-default-browser-check

# Bash commands ===============================================================

bash-adk-ui:
	docker-compose exec adk-ui bash
