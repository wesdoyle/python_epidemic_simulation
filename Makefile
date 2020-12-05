PROJECT_NAME ?= python_epidemic_simulation

.PHONY: test build simulate

test:
	echo "no tests yet"
coming soon wlcome 123
build:
	pip install -r requirements.txt

simulate:
	source env/bin/activate && python universe.py
