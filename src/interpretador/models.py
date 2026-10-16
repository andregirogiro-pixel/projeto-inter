from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    paragrafo: str = Field(max_length=5_000)

    @field_validator("paragrafo")
    @classmethod
    def validar_paragrafo(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O parágrafo não pode estar vazio.")
        return value


class Span(BaseModel):
    inicio: int = Field(ge=0)
    fim: int = Field(gt=0)
    unidade: Literal["pontos_de_codigo_unicode"] = "pontos_de_codigo_unicode"


class Evidence(BaseModel):
    texto: str
    intervalo: Span


class Referent(BaseModel):
    id: str
    rotulo: str
    hipotese: bool = False


class Participant(BaseModel):
    papel: str
    mencao: str
    referente: Referent


class Operators(BaseModel):
    negacao: str | None = None
    modalidade: str | None = None


class Attribution(BaseModel):
    fonte: str
    modo: str
    estado: Literal["afirmada", "percebida", "citada", "questionada", "hipotetica"]


class Proposition(BaseModel):
    id: str
    predicado: str
    forma_textual: str
    descricao: str
    participantes: list[Participant]
    operadores: Operators
    atribuicao: Attribution
    evidencia: Evidence
    confianca: float = Field(ge=0, le=1)


class ReferenceGroup(BaseModel):
    id: str
    rotulo: str
    mencoes: list[str]


class AnalysisSummary(BaseModel):
    proposicoes: int
    referentes: int
    negacoes: int
    atribuicoes_marcadas: int


class AnalysisResponse(BaseModel):
    schema_version: Literal["0.1.0"] = "0.1.0"
    paragrafo: str
    proposicoes: list[Proposition]
    referentes: list[ReferenceGroup]
    resumo: AnalysisSummary
    alertas: list[str]

