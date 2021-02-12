THRIFT_DIR=./flipper_thrift
THRIFT_PYTHON=${THRIFT_DIR}/python
PKG_VERSION = $(shell python -c "import pkg_resources; print(pkg_resources.require('flipper-client')[0].version)")


install:
	python setup.py install


install-dev:
    pip install --upgrade pip
	pip install -e .[dev]
	pre-commit install
	pre-commit install-hooks


virtualenv: virtualenv-install


virtualenv-install:
	@pyenv virtualenv -p python3.6 3.6.5 flipper-client


thrift:
	thrift -r --gen py -out ${THRIFT_PYTHON} ${THRIFT_DIR}/*.thrift


clean:
	@rm -rf build
	@rm -rf dist


build: clean
	python setup.py sdist bdist_wheel


version:
	@echo ${PKG_VERSION}


publish: build
	twine upload dist/*


hooks:
	pre-commit run --all-files


mypy:
	@mypy --follow-imports=silent --ignore-missing-imports flipper


circleci-install:
	brew install circleci
	circleci setup


validate-circleci:
	circleci config validate


exec-circleci: validate-circleci
	circleci local execute
