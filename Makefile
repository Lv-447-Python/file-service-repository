.PHONY: help setup db_migrate run test lint

VENV_NAME?=env
PYTHON=${VENV_NAME}/bin/python3

.DEFAULT: help
help:
	@echo "make setup"
	@echo "       full "
	@echo "make run"
	@echo "       run project"
	@echo "make lint"
	@echo "       run pylint and mypy"
	@echo "make test"
	@echo "       run tests"


setup: $(VENV_NAME)/bin/activate 
$(VENV_NAME)/bin/activate: requirements.txt
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	mkdir files
	touch $(VENV_NAME)/bin/activate
	make db_migrate
	${PYTHON} manage.py db upgrade
	${PYTHON} manage.py db migrate

db_migrate: $(VENV_NAME)/bin/activate
	${PYTHON} manage.py db init
	${PYTHON} manage.py db upgrade
	${PYTHON} manage.py db migrate

run: $(VENV_NAME)/bin/activate
	${PYTHON} run.py

test:
	echo "Will be soon..."

lint: $(VENV_NAME)/bin/activate
	$(PYTHON) -m pylint file_service
