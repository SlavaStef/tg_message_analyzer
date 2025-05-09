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
    TARGET = os.environ['TARGET']
except KeyError:
    raise RuntimeError("Missing required environment variable: TARGET")

DB_PATH = os.environ.get('DB_PATH', 'monitor.db')