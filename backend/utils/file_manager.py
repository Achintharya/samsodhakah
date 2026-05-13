"""
Thread-safe atomic file operations with cross-platform locking.
Preserved and refactored from Akṣarajña backend AtomicFileManager.
"""

from __future__ import annotations

import os
import time
import json
import shutil
import tempfile
import threading
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Cross-platform file locking
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False
    try:
        import msvcrt
        HAS_MSVCRT = True
    except ImportError:
        HAS_MSVCRT = False


class AtomicFileManager:
    """Thread-safe atomic file operations with proper locking and versioning."""

    def __init__(self, base_path: str | Path = "./runtime/data") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.lock_dir = self.base_path / ".locks"
        self.lock_dir.mkdir(exist_ok=True)
        self.backup_dir = self.base_path / ".backups"
        self.backup_dir.mkdir(exist_ok=True)
        self._thread_lock = threading.Lock()

    def _lock_path(self, filename: str) -> Path:
        return self.lock_dir / f"{filename}.lock"

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        if not file_path.exists():
            return None
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        # Keep only last 10 backups
        for old in sorted(self.backup_dir.glob(f"{file_path.stem}_*{file_path.suffix}"))[:-10]:
            old.unlink()
        return backup_path

    def _acquire_lock(self, lock_handle) -> None:
        if HAS_FCNTL:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        elif HAS_MSVCRT:
            msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)

    def _release_lock(self, lock_handle) -> None:
        if HAS_FCNTL:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        elif HAS_MSVCRT:
            msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)

    def write(self, filename: str, content: str, encoding: str = "utf-8") -> None:
        """Atomically write content to a file."""
        file_path = self.base_path / filename
        lock_file = self._lock_path(filename)

        with self._thread_lock:
            with open(lock_file, "w") as lock:
                try:
                    self._acquire_lock(lock)
                except (BlockingIOError, OSError):
                    for attempt in range(5):
                        time.sleep(0.1 * (2**attempt))
                        try:
                            self._acquire_lock(lock)
                            break
                        except (BlockingIOError, OSError):
                            continue

                self._create_backup(file_path)

                with tempfile.NamedTemporaryFile(
                    mode="w", encoding=encoding, dir=file_path.parent,
                    delete=False, suffix=f".tmp_{filename}"
                ) as temp:
                    temp_file = Path(temp.name)
                    temp.write(content)
                    temp.flush()
                    if hasattr(os, "fsync"):
                        os.fsync(temp.fileno())

                shutil.move(str(temp_file), str(file_path))

        if lock_file.exists():
            lock_file.unlink()

    def append(self, filename: str, content: str, encoding: str = "utf-8") -> None:
        """Atomically append content to a file."""
        file_path = self.base_path / filename
        existing = file_path.read_text(encoding) if file_path.exists() else ""
        self.write(filename, existing + content, encoding)

    def read(self, filename: str, encoding: str = "utf-8") -> str:
        """Read content from a file."""
        file_path = self.base_path / filename
        if file_path.exists():
            return file_path.read_text(encoding)
        return ""

    def write_json(self, filename: str, data: dict | list) -> None:
        """Atomically write JSON data to a file."""
        self.write(filename, json.dumps(data, indent=2, ensure_ascii=False))

    def read_json(self, filename: str) -> Optional[dict | list]:
        """Read JSON data from a file."""
        content = self.read(filename)
        if content:
            return json.loads(content)
        return None


# Global instance
file_manager = AtomicFileManager()