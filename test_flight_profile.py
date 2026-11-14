"""Self-test for the simulated flight profile in fake_telemetry.py."""
from fake_telemetry import (
    flight_profile, APOGEE_ALTITUDE, TIME_TO_APOGEE, DESCENT_RATE, FLIGHT_DURATION,
)

# Before launch and after landing the rocket is on the ground and still
assert flight_profile(-1) == (0.0, 0.0)
assert flight_profile(FLIGHT_DURATION) == (0.0, 0.0)
assert flight_profile(FLIGHT_DURATION + 60) == (0.0, 0.0)

# Apogee: peak altitude reached with zero vertical velocity
altitude, velocity = flight_profile(TIME_TO_APOGEE)
assert abs(altitude - APOGEE_ALTITUDE) < 0.01
assert abs(velocity) < 0.01

# Altitude never exceeds apogee and never goes negative at any 100 ms step
steps = [i / 10 for i in range(int(FLIGHT_DURATION * 10) + 20)]
altitudes = [flight_profile(t)[0] for t in steps]
assert max(altitudes) <= APOGEE_ALTITUDE + 0.01
assert min(altitudes) >= 0.0

# Ascent has positive velocity, descent is a steady parachute fall
assert flight_profile(1.0)[1] > 0
assert flight_profile(TIME_TO_APOGEE + 5)[1] == -DESCENT_RATE

print(f"Peak altitude {max(altitudes):.1f} m, flight time {FLIGHT_DURATION:.1f} s")
print("PASSED: simulated flight profile is realistic and returns to rest.")
