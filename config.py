import os
from dotenv import load_dotenv

load_dotenv()

try:
    API_ID = int(os.environ['API_ID'])
    API_HASH = os.environ['API_HASH']
except KeyError as e:
    raise RuntimeError(f"Missing required environment variable: {e}")

SESSION_NAME = os.environ.get('SESSION_NAME', 'session_monitor')

try:
    _raw = os.environ['TARGET']
except KeyError:
    raise RuntimeError("Missing required environment variable: TARGET")

if _raw.lstrip('-').isdigit():
    TARGET = int(_raw)
else:
    TARGET = _raw

DB_PATH = os.environ.get('DB_PATH', 'monitor.db')