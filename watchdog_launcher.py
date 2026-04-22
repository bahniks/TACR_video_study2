#! python3

import os
import sys
import json
import time
import subprocess
from datetime import datetime


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_SCRIPT = os.path.join(PROJECT_ROOT, "experiment.py")
HEARTBEAT_FILE = os.path.join(PROJECT_ROOT, "temp_heartbeat.json")
LOG_FILE = os.path.join(PROJECT_ROOT, "watchdog.log")

POLL_INTERVAL_S = 2.0
STALE_TIMEOUT_S = 30.0
STARTUP_GRACE_S = 45.0
MAX_RESTARTS = 20


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message):
    line = f"[{now_text()}] {message}"
    print(line)
    with open(LOG_FILE, mode="a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_heartbeat_payload():
    if not os.path.exists(HEARTBEAT_FILE):
        return None

    try:
        with open(HEARTBEAT_FILE, mode="r", encoding="utf-8") as f:
            payload = json.load(f)
        ts = payload.get("timestamp")
        pid = payload.get("pid")
        state = payload.get("state", "")
        if isinstance(ts, (int, float)) and isinstance(pid, int):
            return {
                "timestamp": float(ts),
                "pid": pid,
                "state": state,
            }
    except Exception:
        return None

    return None


def start_experiment():
    # Remove stale heartbeat so a new process must publish a fresh one.
    try:
        if os.path.exists(HEARTBEAT_FILE):
            os.remove(HEARTBEAT_FILE)
    except Exception:
        pass

    cmd = [sys.executable, EXPERIMENT_SCRIPT]
    return subprocess.Popen(cmd, cwd=PROJECT_ROOT)


def terminate_process(proc):
    if proc.poll() is not None:
        return

    try:
        proc.terminate()
        proc.wait(timeout=8)
    except Exception:
        try:
            proc.kill()
            proc.wait(timeout=5)
        except Exception:
            pass


def main():
    if not os.path.exists(EXPERIMENT_SCRIPT):
        print("experiment.py not found in project root")
        sys.exit(1)

    restart_count = 0

    log("Starting watchdog launcher")
    proc = start_experiment()
    launch_time = time.time()
    log(f"Started experiment PID={proc.pid}")

    while True:
        exit_code = proc.poll()
        if exit_code is not None:
            if exit_code == 0:
                log("Experiment exited normally. Watchdog stopping.")
                return

            restart_count += 1
            if restart_count > MAX_RESTARTS:
                log(f"Experiment exited with code {exit_code}; max restarts exceeded. Stopping watchdog.")
                return

            log(f"Experiment exited with code {exit_code}; restarting ({restart_count}/{MAX_RESTARTS}).")
            proc = start_experiment()
            launch_time = time.time()
            log(f"Started experiment PID={proc.pid}")
            time.sleep(POLL_INTERVAL_S)
            continue

        now = time.time()
        heartbeat = read_heartbeat_payload()

        if heartbeat is None:
            if now - launch_time > STARTUP_GRACE_S:
                restart_count += 1
                log(f"No heartbeat after {STARTUP_GRACE_S:.0f}s; restarting PID={proc.pid} ({restart_count}/{MAX_RESTARTS}).")
                terminate_process(proc)

                if restart_count > MAX_RESTARTS:
                    log("Max restarts exceeded while waiting for heartbeat. Stopping watchdog.")
                    return

                proc = start_experiment()
                launch_time = time.time()
                log(f"Started experiment PID={proc.pid}")
            time.sleep(POLL_INTERVAL_S)
            continue

        if heartbeat["pid"] != proc.pid:
            # Ignore heartbeat from previous run/restarted process.
            time.sleep(POLL_INTERVAL_S)
            continue

        if heartbeat["timestamp"] < launch_time:
            # Ignore heartbeat that predates current child launch.
            time.sleep(POLL_INTERVAL_S)
            continue

        if heartbeat.get("state") in ("stopping", "restarting"):
            # Process is shutting down by design; wait for next child heartbeat.
            time.sleep(POLL_INTERVAL_S)
            continue

        if now - heartbeat["timestamp"] > STALE_TIMEOUT_S:
            restart_count += 1
            age = now - heartbeat["timestamp"]
            log(f"Heartbeat stale ({age:.1f}s > {STALE_TIMEOUT_S:.1f}s); restarting PID={proc.pid} ({restart_count}/{MAX_RESTARTS}).")
            terminate_process(proc)

            if restart_count > MAX_RESTARTS:
                log("Max restarts exceeded due to stale heartbeat. Stopping watchdog.")
                return

            proc = start_experiment()
            launch_time = time.time()
            log(f"Started experiment PID={proc.pid}")

        time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    main()
