ACTIVATE=. .venv/bin/activate


# see: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
PHONY: help
help: ## help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

.PHONY: init
init: ## initalize repos
	python3.10 -m venv .venv --prompt cringeycat	
	mkdir -p db/feeds
	mkdir -p build

.PHONY: install
install: ## install libs
	$(ACTIVATE) && pip install -r requirements.txt


.PHONY:
setup-web:
	mkdir -p build
	cp -R staticfiles/* build

.PHONY: run
run: ## run cringeycat
	$(ACTIVATE) && python cringeycat.py

.PHONY:
build: setup-web run


	
