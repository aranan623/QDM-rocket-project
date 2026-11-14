import time, math, random

FLIGHT_DURATION = 20  # seconds from launch to landing - matches the flight profile below

def generate_fake_telemetry():
    """Yields one telemetry dict every 100ms, forever - simulates a flight, then sits landed."""
    t0 = time.time()
    launched = 0
    apogee = 0
    launch_t = 0

    while True:
        t = time.time() - t0
        time_ms = int(t * 1000)

        if t > 2 and not launched:
            launched = 1
            launch_t = t

        if launched:
            elapsed = t - launch_t
            if elapsed >= FLIGHT_DURATION:
                altitude = 0.0
                vv = 0.0
            else:
                altitude = max(0.0, 300 * elapsed - 15 * elapsed ** 2)
                vv = 300 - 30 * elapsed
            if vv < 0 and not apogee:
                apogee = 1
        else:
            altitude = 0.0
            vv = 0.0

        yield {
            "time_ms": time_ms,
            "accel_x": random.uniform(-1, 1),
            "accel_y": random.uniform(-1, 1),
            "accel_z": 9.8 + (random.uniform(-2, 20) if launched else 0),
            "gyro_x": random.uniform(-5, 5),
            "gyro_y": random.uniform(-5, 5),
            "gyro_z": random.uniform(-5, 5),
            "temp_c": 22.0 - altitude * 0.006,
            "pressure_hpa": 1013.25 * (1 - altitude / 44330) ** 5.255,
            "altitude_m": altitude,
            "vertical_velocity_mps": vv,
            "roll_deg": 5 * math.sin(t),
            "pitch_deg": 5 * math.cos(t),
            "yaw_deg": (t * 3) % 360,
            "launched": launched,
            "apogee": apogee,
        }

        time.sleep(0.1)

if __name__ == "__main__":
    print("Generating fake telemetry - Ctrl+C to stop.")
    try:
        for packet in generate_fake_telemetry():
            print(packet)
    except KeyboardInterrupt:
        pass
