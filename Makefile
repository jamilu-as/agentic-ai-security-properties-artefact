.PHONY: help check lock-prereg freeze setup prose stale semantic refresh
# NB: gate0..gate5 are deliberately NOT .PHONY - GNU make will not apply the
# gate% pattern rule to a target declared phony, which silently made them no-ops.
PY := python3

help:
	@echo "make check        all checks, advisory"
	@echo "make gate<N>      enforce gate N (0-5)"
	@echo "make lock-prereg  hash-lock the pre-registration (G1, before any R2 data)"
	@echo "make freeze       record the data freeze (G2)"
	@echo "make prose        academic register: self-appraisal, AI tells, tic density"
	@echo "make stale        cross-file fact consistency + derived-file freshness"
	@echo "make semantic     judgements needing a reader, not a regex"
	@echo "make refresh      re-stamp derived files after reviewing them"
	@echo "make setup        install check dependencies"
	@echo ""
	@echo "Individual checks: $(PY) checks/<name>.py --advisory"
	@echo "Reviewer agents:   /review G4"

setup:            ; $(PY) -m pip install -r requirements.txt
check:            ; cd checks && $(PY) run_all.py
prose:            ; cd checks && $(PY) check_prose.py --advisory
stale:            ; cd checks && $(PY) check_staleness.py --advisory
semantic:         ; cd checks && $(PY) check_semantic.py --advisory

# Re-stamp derived files AFTER reading them. The hash claims a human checked it.
refresh:          ; cd checks && $(PY) refresh.py
gate%:            ; cd checks && $(PY) run_all.py --gate G$*

# G1. Locks the analysis plan before any R2 data is seen.
lock-prereg:
	@test -s preregistration/PREREGISTRATION.md || (echo "write the pre-registration first"; exit 1)
	@shasum -a 256 preregistration/PREREGISTRATION.md | awk '{print $$1}' > preregistration/HASH.txt
	@date -u +"locked %Y-%m-%dT%H:%M:%SZ" >> preregistration/HASH.txt
	@cat preregistration/HASH.txt

# G2. Records the freeze so nothing drifts in afterwards.
freeze:
	@date -u +"DATA FREEZE %Y-%m-%dT%H:%M:%SZ" > work/w2-composition/results/FREEZE.txt
	@git rev-parse HEAD >> work/w2-composition/results/FREEZE.txt
	@cat work/w2-composition/results/FREEZE.txt
