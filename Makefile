all: report

upload:
	python setup.py sdist upload

test:
	python setup.py test

report:
	coverage run --source mongu.py setup.py test && coverage report
