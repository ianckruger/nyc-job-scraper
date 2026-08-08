from __future__ import annotations

from enum import Enum


class RemotePolicy(str, Enum):
    ONSITE = "on-site"
    HYBRID = "hybrid"
    REMOTE = "remote"
    UNKNOWN = "unknown"


class SourceType(str, Enum):
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKDAY = "workday"
    SMARTRECRUITERS = "smartrecruiters"
    WEBSCRAPE = "webscrape"
