THRIFT_DIR=./flipper_thrift
THRIFT_PYTHON=${THRIFT_DIR}/python
PKG_VERSION = $(shell python -c "import pkg_resources; print(pkg_resources.require('flipper-client')[0].version)")


install:
	python setup.py install


install-dev:
	pip install -e .[dev]


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
	cloudsmith push python carta/pip dist/flipper_client-${PKG_VERSION}-py3-none-any.whl
