import time, math, random

# Simulated flight profile, matched to the OpenRocket simulation of the
# rocket on an Estes D12 motor (design file QDM1-3.ork).
APOGEE_ALTITUDE = 215.5   # metres - simulated apogee
TIME_TO_APOGEE = 6.7      # seconds from launch to apogee
DESCENT_RATE = 8.7        # m/s under parachute (simulated ground-hit velocity)
GRAVITY = 9.81            # m/s^2
# After apogee the rocket speeds up under gravity until it reaches DESCENT_RATE
RAMP_TIME = DESCENT_RATE / GRAVITY
RAMP_DROP = 0.5 * GRAVITY * RAMP_TIME ** 2
FLIGHT_DURATION = TIME_TO_APOGEE + RAMP_TIME + (APOGEE_ALTITUDE - RAMP_DROP) / DESCENT_RATE  # about 31.9 s


def flight_profile(elapsed):
    """Return (altitude_m, vertical_velocity_mps) at `elapsed` seconds after launch.

    Ascent: velocity falls linearly from its launch value to zero at apogee,
    which gives a parabolic climb to APOGEE_ALTITUDE.
    Descent: the rocket accelerates under gravity until it reaches
    DESCENT_RATE, then falls at that steady rate under parachute.
    After landing (or before launch) both values are 0.
    """
    if elapsed < 0 or elapsed >= FLIGHT_DURATION:
        return 0.0, 0.0
    if elapsed <= TIME_TO_APOGEE:
        remaining = 1 - elapsed / TIME_TO_APOGEE
        altitude = APOGEE_ALTITUDE * (1 - remaining ** 2)
        velocity = 2 * APOGEE_ALTITUDE / TIME_TO_APOGEE * remaining
        return altitude, velocity
    falling = elapsed - TIME_TO_APOGEE
    ramp = min(falling, RAMP_TIME)
    altitude = APOGEE_ALTITUDE - 0.5 * GRAVITY * ramp ** 2 - DESCENT_RATE * (falling - ramp)
    return max(0.0, altitude), -GRAVITY * ramp


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
            altitude, vv = flight_profile(t - launch_t)
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
