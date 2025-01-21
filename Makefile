install:
	pip install -e ".[dev]"

test: install
	pytest tests/*