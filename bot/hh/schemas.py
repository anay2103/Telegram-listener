from datetime import datetime
from typing import Any, Optional

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, field_serializer, field_validator

template = Environment(loader=FileSystemLoader('bot/templates')).get_template('vacancy.txt')


class Document(BaseModel):
    id: str
    text: str
    metadata: dict[str, Any]


class Vacancy(BaseModel):
    id: str


class VacancyListResponse(BaseModel):
    items: list[Vacancy]
    page: int
    pages: int
    per_page: int
    found: int


class NameModel(BaseModel):
    id: str


class SalaryRangeModel(BaseModel):
    from_: Optional[int] = Field(None, validation_alias='from')
    to: Optional[int] = None
    currency: str
    gross: bool
    mode: NameModel
    frequency: Optional[NameModel] = None


class VacancyAddressModel(BaseModel):
    raw: Optional[str] = None


class VacancyMetadataModel(BaseModel):
    id: str
    type: NameModel
    alternate_url: str
    published_at: datetime
    created_at: datetime

    @field_serializer('type', return_type=str)
    def validate_type(self, value: NameModel) -> str:
        return value.id

    @field_serializer('published_at', 'created_at', return_type=str)
    def validate_time(self, value: datetime) -> str:
        return value.isoformat()


class VacancyDetailResponse(BaseModel):
    id: str
    name: str
    description: str
    employer: NameModel
    area: NameModel
    salary_range: Optional[SalaryRangeModel] = None
    address: Optional[VacancyAddressModel] = None
    experience: Optional[NameModel] = None
    work_schedule_by_days: list[NameModel] = []
    working_hours: list[NameModel] = []
    work_format: list[NameModel] = []
    employment_form: Optional[NameModel] = None
    department: Optional[NameModel] = None
    description: str
    key_sklls: list[NameModel] = []

    @field_validator('description')
    @classmethod
    def validate_description(cls, value: str) -> str:
        return BeautifulSoup(value).get_text()

    @classmethod
    def from_source(cls, data: dict) -> Document:
        vacancy = cls(**data)
        text = template.render(vacancy=vacancy)
        metadata = VacancyMetadataModel(**data).model_dump()
        return Document(id=metadata['id'], text=text, metadata=metadata)
