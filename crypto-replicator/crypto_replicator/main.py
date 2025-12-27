"""
Main entry point for Crypto-Replicator service.

Coordinates the listener, encryptor, and sender components.
"""

import logging
import signal
import sys
from pathlib import Path

from .config import Config, load_config
from .crypto import HybridEncryptor
from .listener import ChangeEvent, PostgresListener
from .sender import CloudSender


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class CryptoReplicator:
    """
    Main coordinator for the Crypto-Replicator service.
    
    Listens for database changes, encrypts them, and sends to cloud.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.listener = PostgresListener(config)
        self.sender = CloudSender(config)
        self._encryptor: HybridEncryptor | None = None
        self._running = False
    
    def start(self) -> None:
        """Start the replicator service."""
        logger.info("Starting Crypto-Replicator...")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Initialize encryptor
        self._init_encryptor()
        
        # Connect to database and cloud
        self.listener.connect()
        self.sender.connect()
        
        self._running = True
        logger.info("Crypto-Replicator started successfully")
        
        # Start listening
        try:
            self.listener.listen(self._handle_change)
        except Exception as e:
            logger.error(f"Error in listener: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the replicator service."""
        if not self._running:
            return
        
        logger.info("Stopping Crypto-Replicator...")
        self._running = False
        
        self.listener.stop()
        self.listener.disconnect()
        self.sender.disconnect()
        
        logger.info("Crypto-Replicator stopped")
    
    def _init_encryptor(self) -> None:
        """Initialize the hybrid encryptor."""
        key_path = self.config.rsa_public_key_path
        
        if not key_path.exists():
            logger.warning(
                f"RSA public key not found at {key_path}. "
                "Running in demo mode with generated key."
            )
            # Generate a demo key pair for testing
            from .crypto import generate_key_pair
            private_pem, public_pem = generate_key_pair()
            
            # Save keys for testing
            demo_dir = Path("/tmp/nis2-demo-keys")
            demo_dir.mkdir(exist_ok=True)
            
            (demo_dir / "private.pem").write_bytes(private_pem)
            (demo_dir / "public.pem").write_bytes(public_pem)
            
            logger.info(f"Demo keys saved to {demo_dir}")
            
            self._encryptor = HybridEncryptor(
                public_key_pem=public_pem,
                key_id="demo-key"
            )
        else:
            self._encryptor = HybridEncryptor(
                public_key_path=key_path,
                key_id=self.config.key_id
            )
        
        logger.info(f"Encryptor initialized with key: {self._encryptor.key_id}")
    
    def _handle_change(self, event: ChangeEvent) -> None:
        """Handle a database change event."""
        logger.debug(
            f"Change detected: {event.table}/{event.operation}"
        )
        
        # Encrypt the change
        envelope = self._encryptor.encrypt(
            data=event.data,
            table=event.table,
            operation=event.operation
        )
        
        # Send to cloud
        self.sender.send(envelope)
        
        if self.config.debug:
            logger.debug(f"Encrypted and queued: {envelope.key_id}")
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)


def main() -> None:
    """Entry point for the service."""
    config = load_config()
    
    if config.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    replicator = CryptoReplicator(config)
    replicator.start()


if __name__ == "__main__":
    main()
