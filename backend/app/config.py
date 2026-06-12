import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 3001))

# ---------------------------------------------------------------------------
# Database: SQLite (default, lightweight) or MySQL (production)
# Set DATABASE_TYPE=mysql and configure MYSQL_* vars to use MySQL.
# ---------------------------------------------------------------------------
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()

if DATABASE_TYPE == "mysql":
    DB_CONFIG = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "trade_flow"),
    }
    DATABASE_URL = (
        f"mysql+pymysql://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        "?charset=utf8mb4"
    )
else:
    # SQLite — lightweight default, no external DB needed
    db_path = os.getenv(
        "SQLITE_PATH",
        str(Path(__file__).resolve().parent.parent.parent / "data" / "trade_flow.db"),
    )
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    DATABASE_URL = f"sqlite:///{db_path}"
