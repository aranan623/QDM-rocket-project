QDM-TP-002 test scripts
=======================

To repeat the ground station logging test (takes about one minute):

1. Clone or locate the QDM-rocket-project repository (github.com/aranan623/QDM-rocket-project).
2. Install its requirements: pip install flask flask-socketio
3. From this folder run:

   mkdir -p /tmp/tp002home/rocket-ground-station
   python3 run_tp002.py /path/to/QDM-rocket-project /tmp/tp002home python3

The script starts logging_harness.py, lets it log simulated telemetry for 60 seconds, kills it with SIGKILL,
analyses the CSV log and runs the nine decoder cases. Results are printed and saved to tr002_result.json.

Files
-----
logging_harness.py   runs the ground station's own logging path without the web server
run_tp002.py         the test runner
QDM-TR-002_*         data and figures from the run of 14 Nov 2026 at 19:58 (AJT210)
QDM-TR-001_*         OpenRocket simulation data and figures for QDM1-3
