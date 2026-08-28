.PHONY: check gate% words claims register struct rubric cites prereg lock-prereg freeze setup
PY := python3

setup:
	$(PY) -m pip install -r requirements.txt

check:            ; cd checks && $(PY) run_all.py
gate%:            ; cd checks && $(PY) run_all.py --gate G$*
claims:           ; cd checks && $(PY) check_forbidden_claims.py
register:         ; cd checks && $(PY) check_register.py
words:            ; cd checks && $(PY) check_wordcount.py
struct:           ; cd checks && $(PY) check_structure.py
rubric:           ; cd checks && $(PY) check_rubric_trace.py
cites:            ; cd checks && $(PY) check_citations.py
prereg:           ; cd checks && $(PY) check_prereg.py

# Day 2. Locks the analysis plan before any R2 data is seen.
lock-prereg:
	@test -s preregistration/PREREGISTRATION.md || (echo "write the pre-registration first"; exit 1)
	@shasum -a 256 preregistration/PREREGISTRATION.md | awk '{print $$1}' > preregistration/HASH.txt
	@date -u +"locked %Y-%m-%dT%H:%M:%SZ" >> preregistration/HASH.txt
	@cat preregistration/HASH.txt

# Day 7. Records the freeze so nothing drifts in afterwards.
freeze:
	@date -u +"DATA FREEZE %Y-%m-%dT%H:%M:%SZ" > results/FREEZE.txt
	@git rev-parse HEAD >> results/FREEZE.txt
	@cat results/FREEZE.txt
sources:          ; cd checks && $(PY) check_sources.py
