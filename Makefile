NOSETESTS = nosetests

all: test

test: test-quick test-slow

test-quick:
	$(NOSETESTS) -a '!slow'

test-slow:
	$(NOSETESTS) -a 'slow'

.PHONY: all test test-quick test-slow
