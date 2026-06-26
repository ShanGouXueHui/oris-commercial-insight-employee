#!/usr/bin/env bash
cd "${PRODUCT_DIR:-$HOME/projects/oris-commercial-insight-employee}" || exit 1
echo "Insight Rebuild Module 36 official bootstrap starting..."
python3 -m unittest discover -s tests -p 'test_*.py' -q
export TEST_RC=$?
python3 scripts/w36.py
exit "$TEST_RC"
