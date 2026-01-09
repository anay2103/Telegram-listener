from pydantic import BaseModel, Field


class Vacancy(BaseModel):
    id: str = Field(description='Идентификатор вакансии')
    name: str = Field(description='Название вакансии')
    company: str = Field(description='Название компании-работодателя')
    url: str = Field(description='Url на источник вакансии')
    description: str = Field(description='Краткое описание вакансии')


class HHAgentOutput(BaseModel):
    vacancies: list[Vacancy]
