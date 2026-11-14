import sys, threading, os, csv
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO
from telemetry_format import FIELD_NAMES, decode_packet
from fake_telemetry import generate_fake_telemetry

SIMULATE = "--simulate" in sys.argv

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

CSV_PATH = os.path.expanduser("~/rocket-ground-station/telemetry_log.csv")
FIELDS = FIELD_NAMES + ["received_at"]

flight_state = "READY"
packet_count = 0
max_altitude = 0.0
csv_file = None
writer = None

def open_csv():
    global csv_file, writer
    file_exists = os.path.exists(CSV_PATH)
    csv_file = open(CSV_PATH, "a", newline="")
    writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
    if not file_exists:
        writer.writeheader()
        csv_file.flush()

def update_flight_state(t):
    global flight_state, max_altitude
    if t["launched"] and flight_state == "READY":
        flight_state = "LAUNCH"
    if flight_state == "LAUNCH" and t["altitude_m"] > 2:
        flight_state = "ASCENT"
    if t["altitude_m"] > max_altitude:
        max_altitude = t["altitude_m"]
    if t["apogee"] and flight_state == "ASCENT":
        flight_state = "APOGEE"
    if flight_state == "APOGEE" and t["vertical_velocity_mps"] < -1:
        flight_state = "DESCENT"
    if flight_state == "DESCENT" and abs(t["vertical_velocity_mps"]) < 0.5 and t["altitude_m"] < 5:
        flight_state = "LANDED"

def handle_telemetry(telemetry):
    global packet_count
    packet_count += 1
    telemetry["received_at"] = datetime.now().isoformat()
    update_flight_state(telemetry)

    writer.writerow({k: telemetry[k] for k in FIELDS})
    csv_file.flush()
    os.fsync(csv_file.fileno())

    telemetry["packet_count"] = packet_count
    telemetry["flight_state"] = flight_state
    telemetry["max_altitude"] = max_altitude
    socketio.emit("telemetry", telemetry)

def simulate_loop():
    print("SIMULATE MODE: generating fake telemetry, no radio used.")
    for telemetry in generate_fake_telemetry():
        handle_telemetry(telemetry)

def radio_loop():
    from LoRaRF import SX127x

    LoRa = SX127x()
    if not LoRa.begin():
        print("ERROR: Could not detect Radio A - check wiring")
        return

    LoRa.setFrequency(433000000)
    LoRa.setLoRaModulation(7, 250000, 5, False)
    LoRa.setLoRaPacket(LoRa.HEADER_EXPLICIT, 12, 255, True, False)
    LoRa.setSyncWord(0x34)

    print("REAL RADIO MODE: listening on Radio A.")
    while True:
        LoRa.request()
        LoRa.wait()
        length = LoRa.available()
        if length > 0:
            raw = bytes(LoRa.read() for _ in range(length))
            try:
                handle_telemetry(decode_packet(raw))
            except ValueError as e:
                print("Skipped a bad packet:", e)

@app.route("/")
def index():
    return render_template("dashboard.html")

if __name__ == "__main__":
    open_csv()
    target = simulate_loop if SIMULATE else radio_loop
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    socketio.run(app, host="0.0.0.0", port=5000)
