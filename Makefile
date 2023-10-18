RUN = poetry run
DATA = src/prefixmaps/data

test:
	$(RUN) python -m unittest


etl:
	$(RUN) slurp-prefixmaps -d $(DATA)

lint-fix:
	$(RUN) tox -e lint-fix


format: lint-fix