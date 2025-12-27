"""
Mock Cloud Receiver for testing.

A simple Flask app that receives encrypted envelopes and stores them.
Used for integration testing and local development.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List

from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage for received envelopes
envelopes: List[dict] = []

# File storage path
STORAGE_PATH = Path(os.environ.get("STORAGE_PATH", "/data/envelopes"))


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "envelopes_received": len(envelopes),
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/envelopes", methods=["POST"])
def receive_envelope():
    """Receive an encrypted envelope."""
    try:
        envelope = request.get_json()
        
        # Validate required fields
        required = ["version", "table", "operation", "encrypted_data", "encrypted_key"]
        for field in required:
            if field not in envelope:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        # Add metadata
        envelope["_received_at"] = datetime.utcnow().isoformat()
        envelope["_id"] = len(envelopes) + 1
        
        # Store in memory
        envelopes.append(envelope)
        
        # Persist to file (optional)
        if STORAGE_PATH.exists():
            file_path = STORAGE_PATH / f"envelope_{envelope['_id']}.json"
            file_path.write_text(json.dumps(envelope, indent=2))
        
        logger.info(
            f"Received envelope #{envelope['_id']}: "
            f"{envelope['table']}/{envelope['operation']}"
        )
        
        return jsonify({
            "status": "accepted",
            "id": envelope["_id"]
        }), 201
    
    except Exception as e:
        logger.error(f"Error receiving envelope: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/envelopes", methods=["GET"])
def list_envelopes():
    """List all received envelopes (metadata only)."""
    return jsonify({
        "count": len(envelopes),
        "envelopes": [
            {
                "id": e["_id"],
                "table": e["table"],
                "operation": e["operation"],
                "received_at": e["_received_at"],
                "key_id": e.get("key_id", "unknown")
            }
            for e in envelopes
        ]
    })


@app.route("/envelopes/<int:envelope_id>", methods=["GET"])
def get_envelope(envelope_id: int):
    """Get a specific envelope by ID."""
    for e in envelopes:
        if e["_id"] == envelope_id:
            return jsonify(e)
    return jsonify({"error": "Not found"}), 404


@app.route("/envelopes", methods=["DELETE"])
def clear_envelopes():
    """Clear all stored envelopes (for testing)."""
    global envelopes
    count = len(envelopes)
    envelopes = []
    logger.info(f"Cleared {count} envelopes")
    return jsonify({"status": "cleared", "count": count})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Mock Cloud Receiver on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
