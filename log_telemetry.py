import csv, os
from datetime import datetime
from telemetry_format import FIELD_NAMES
from fake_telemetry import generate_fake_telemetry

CSV_PATH = os.path.expanduser("~/rocket-ground-station/telemetry_log.csv")
FIELDS = FIELD_NAMES + ["received_at"]

file_exists = os.path.exists(CSV_PATH)
csv_file = open(CSV_PATH, "a", newline="")
writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
if not file_exists:
    writer.writeheader()
    csv_file.flush()

print(f"Logging simulated telemetry to {CSV_PATH} ... Ctrl+C to stop.")

try:
    for telemetry in generate_fake_telemetry():
        telemetry["received_at"] = datetime.now().isoformat()
        writer.writerow(telemetry)
        csv_file.flush()
        os.fsync(csv_file.fileno())
        print(telemetry)
except KeyboardInterrupt:
    csv_file.close()
