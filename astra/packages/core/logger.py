import os
import sys

# Logging Modes:
# NORMAL (INFO, WARN, ERROR)
# DEVELOPER (TRACE, DEBUG, INFO, WARN, ERROR)

LOG_LEVEL = os.environ.get("ASTRA_LOG_LEVEL", "INFO").upper()

def is_debug():
    return LOG_LEVEL in ["DEBUG", "TRACE"]

def trace(msg):
    if LOG_LEVEL == "TRACE":
        print(msg)

def debug(msg):
    if LOG_LEVEL in ["DEBUG", "TRACE"]:
        print(msg)

def info(msg):
    if LOG_LEVEL in ["INFO", "DEBUG", "TRACE"]:
        print(msg)

def warn(msg):
    if LOG_LEVEL in ["WARN", "INFO", "DEBUG", "TRACE"]:
        print(f"[WARN] {msg}")

def error(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)

def user_facing(msg):
    """Always prints for the clean user experience."""
    print(msg)
