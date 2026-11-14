# Rocket Ground Station

Raspberry Pi ground station for the QDM model rocket. It receives telemetry over LoRa (Ai-Thinker Ra-02 / SX1278, 433 MHz), logs every packet to CSV and serves a live web dashboard.

## What it does

1. Receives one telemetry packet every 100 ms from the rocket's flight computer.
2. Decodes the 16-field CSV packet (`telemetry_format.py`).
3. Appends every packet to `telemetry_log.csv`, flushing to disk after each row so a power loss costs at most one row.
4. Pushes each packet to a browser dashboard (Flask, Socket.IO, Chart.js).
5. Tracks the flight state: `READY → LAUNCH → ASCENT → APOGEE → DESCENT → LANDED`.

Logging runs in its own thread, so it carries on whether or not a browser is connected.

## Telemetry packet

One line of comma-separated text, 16 values, in this order:

```
time_ms, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, temp_c, pressure_hpa,
altitude_m, vertical_velocity_mps, roll_deg, pitch_deg, yaw_deg, launched, apogee
```

Units: acceleration m/s², gyro °/s, temperature °C, pressure hPa, altitude m, velocity m/s, angles degrees. `launched` and `apogee` are 0/1 flags.

## Hardware

| Ra-02 pin | Pi GPIO (BCM) | Physical pin |
|---|---|---|
| VCC | 3V3 | 1 |
| GND | GND | 6 |
| NSS | GPIO8 (CE0) | 24 |
| MOSI | GPIO10 | 19 |
| MISO | GPIO9 | 21 |
| SCK | GPIO11 | 23 |
| RESET | GPIO22 | 15 |

The Ra-02 is a 3.3 V device. Attach the antenna before powering it.

## Setup (Raspberry Pi OS Lite, 32-bit)

```bash
sudo raspi-config        # Interface Options -> SPI -> Yes, then reboot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
python3 app.py --simulate   # simulated flight, no radio needed
python3 app.py              # real radio
```

Dashboard: `http://groundstation.local:5000`

## Files

| File | Purpose |
|---|---|
| `app.py` | Main server: telemetry thread, CSV logging, flight state, dashboard |
| `telemetry_format.py` | Packet encode and decode |
| `fake_telemetry.py` | Simulated flight for testing without a radio |
| `log_telemetry.py` | Standalone CSV logging test |
| `test_packet_format.py` | Encode/decode round-trip self-test |
| `test_flight_profile.py` | Self-test for the simulated flight profile |
| `test_spi_connection.py` | Checks the Pi can talk to the Ra-02 over SPI |
| `templates/dashboard.html` | Live dashboard page |

## Radio settings

433 MHz, SF7, 250 kHz bandwidth, coding rate 4/5, sync word 0x34, explicit header, CRC on, 12-symbol preamble. These must match the transmitter.
