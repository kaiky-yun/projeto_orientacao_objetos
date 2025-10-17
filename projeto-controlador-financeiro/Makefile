PY=python3.12

venv:
	$(PY) -m venv .venv

install: venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && $(PY) -m finance.cli

test:
	. .venv/bin/activate && pytest -q
