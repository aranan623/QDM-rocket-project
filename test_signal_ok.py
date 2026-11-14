"""Self-test for the SIGNAL OK launch hold in link_monitor.py."""
from link_monitor import LinkMonitor, WINDOW_S


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


clock = FakeClock()
link = LinkMonitor(clock)

# 1. No packets yet: hold
s = link.status()
assert not s["signal_ok"] and s["launch_hold"] == "HOLD"

# 2. Packets every 100 ms for 2 s (10 Hz): signal OK
for _ in range(20):
    clock.t += 0.1
    link.good_packet()
s = link.status()
assert s["signal_ok"], s
assert s["launch_hold"] == "CLEAR TO START COUNTDOWN"
assert 9.0 <= s["packet_rate_hz"] <= 10.5

# 3. Weak link, one packet every 400 ms (2.5 Hz): hold
weak = LinkMonitor(clock)
for _ in range(10):
    clock.t += 0.4
    weak.good_packet()
assert not weak.status()["signal_ok"]

# 4. Link drops: 1.5 s with no packets turns a good link back to hold
clock.t += 1.5
assert not link.status()["signal_ok"]

# 5. After the window has passed with no packets, the rate falls to zero
clock.t += WINDOW_S
assert link.status()["packet_rate_hz"] == 0.0

# 6. Bad packets are counted but never count towards SIGNAL OK
link.bad_packet(); link.bad_packet()
assert link.status()["bad_packets"] == 2
assert not link.status()["signal_ok"]

print("PASSED: SIGNAL OK only when valid packets arrive at 5 Hz or more and the newest is under 1 s old.")
