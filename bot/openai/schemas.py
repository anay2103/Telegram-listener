from pydantic import BaseModel, Field


class HHAgentOutput(BaseModel):
    vacancies: list[str] = Field(description='список описаний вакансий и ссылок на них')
    ids: list[int] = Field(description='список идентификаторов вакансий')
