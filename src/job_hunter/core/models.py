from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

@dataclass
class JobPosting:
    id: Optional[str] = None
    source: str = ""
    source_job_id: Optional[str] = None

    title: str =""
    company: str = ""
    location: Optional[str] = None
    remote_policy: Optional[str] = None # this can be on-site hybrid or remote or simply unknown

    job_url: str=""
    apply_url: Optional[str] = None
    description: str = ""
    posted_at: Optional[datetime]= None
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: Optional[str] = None # useless for now since im rendering this towards NYC but for the future if I use this again, I wanna work in the UK

    employment_type: Optional[str] = None # filter out full time, salary,contract, whatever
    seniority: Optional[str] = None # entry leverl, junior, midlevel
    tags: list[str] = field(default_factory=list)
    score: float = 0.0
    is_swe_relevant: bool = False
    is_nyc_relevant: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)