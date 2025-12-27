"""
Cloud API sender for encrypted envelopes.

Sends encrypted data to a cloud backup service.
Supports batching and retry logic.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config
from .crypto import EncryptedEnvelope


logger = logging.getLogger(__name__)


@dataclass
class SendResult:
    """Result of sending envelopes to cloud."""
    success: bool
    sent_count: int
    failed_count: int
    errors: List[str] = field(default_factory=list)


class CloudSender:
    """
    Sends encrypted envelopes to cloud storage API.
    
    Features:
    - Batching for efficiency
    - Automatic retry with exponential backoff
    - Dry run mode for testing
    """
    
    def __init__(self, config: Config):
        self.config = config
        self._session: Optional[requests.Session] = None
        self._buffer: List[EncryptedEnvelope] = []
        self._last_flush = datetime.now()
    
    def connect(self) -> None:
        """Initialize HTTP session with retry logic."""
        self._session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)
        
        # Set default headers
        if self.config.cloud_api_token:
            self._session.headers["Authorization"] = (
                f"Bearer {self.config.cloud_api_token}"
            )
        self._session.headers["Content-Type"] = "application/json"
        
        logger.info(f"Cloud sender initialized: {self.config.cloud_api_url}")
    
    def disconnect(self) -> None:
        """Close HTTP session and flush buffer."""
        self.flush()
        if self._session:
            self._session.close()
            self._session = None
    
    def send(self, envelope: EncryptedEnvelope) -> None:
        """
        Queue an envelope for sending.
        
        Automatically flushes when batch size is reached
        or flush interval expires.
        """
        self._buffer.append(envelope)
        
        # Check if we should flush
        should_flush = (
            len(self._buffer) >= self.config.batch_size or
            self._seconds_since_flush() >= self.config.flush_interval_seconds
        )
        
        if should_flush:
            self.flush()
    
    def flush(self) -> SendResult:
        """Send all buffered envelopes to cloud."""
        if not self._buffer:
            return SendResult(success=True, sent_count=0, failed_count=0)
        
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would send {len(self._buffer)} envelopes")
            count = len(self._buffer)
            self._buffer.clear()
            self._last_flush = datetime.now()
            return SendResult(success=True, sent_count=count, failed_count=0)
        
        if not self.config.cloud_api_url:
            logger.warning("No cloud API URL configured, discarding envelopes")
            self._buffer.clear()
            return SendResult(
                success=False,
                sent_count=0,
                failed_count=len(self._buffer),
                errors=["No cloud API URL configured"]
            )
        
        # Send envelopes
        sent = 0
        failed = 0
        errors = []
        
        for envelope in self._buffer:
            try:
                self._send_single(envelope)
                sent += 1
            except Exception as e:
                failed += 1
                errors.append(str(e))
                logger.error(f"Failed to send envelope: {e}")
        
        self._buffer.clear()
        self._last_flush = datetime.now()
        
        logger.info(f"Flush complete: {sent} sent, {failed} failed")
        return SendResult(
            success=(failed == 0),
            sent_count=sent,
            failed_count=failed,
            errors=errors
        )
    
    def _send_single(self, envelope: EncryptedEnvelope) -> None:
        """Send a single envelope to the cloud API."""
        if not self._session:
            raise RuntimeError("Not connected. Call connect() first.")
        
        response = self._session.post(
            f"{self.config.cloud_api_url}/envelopes",
            data=envelope.to_json(),
            timeout=30,
        )
        response.raise_for_status()
        
        if self.config.debug:
            logger.debug(f"Sent envelope for {envelope.table}/{envelope.operation}")
    
    def _seconds_since_flush(self) -> float:
        """Calculate seconds since last flush."""
        return (datetime.now() - self._last_flush).total_seconds()


class MockCloudReceiver:
    """
    A mock cloud receiver for testing.
    Stores envelopes in memory and can verify them.
    """
    
    def __init__(self):
        self.envelopes: List[EncryptedEnvelope] = []
    
    def receive(self, envelope: EncryptedEnvelope) -> None:
        """Store an envelope."""
        self.envelopes.append(envelope)
        logger.info(
            f"[MOCK] Received envelope: {envelope.table}/{envelope.operation}"
        )
    
    def get_all(self) -> List[EncryptedEnvelope]:
        """Get all received envelopes."""
        return self.envelopes.copy()
    
    def clear(self) -> None:
        """Clear all stored envelopes."""
        self.envelopes.clear()
