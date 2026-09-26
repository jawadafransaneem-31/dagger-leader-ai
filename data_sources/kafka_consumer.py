from __future__ import annotations
from typing import Iterator
from config.settings import get_settings


def stream() -> Iterator[dict]:
    from kafka import KafkaConsumer
    import json
    s = get_settings()
    c = KafkaConsumer(
        s.kafka_topic,
        bootstrap_servers=s.kafka_bootstrap_servers,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    for msg in c:
        yield msg.value
