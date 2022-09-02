default: test

test: env
	.env/bin/pytest

env: .env/.up-to-date

.env/.up-to-date: setup.py Makefile
	python -m virtualenv .env
	.env/bin/pip install -e ".[testing]"
	touch $@

