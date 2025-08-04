from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CategoryDTO(BaseModel):
    name: str
    slug: str


class CompetitionDTO(BaseModel):
    id: str
    short: str
    title: str


class RivalDTO(BaseModel):
    name: str
    name_eng: str
    short_name: str
    term: str
    stadium: Optional[str] = None
    city: Optional[str] = None


class EventDTO(BaseModel):
    competition: CompetitionDTO
    rival: RivalDTO
    place: str
    score: Optional[str] = None
    stats: list
    eventId: str
    date: datetime
