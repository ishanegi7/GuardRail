.PHONY: up down build logs scan test demo

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

test:
	docker compose exec api pytest tests/

demo: up
	@echo "GuardRail AI is running!"
	@echo "Dashboard: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "Demo API: http://localhost:8080"
