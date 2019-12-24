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
	rm -rf $(VENV_NAME) $(MIGRATION_FOLDER)

init_db:
	if [ ! -d ${MIGRATION_FOLDER} ] ; then \
		python3 manage.py db init; \
		python3 manage.py db upgrade; \
		python3 manage.py db migrate; \
		python3 manage.py db upgrade; \
	else \
		python3 manage.py db upgrade; \
		python3 manage.py db migrate; \
		python3 manage.py db upgrade; \
	fi


lint:
	${PYTHON} -m pylint file_service

test:
	${PYTHON} -m pytest tests/BaseTest.py

coverage:
	env/bin/coverage run --omit env\* -m unittest discover
	env/bin/coverage report -m
