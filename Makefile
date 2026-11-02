SCAN ?= 1961
PY := python3

.PHONY: firstpass render ocr parse report check

firstpass:
	$(PY) pipeline/firstpass.py all --scan $(SCAN)

render ocr parse report:
	$(PY) pipeline/firstpass.py $@ --scan $(SCAN)

check:
	$(PY) -m py_compile pipeline/firstpass.py
