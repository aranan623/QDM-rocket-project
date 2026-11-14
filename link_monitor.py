"""Radio link health check used as the launch hold point.

The countdown may only start when the dashboard shows SIGNAL OK. SIGNAL OK means
valid packets are arriving often enough and recently enough. Anything else is HOLD.
"""
import time
from collections import deque

WINDOW_S = 2.0       # look back over the last 2 seconds
MIN_RATE_HZ = 5.0    # need at least half of the expected 10 packets per second
MAX_AGE_S = 1.0      # and the newest packet must be less than 1 second old


class LinkMonitor:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.times = deque()
        self.bad_packets = 0

    def good_packet(self):
        self.times.append(self.clock())
        self._trim()

    def bad_packet(self):
        self.bad_packets += 1

    def _trim(self):
        now = self.clock()
        while self.times and now - self.times[0] > WINDOW_S:
            self.times.popleft()

    def status(self):
        self._trim()
        now = self.clock()
        rate = len(self.times) / WINDOW_S
        age = (now - self.times[-1]) if self.times else None
        ok = rate >= MIN_RATE_HZ and age is not None and age <= MAX_AGE_S
        return {
            "signal_ok": ok,
            "launch_hold": "CLEAR TO START COUNTDOWN" if ok else "HOLD",
            "packet_rate_hz": round(rate, 1),
            "last_packet_age_s": None if age is None else round(age, 2),
            "bad_packets": self.bad_packets,
        }
