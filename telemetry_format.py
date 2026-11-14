FIELD_NAMES = [
    "time_ms", "accel_x", "accel_y", "accel_z",
    "gyro_x", "gyro_y", "gyro_z",
    "temp_c", "pressure_hpa", "altitude_m", "vertical_velocity_mps",
    "roll_deg", "pitch_deg", "yaw_deg",
    "launched", "apogee",
]

# time_ms, launched, and apogee are whole numbers - everything else is a decimal
INT_FIELDS = {"time_ms", "launched", "apogee"}

def encode_packet(values: dict) -> str:
    """Turn a telemetry dict into one CSV text line, e.g. "12345,0.1,-0.2,...,1,0" """
    parts = [str(values[name]) for name in FIELD_NAMES]
    return ",".join(parts)

def decode_packet(line) -> dict:
    """Turn one CSV text line (str or bytes) back into a telemetry dict."""
    if isinstance(line, bytes):
        line = line.decode("utf-8", errors="replace")

    parts = line.strip().split(",")
    if len(parts) != len(FIELD_NAMES):
        raise ValueError(f"Expected {len(FIELD_NAMES)} values, got {len(parts)}: {line!r}")

    values = {}
    for name, part in zip(FIELD_NAMES, parts):
        values[name] = int(float(part)) if name in INT_FIELDS else float(part)
    return values
