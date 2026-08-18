from datetime import datetime

def format_datetime(dt: datetime) -> str:
    return dt.isoformat() if dt else None
