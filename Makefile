default: test

test: env
	.env/bin/pytest -v

env: .env/.up-to-date

.env/.up-to-date: setup.py Makefile
	python -m venv .env
	.env/bin/pip install -e ".[testing]"
	touch $@

