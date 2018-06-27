THRIFT_DIR=./flipper_thrift
THRIFT_PYTHON=${THRIFT_DIR}/python


thrift:
	thrift -r --gen py -out ${THRIFT_PYTHON} ${THRIFT_DIR}/*.thrift
