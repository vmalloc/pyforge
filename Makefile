default: test

test: env
	uv run --extra testing pytest tests

env:
	uv venv
	uv pip install -e ".[testing]"
