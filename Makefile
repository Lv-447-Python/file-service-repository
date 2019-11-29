.PHONY: help setup init_db run test lint

VENV_NAME?=env
PYTHON=${VENV_NAME}/bin/python3
MIGRATION_FOLDER?=migrations

setup: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: requirements.txt
	make clean
	test -d $(VENV_NAME) || python3 -m virtualenv $(VENV_NAME)
	mkdir files
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	make init_db

clean:
	rm -rf $(VENV_NAME) $(MIGRATE_FOLDER)

init_db:
	createdb -U postgres statcrutch
	${PYTHON} manage.py db init
	${PYTHON} manage.py db upgrade
	${PYTHON} manage.py db migrate
	${PYTHON} manage.py db upgrade

lint:
	${PYTHON} -m pylint file_service

test:
	${PYTHON} -m pytest tests/BaseTest.py
