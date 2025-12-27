"""
PostgreSQL Change Data Capture (CDC) listener.

Uses PostgreSQL's LISTEN/NOTIFY for real-time change detection.
Triggers are set up on monitored tables to send notifications
when rows are inserted, updated, or deleted.
"""

import json
import logging
import select
from dataclasses import dataclass
from typing import Callable, Optional

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .config import Config


logger = logging.getLogger(__name__)


@dataclass
class ChangeEvent:
    """Represents a database change event."""
    table: str
    operation: str  # INSERT, UPDATE, DELETE
    data: dict
    old_data: Optional[dict] = None  # For UPDATE/DELETE


class PostgresListener:
    """
    Listens for PostgreSQL NOTIFY events on a channel.
    
    The database must have triggers set up to send notifications.
    See setup_triggers() for the required SQL.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self._conn: Optional[psycopg2.extensions.connection] = None
        self._running = False
    
    def connect(self) -> None:
        """Establish connection to PostgreSQL."""
        self._conn = psycopg2.connect(self.config.database_url)
        self._conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = self._conn.cursor()
        cursor.execute(f"LISTEN {self.config.listen_channel};")
        cursor.close()
        
        logger.info(f"Listening on channel: {self.config.listen_channel}")
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
        logger.info("Disconnected from PostgreSQL")
    
    def listen(
        self,
        callback: Callable[[ChangeEvent], None],
        timeout: float = 5.0
    ) -> None:
        """
        Start listening for notifications.
        
        Args:
            callback: Function to call for each change event
            timeout: Seconds to wait between poll cycles
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")
        
        self._running = True
        logger.info("Starting listener loop...")
        
        while self._running:
            # Wait for notification with timeout
            if select.select([self._conn], [], [], timeout) == ([], [], []):
                # Timeout - no notification, continue loop
                continue
            
            # Process any pending notifications
            self._conn.poll()
            while self._conn.notifies:
                notify = self._conn.notifies.pop(0)
                try:
                    event = self._parse_notification(notify.payload)
                    if event:
                        callback(event)
                except Exception as e:
                    logger.error(f"Error processing notification: {e}")
    
    def stop(self) -> None:
        """Stop the listener loop."""
        self._running = False
        logger.info("Stopping listener...")
    
    def _parse_notification(self, payload: str) -> Optional[ChangeEvent]:
        """Parse a NOTIFY payload into a ChangeEvent."""
        try:
            data = json.loads(payload)
            return ChangeEvent(
                table=data.get("table", "unknown"),
                operation=data.get("operation", "UNKNOWN"),
                data=data.get("data", {}),
                old_data=data.get("old_data"),
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in notification: {e}")
            return None


def get_trigger_sql(table_name: str, channel: str = "nis2_changes") -> str:
    """
    Generate SQL to create a trigger for CDC on a table.
    
    Args:
        table_name: Name of the table to monitor
        channel: NOTIFY channel to use
    
    Returns:
        SQL statements to create function and trigger
    """
    function_name = f"notify_{table_name}_changes"
    trigger_name = f"trg_{table_name}_notify"
    
    return f"""
-- Function to send notification on changes
CREATE OR REPLACE FUNCTION {function_name}()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    IF TG_OP = 'DELETE' THEN
        payload = json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'data', row_to_json(OLD),
            'old_data', NULL
        );
    ELSIF TG_OP = 'UPDATE' THEN
        payload = json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'data', row_to_json(NEW),
            'old_data', row_to_json(OLD)
        );
    ELSE
        payload = json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'data', row_to_json(NEW),
            'old_data', NULL
        );
    END IF;
    
    PERFORM pg_notify('{channel}', payload::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function
DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};
CREATE TRIGGER {trigger_name}
AFTER INSERT OR UPDATE OR DELETE ON {table_name}
FOR EACH ROW EXECUTE FUNCTION {function_name}();
"""
