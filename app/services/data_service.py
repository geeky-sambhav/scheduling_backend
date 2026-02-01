import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Thread locks for file operations
_file_locks: Dict[str, Lock] = {}


def _get_lock(file_path: str) -> Lock:
    """Get or create a lock for a specific file path."""
    if file_path not in _file_locks:
        _file_locks[file_path] = Lock()
    return _file_locks[file_path]


def read_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Read data from a JSON file with thread safety.


    """
    lock = _get_lock(str(file_path))

    with lock:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}, returning empty list")
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Read {len(data)} records from {file_path}")
            return data


def write_json_file(file_path: Path, data: List[Dict[str, Any]]) -> None:
    """
    Write data to a JSON file with thread safety.
    """
    lock = _get_lock(str(file_path))

    with lock:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Wrote {len(data)} records to {file_path}")
