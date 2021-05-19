from enum import Enum
from pydantic import BaseModel
from typing import List
from typing import Optional


class RetentionPolicy(str, Enum):
    limits = "limits"
    interest = "interest"
    workqueue = "workqueue"


class Storage(str, Enum):
    file = "file"
    memory = "memory"


class StreamConfig(BaseModel):
    retention: RetentionPolicy = RetentionPolicy.limits
    storage: Storage = Storage.memory
    subjects: List[str] = []
    name: str
    max_consumers: int = -1
    max_msgs: int = -1
    max_bytes: int = -1
    max_age: int = int(24 * 365 * 3.6e12)  # nanoseconds
    duplicate_window: int = int(2 * 6e10)  # nanoseconds
    max_msg_size: int = -1
    replicas: int = 1
    ack: bool = False


class DeliverPolicy(str, Enum):
    all = "all"
    last = "last"
    new = "new"
    by_start_sequence = "by_start_sequence"
    by_start_time = "by_start_time"


class AckPolicy(str, Enum):
    none = "none"
    all = "all"
    explicit = "explicit"


class ReplayPolicy(str, Enum):
    instant = "instant"
    original = "original"


class ConsumerConfig(BaseModel):
    ack_policy: AckPolicy = AckPolicy.explicit
    ack_wait: Optional[int] = None
    deliver_policy: DeliverPolicy = DeliverPolicy.all
    deliver_subject: Optional[str] = None
    durable_name: Optional[str] = None
    filter_subject: Optional[str] = None
    flow_control: Optional[bool] = None
    idle_heartbeat: Optional[int] = None
    max_ack_pending: Optional[int] = None
    max_deliver: Optional[int] = None
    max_waiting: Optional[int] = None
    opt_start_seq: Optional[int] = None
    opt_start_time: Optional[int] = None
    rate_limit_bps: Optional[int] = None
    replay_policy: ReplayPolicy = ReplayPolicy.instant
    sample_freq: Optional[str] = None
