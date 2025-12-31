import os


NATS_URL = os.environ.get("NATS_URL", "nats://localhost:4222")

NATS_CONSUMER = {
    "connect_args": {
        "servers": [NATS_URL],
        "allow_reconnect": True,
        "max_reconnect_attempts": 5,
        "reconnect_time_wait": 1,
        "connect_timeout": 10,
    },
}
