init:
	pip install pipenv --upgrade
	# We need to install xcffib first
	pipenv install --skip-lock "xcffib>=0.5.0"
	pipenv install --verbose --sequential --dev --skip-lock
	cd lib/qtile/ && python ./libqtile/ffi_build.py
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
readme:
	python tools/make_readme.py
