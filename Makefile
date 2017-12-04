init:
	pip install pipenv --upgrade
	pipenv install --sequential --dev --skip-lock
test:
	pipenv run pytest -v --cov plasma --cov-report term-missing:skip-covered tests/
lint:
	pipenv run flake8
	pipenv run pylint --rcfile setup.cfg plasma/
codecov:
	pipenv run codecov
publish:
	python setup.py bdist_wheel sdist
	twine upload -r pypi dist/*
	rm -rf *.egg-info build/ dist/
