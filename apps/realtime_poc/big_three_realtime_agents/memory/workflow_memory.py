"""
Workflow memory - Execution history and task tracking.

Stores workflow execution records for learning and debugging.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..exceptions import ValidationError, MemoryStoreError

logger = logging.getLogger(__name__)


class WorkflowMemory:
    """
    Workflow execution history storage.

    Tracks workflow executions for learning and pattern analysis.

    Example:
        >>> workflow_mem = WorkflowMemory(storage_dir="memory/workflows")
        >>> workflow_mem.store_execution("task_123", execution_data)
        >>> recent = workflow_mem.get_recent(limit=5)
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize workflow memory.

        Args:
            storage_dir: Directory for workflow storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.storage_dir / "index.json"
        self._index: List[Dict[str, Any]] = self._load_index()

    def _sanitize_execution_id(self, execution_id: str) -> str:
        """
        Sanitize execution_id to prevent path traversal attacks.

        Args:
            execution_id: Raw execution identifier

        Returns:
            Sanitized execution_id

        Raises:
            ValidationError: If execution_id is invalid or dangerous
        """
        # Only allow alphanumeric, underscore, hyphen
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '', execution_id)

        if not safe_id:
            raise ValidationError(
                f"Invalid execution_id: '{execution_id}' - must contain alphanumeric characters"
            )

        if safe_id != execution_id:
            raise ValidationError(
                f"Invalid execution_id: '{execution_id}' contains forbidden characters. "
                f"Allowed: alphanumeric, underscore, hyphen"
            )

        # Prevent path traversal attempts
        if '..' in execution_id or '/' in execution_id or '\\' in execution_id:
            raise ValidationError(f"Path traversal detected in execution_id: '{execution_id}'")

        return safe_id

    def store_execution(
        self,
        execution_id: str,
        execution_data: Dict[str, Any]
    ) -> None:
        """
        Store workflow execution record.

        Args:
            execution_id: Unique execution identifier (alphanumeric, underscore, hyphen only)
            execution_data: Execution details and results

        Raises:
            ValidationError: If execution_id contains invalid characters
            MemoryStoreError: If storage operation fails
        """
        # Sanitize execution_id to prevent path traversal
        safe_id = self._sanitize_execution_id(execution_id)

        # Add timestamp
        execution_data["stored_at"] = datetime.now().isoformat()
        execution_data["execution_id"] = safe_id

        # Write execution file
        exec_file = self.storage_dir / f"{safe_id}.json"

        # Verify path stays within storage_dir (defense in depth)
        try:
            resolved_path = exec_file.resolve()
            if not resolved_path.is_relative_to(self.storage_dir.resolve()):
                raise ValidationError(f"Path traversal attempt detected: {execution_id}")
        except ValueError as e:
            raise ValidationError(f"Invalid path: {execution_id}") from e

        try:
            exec_file.write_text(json.dumps(execution_data, indent=2))
        except Exception as exc:
            logger.error(f"Failed to store execution {safe_id}: {exc}")
            raise MemoryStoreError(f"Cannot store execution: {exc}") from exc

        # Update index
        self._index.append({
            "execution_id": safe_id,
            "timestamp": execution_data["stored_at"],
            "task": execution_data.get("task", "")[:100],
            "status": execution_data.get("status", "unknown"),
        })
        self._save_index()

        logger.info(f"Stored workflow execution: {safe_id}")

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve workflow execution record.

        Args:
            execution_id: Execution identifier

        Returns:
            Execution data or None if not found

        Raises:
            ValidationError: If execution_id is invalid
        """
        # Sanitize execution_id
        safe_id = self._sanitize_execution_id(execution_id)
        exec_file = self.storage_dir / f"{safe_id}.json"

        # Verify path (defense in depth)
        try:
            if not exec_file.resolve().is_relative_to(self.storage_dir.resolve()):
                raise ValidationError(f"Path traversal attempt: {execution_id}")
        except ValueError as e:
            raise ValidationError(f"Invalid path: {execution_id}") from e

        if not exec_file.exists():
            return None

        try:
            return json.loads(exec_file.read_text())
        except Exception as exc:
            logger.error(f"Failed to load execution {safe_id}: {exc}")
            return None

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow executions."""
        return self._index[-limit:] if self._index else []

    def count(self) -> int:
        """Get total number of stored workflows."""
        return len(self._index)

    def search_by_task(self, keyword: str) -> List[Dict[str, Any]]:
        """Search workflows by task keyword."""
        keyword_lower = keyword.lower()
        return [
            entry for entry in self._index
            if keyword_lower in entry.get("task", "").lower()
        ]

    def _load_index(self) -> List[Dict[str, Any]]:
        """Load workflow index."""
        if not self._index_file.exists():
            return []

        try:
            return json.loads(self._index_file.read_text())
        except Exception as exc:
            logger.error(f"Failed to load workflow index: {exc}")
            return []

    def _save_index(self) -> None:
        """Save workflow index."""
        try:
            self._index_file.write_text(json.dumps(self._index, indent=2))
        except Exception as exc:
            logger.error(f"Failed to save workflow index: {exc}")
