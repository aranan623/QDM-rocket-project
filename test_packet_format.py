from telemetry_format import encode_packet, decode_packet

sample = {
    "time_ms": 12345,
    "accel_x": 0.1, "accel_y": -0.2, "accel_z": 9.8,
    "gyro_x": 1.0, "gyro_y": -1.0, "gyro_z": 0.5,
    "temp_c": 21.4, "pressure_hpa": 1005.2,
    "altitude_m": 87.3, "vertical_velocity_mps": 12.6,
    "roll_deg": 2.1, "pitch_deg": -1.4, "yaw_deg": 178.9,
    "launched": 1, "apogee": 0,
}

line = encode_packet(sample)
print("Encoded CSV line:", line)
print("Length:", len(line), "bytes")

decoded = decode_packet(line)
print("Decoded back:", decoded)

for key in sample:
    assert abs(decoded[key] - sample[key]) < 0.001, f"Mismatch on {key}"

print("PASSED: packet format encodes and decodes correctly.")
