"""TR-002 run: start app.py --simulate, hard-kill it mid-write, analyse the CSV, test decode error handling."""
import subprocess, sys, time, os, csv, signal, json, platform, statistics
repo, home, py = sys.argv[1], sys.argv[2], sys.argv[3]
env = dict(os.environ, HOME=home)
log = os.path.join(home, "rocket-ground-station", "telemetry_log.csv")
t0 = time.time()
p = subprocess.Popen([py, os.path.abspath("logging_harness.py"), repo], cwd=repo, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(60.0)
p.send_signal(signal.SIGKILL)   # abrupt stop, no clean shutdown
p.wait(); run_s = time.time() - t0
raw = open(log, newline="").read()
lines = raw.split("\n")
rows = list(csv.DictReader(open(log, newline="")))
hdr = lines[0].strip().split(",")
ts = [int(r["time_ms"]) for r in rows]
gaps = [b - a for a, b in zip(ts, ts[1:])]
complete = sum(1 for r in rows if len(r) == 17 and all(v not in (None, "") for v in r.values()))
states_ok = max(float(r["altitude_m"]) for r in rows)
res = {
 "python": platform.python_version(), "platform": platform.platform(), "run_seconds": round(run_s, 1),
 "header_fields": len(hdr), "rows": len(rows), "complete_rows": complete,
 "file_ends_with_newline": raw.endswith("\n"),
 "span_s": round((ts[-1] - ts[0]) / 1000, 2), "rate_hz": round((len(ts) - 1) / ((ts[-1] - ts[0]) / 1000), 3),
 "gap_mean_ms": round(statistics.mean(gaps), 2), "gap_min_ms": min(gaps), "gap_max_ms": max(gaps),
 "gaps_over_150ms": sum(g > 150 for g in gaps), "max_altitude_m": round(states_ok, 1), "last_line_complete": len(lines[-2].split(","))==17 if raw.endswith("\n") else len(lines[-1].split(","))==17,
 "apogee_flag_rows": sum(r["apogee"] == "1" for r in rows), "launched_flag_rows": sum(r["launched"] == "1" for r in rows),
}
sys.path.insert(0, repo)
from telemetry_format import decode_packet, encode_packet, FIELD_NAMES
good = "12345,0.1,-0.2,9.8,1.0,-1.0,0.5,21.4,1005.2,87.3,12.6,2.1,-1.4,178.9,1,0"
cases = [
 ("D1 valid text packet", good, "decoded"),
 ("D2 valid bytes packet with CR/LF", (good + "\r\n").encode(), "decoded"),
 ("D3 15 fields (one missing)", ",".join(good.split(",")[:-1]), "ValueError"),
 ("D4 17 fields (one extra)", good + ",5", "ValueError"),
 ("D5 non-numeric field", good.replace("9.8", "abc"), "ValueError"),
 ("D6 empty packet", "", "ValueError"),
 ("D7 corrupted bytes", b"\xff\xfe\x00garbage", "ValueError"),
 ("D8 empty field", good.replace(",21.4,", ",,"), "ValueError"),
]
out = []
for name, pkt, expect in cases:
    try:
        d = decode_packet(pkt); got = "decoded" if len(d) == 16 else "bad"
    except ValueError: got = "ValueError"
    except Exception as e: got = type(e).__name__
    out.append([name, expect, got, "PASS" if got == expect else "FAIL"])
d = decode_packet(good); rt = decode_packet(encode_packet(d)) == d
out.append(["D9 encode/decode round trip", "identical", "identical" if rt else "different", "PASS" if rt else "FAIL"])
res["decode_cases"] = out
json.dump(res, open("tr002_result.json", "w"), indent=1); print(json.dumps(res, indent=1))
