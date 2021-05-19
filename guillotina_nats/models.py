from pydantic import BaseModel, validator
from typing import List
from enum import Enum

class RetentionPolicy(str, Enum):
    limits = 'limits'
    interest = 'interest'
    workqueue = 'workqueue'


class Storage(str, Enum):
    file = 'file'
    memory = 'memory'


class StreamConfig(BaseModel):
    retention: RetentionPolicy = RetentionPolicy.limits
    storage: Storage = Storage.memory
    subjects: List[str] = []
    name: str
    max_consumers: int = -1
    max_msgs: int = -1
    max_bytes: int = -1
    max_age: int = int(24 * 365 * 3.6e+12)  # nanoseconds
    duplicate_window: int = int(2 * 6e+10) # nanoseconds
    max_msg_size: int = -1
    replicas: int = 1
    ack: bool = False


class DeliverPolicy(str, Enum):
    all = 'all'
    last = 'last'
    new = 'new'
    by_start_sequence = 'by_start_sequence'
    by_start_time = 'by_start_time'

class AckPolicy(str, Enum):
    none = 'none'
    all = 'all'
    explicit = 'explicit'

class ReplayPolicy(str, Enum):
    instant = 'instant'
    original = 'original'

class ConsumerConfig(BaseModel):
    ack_policy: AckPolicy = AckPolicy.explicit
    ack_wait: int = None
    deliver_policy: DeliverPolicy = DeliverPolicy.all
    deliver_subject: str = None
    durable_name: str = None
    filter_subject: str = None
    flow_control: bool = None
    idle_heartbeat:  int = None
    max_ack_pending: int = None
    max_deliver: int = None
    max_waiting: int = None
    opt_start_seq: int = None
    opt_start_time: int = None
    rate_limit_bps: int = None
    replay_policy: ReplayPolicy = ReplayPolicy.instant
    sample_freq: str = None
