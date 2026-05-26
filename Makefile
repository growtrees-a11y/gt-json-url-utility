.PHONY: build test up down logs deploy clean shell lint

IMAGE_NAME := ghcr.io/growtrees-a11y/fino-json-url-utility
COMPOSE := docker compose

## ── Docker ──────────────────────────────────────────────

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

shell:
	$(COMPOSE) exec app bash

clean:
	$(COMPOSE) down -v --remove-orphans
	docker image prune -f

## ── CI / CD ────────────────────────────────────────────

test:
	python3 -m pytest test_main.py -v

lint:
	pip install flake8
	flake8 --max-line-length=120 .

deploy: build
	@echo "Push image to GHCR..."
	docker push $(IMAGE_NAME):latest

deploy-docker-login:
	@echo "Log in to GHCR, then run: make deploy"
	docker login ghcr.io
