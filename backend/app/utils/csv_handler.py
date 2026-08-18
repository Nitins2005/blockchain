import csv
import io
from typing import List, Dict, Any

def generate_csv(data: List[Dict[str, Any]], fieldnames: List[str] = None) -> bytes:
    if not data:
        return b""
    if not fieldnames:
        fieldnames = list(data[0].keys())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(data)
    return buffer.getvalue().encode('utf-8')

def parse_csv(content: bytes) -> List[Dict[str, Any]]:
    buffer = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(buffer)
    return [row for row in reader]
