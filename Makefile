.PHONY: help test clean dockerbuild dockerserve dockershell deploy


DOCKER_CONFIG=compose.yaml


help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  test           Run the full test suite"
	@echo "  clean          Delete assets processed by webpack"
	@echo "  dockerbuild    Build the Docker compose dev environment"
	@echo "  dockerserve    Run the Docker containers for the site"
	@echo "                 (starts a webserver on http://localhost:8000)"
	@echo "  dockershell    Connect to a bash shell on the Django Docker container"
	@echo "  deploy         Deploy the app to fly.io"


test:
	tox

clean:
	rm -rf assets/dist/*

# Build the local multi-container application
# This command can take a while the first time
dockerbuild:
	docker compose -f $(DOCKER_CONFIG) build

# You should run "dockerbuild" at least once before running this
# It isn't a dependency because running "dockerbuild" can take some time
dockerserve:
	docker compose -f $(DOCKER_CONFIG) up

# Use this command to inspect the container, run management commands,
# or run anything else on the Django container. It does expect the
# container to already be running
dockershell:
	docker compose -f $(DOCKER_CONFIG) exec django /bin/bash

# Build and deploy the production container
deploy:
	flyctl deploy
