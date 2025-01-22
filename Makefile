install:
	pip install -e ".[dev]"

test: install
	pytest tests/*

ruff: install
	pip install ruff
	ruff check .
	ruff format .

coverage:
	pip install coverage
	coverage run -m pytest tests/*
	coverage report
