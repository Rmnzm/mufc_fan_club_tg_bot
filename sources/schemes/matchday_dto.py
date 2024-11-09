from typing import List

from pydantic import BaseModel


class CategoryDTO(BaseModel):
    name: str
    slug: str


class TournamentDTO(BaseModel):
    name: str
    slug: str
    category: CategoryDTO


class StatusDTO(BaseModel):
    code: int
    description: str
    type: str


class NameTranslationDTO(BaseModel):
    ar: str
    ru: str


class FieldTranslationsDTO(BaseModel):
    nameTranslation: NameTranslationDTO


class TeamDTO(BaseModel):
    name: str
    slug: str
    type: int
    fieldTranslations: FieldTranslationsDTO


class EventDTO(BaseModel):
    tournament: TournamentDTO
    status: StatusDTO
    homeTeam: TeamDTO
    awayTeam: TeamDTO
    homeScore: dict
    awayScore: dict
    id: int
    startTimestamp: int


class MatchDayDTO(BaseModel):
    events: List[EventDTO]
