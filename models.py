from dataclasses import dataclass

@dataclass
class Job:
    title: str
    location: str
    posted_date: str
    description: str
    url: str
    score: int = 0