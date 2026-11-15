"""SQLite Checkpoint Persistence & Thread Recovery Engine."""
import sqlite3
from typing import Any, Dict, List, Optional
from langgraph.checkpoint.sqlite import SqliteSaver
from app.ai.config import ai_config
from app.core.logging import logger


class CheckpointManager:
    """Manages LangGraph SQLite checkpoint saver and state thread retrieval."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or ai_config.CHECKPOINTS_DB_PATH
        self._conn: Optional[sqlite3.Connection] = None
        self._saver: Optional[SqliteSaver] = None

    def get_saver(self) -> SqliteSaver:
        """Returns or creates the SQLite checkpointer connection."""
        if self._saver is None:
            # check_same_thread=False allows sharing across async loop invocations
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._saver = SqliteSaver(self._conn)
            # Setup tables if not existing
            self._saver.setup()
            logger.info(f"LangGraph SQLite Checkpointer initialized at '{self.db_path}'")
        return self._saver

    def get_thread_state(self, compiled_graph: Any, thread_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves latest state snapshot for a given thread_id."""
        config = {"configurable": {"thread_id": thread_id}}
        try:
            state_snapshot = compiled_graph.get_state(config)
            if state_snapshot and state_snapshot.values:
                return {
                    "thread_id": thread_id,
                    "values": state_snapshot.values,
                    "next": state_snapshot.next,
                    "config": state_snapshot.config,
                    "metadata": state_snapshot.metadata,
                }
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch state for thread {thread_id}: {e}")
            return None

    def close(self):
        """Close database connection cleanly."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._saver = None


checkpoint_manager = CheckpointManager()

