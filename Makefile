.PHONY: test package demo

test:
	python3 -m pytest

package:
	python3 scripts/package_skills.py

demo:
	python3 scripts/demo_invoice.py
