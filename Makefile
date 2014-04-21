all: test

upload:
	python setup.py sdist upload

test:
	python -m unittest discover
