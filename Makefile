.PHONY: help test clean deploy


help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  test           Run the full test suite"
	@echo "  clean          Delete assets processed by webpack"
	@echo "  deploy         Deploy the app to fly.io"


test:
	tox

clean:
	rm -rf assets/dist/*

# Build and deploy the production container
deploy:
	flyctl deploy
