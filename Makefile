all: test

upload:
	python setup.py sdist upload

test:
	python setup.py test
