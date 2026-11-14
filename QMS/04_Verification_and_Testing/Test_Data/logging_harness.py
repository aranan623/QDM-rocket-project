"""Test harness for QDM-TP-002.

Runs the ground station's own logging path (open_csv -> simulate_loop ->
handle_telemetry -> CSV) without starting the web server, so the test does
not depend on port 5000 being free. Stop it with Ctrl+C or by killing it.

Usage: python3 logging_harness.py /path/to/rocket-ground-station
"""
import sys

sys.path.insert(0, sys.argv[1])
sys.argv = ["app.py", "--simulate"]

import app  # the ground station module under test

app.open_csv()
app.simulate_loop()
