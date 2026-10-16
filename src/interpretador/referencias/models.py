from typing import Literal

from pydantic import BaseModel, Field

from ..models import Span


MentionOrigin = Literal["contexto_anterior", "paragrafo"]
MentionType = Literal[
    "nome_proprio",
    "descricao_nominal",
    "descricao_complexa",
    "pronome_pessoal",
    "pronome_possessivo",
]


class MentionFeatures(BaseModel):
    classe_semantica: Literal["pessoa", "objeto", "lugar", "evento", "desconhecida"]
    genero: Literal["feminino", "masculino", "indeterminado"]
    numero: Literal["singular", "plural", "indeterminado"]


class Mention(BaseModel):
    id: str
    texto: str
    tipo: MentionType
    origem: MentionOrigin
    intervalo: Span
    caracteristicas: MentionFeatures
    confianca_deteccao: float = Field(ge=0, le=1)
    mencao_pai_id: str | None = None

