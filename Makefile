.PHONY: test package demo sample-pdf

test:
	python3 -m pytest

package:
	python3 scripts/package_skills.py

demo:
	python3 scripts/demo_invoice.py

sample-pdf:
	python3 scripts/make_sample_pdf.py
