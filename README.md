# TACR Study

## Running with watchdog auto-restart

To enable automatic recovery from GUI freezes, start the study through:

python watchdog_launcher.py

What it does:
- launches experiment.py as a child process
- monitors temp_heartbeat.json (updated by the GUI every second)
- restarts the child process when heartbeat becomes stale
- keeps restart history in watchdog.log

Default watchdog timings are defined in watchdog_launcher.py:
- POLL_INTERVAL_S = 2
- STALE_TIMEOUT_S = 30
- STARTUP_GRACE_S = 45
 
