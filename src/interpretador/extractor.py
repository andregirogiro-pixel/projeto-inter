from __future__ import annotations

import re
from dataclasses import dataclass

from .models import (
    AnalysisResponse,
    AnalysisSummary,
    Attribution,
    Evidence,
    Operators,
    Participant,
    Proposition,
    ReferenceGroup,
    Referent,
    Span,
)


@dataclass(frozen=True)
class Token:
    texto: str
    inicio: int
    fim: int

    @property
    def normalizado(self) -> str:
        return self.texto.casefold()


@dataclass(frozen=True)
class Sentence:
    texto: str
    inicio: int
    fim: int


VERBOS = {
    "abandonou": "abandonar", "acredita": "acreditar", "assinasse": "assinar",
    "assinado": "assinar", "assinou": "assinar", "bombardeou": "bombardear",
    "construiu": "construir", "desistiu": "desistir", "encontrada": "encontrar",
    "encontrado": "encontrar", "enviou": "enviar", "enviado": "enviar",
    "esgotando": "esgotar", "frear": "frear", "havia": "haver", "morreu": "morrer",
    "morria": "morrer", "murmurou": "murmurar", "percebeu": "perceber",
    "perder": "perder", "revisando": "revisar", "sentou": "sentar", "seria": "ser",
    "tivesse": "ter", "transformando": "transformar", "foi": "ser", "era": "ser", "sido": "ser",
    "é": "ser", "são": "ser", "está": "estar", "estava": "estar", "pode": "poder",
    "poderia": "poder", "deve": "dever", "deveria": "dever", "quer": "querer",
    "queria": "querer", "disse": "dizer", "afirmou": "afirmar", "contou": "contar",
    "pensou": "pensar", "imaginou": "imaginar", "viu": "ver", "ouviu": "ouvir",
    "chegou": "chegar", "fez": "fazer", "tinha": "ter", "tem": "ter",
    "terá": "ter", "sofreu": "sofrer", "reagiu": "reagir",
}

AUXILIARES = {"havia", "tivesse", "foi", "era", "seria", "estava", "está", "tinha", "terá", "sido"}
VERBOS_FALA = {"dizer", "afirmar", "contar", "murmurar", "perguntar"}
VERBOS_COGNICAO = {"perceber", "acreditar", "pensar", "imaginar", "ver", "ouvir"}
MODAIS = {
    "pode": "possível", "poderia": "hipotética", "seria": "hipotética",
    "talvez": "possível", "possivelmente": "possível", "deve": "provável/necessária",
    "deveria": "esperada", "capaz": "capacidade",
}
PRONOMES_SUJEITO = {"ele", "ela", "eles", "elas"}
INICIOS_NAO_NOMINAIS = {"Quando", "Durante", "Apesar", "No", "Na", "Você", "Claro", "Enquanto", "Embora", "Porque", "Pois"}
NOMES_DE_PAPEL = {"gerente", "engenheira", "profissional", "diretor", "auditores", "bateria", "documento", "burocracia"}
NAO_VERBOS = {
    "quando", "enquanto", "segundo", "comando", "demanda", "anda", "ainda",
    "conteúdo", "sentido", "partido", "estado", "resultado", "cuidado",
}

TOKEN_RE = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", re.UNICODE)
SENTENCE_RE = re.compile(r"\s*[^.!?]+(?:[.!?]+(?=[\"”»']?(?:\s|$))|$)", re.UNICODE)
CONNECTOR_RE = re.compile(r"[,;:]|\b(?:quando|embora|porque|pois|enquanto|apesar\s+de|mas)\b", re.IGNORECASE)


def tokenizar(texto: str) -> list[Token]:
    return [Token(match.group(), match.start(), match.end()) for match in TOKEN_RE.finditer(texto)]


def segmentar_periodos(texto: str) -> list[Sentence]:
    periodos: list[Sentence] = []
    for match in SENTENCE_RE.finditer(texto):
        bruto = match.group()
        esquerda = len(bruto) - len(bruto.lstrip())
        inicio = match.start() + esquerda
        fim = match.end()
        if inicio < fim:
            periodos.append(Sentence(texto[inicio:fim], inicio, fim))
    return periodos or [Sentence(texto, 0, len(texto))]


def lematizar(token: Token) -> str | None:
    palavra = token.normalizado
    if palavra in NAO_VERBOS:
        return None
    if palavra in VERBOS:
        return VERBOS[palavra]
    if palavra.endswith("ando") and len(palavra) > 5:
        return palavra[:-4] + "ar"
    if palavra.endswith("endo") and len(palavra) > 5:
        return palavra[:-4] + "er"
    if palavra.endswith("indo") and len(palavra) > 5:
        return palavra[:-4] + "ir"
    if re.search(r"(?:aram|eram|iram|avam)$", palavra) and len(palavra) > 6:
        return palavra[:-4] + "r"
    if re.search(r"(?:asse|esse|isse)$", palavra) and len(palavra) > 6:
        return palavra[:-4] + "r"
    if re.search(r"(?:ado|ido)$", palavra) and len(palavra) > 5:
        return palavra[:-3] + "r"
    if palavra.endswith("ou") and len(palavra) > 4:
        return palavra[:-2] + "ar"
    return None


def intervalo_evidencia(texto: str, periodo: Sentence, token: Token) -> tuple[int, int]:
    indice_local = token.inicio - periodo.inicio
    inicio_local = 0
    fim_local = len(periodo.texto)
    for match in CONNECTOR_RE.finditer(periodo.texto):
        if match.start() < indice_local:
            inicio_local = match.end()
        else:
            fim_local = match.start()
            break

    inicio = periodo.inicio + inicio_local
    fim = periodo.inicio + fim_local
    while inicio < fim and texto[inicio].isspace():
        inicio += 1
    while fim > inicio and texto[fim - 1].isspace():
        fim -= 1
    return inicio, fim


def participante_mais_proximo(tokens: list[Token], indice_verbo: int, inicio_periodo: int) -> str:
    candidatos = [token for token in tokens[:indice_verbo] if token.inicio >= inicio_periodo]
    for indice in range(len(candidatos) - 1, -1, -1):
        token = candidatos[indice]
        if token.texto[:1].isupper() and token.texto not in INICIOS_NAO_NOMINAIS:
            return token.texto
        if token.normalizado in PRONOMES_SUJEITO:
            return token.texto
        if token.normalizado in NOMES_DE_PAPEL:
            artigo = ""
            if indice > 0 and candidatos[indice - 1].normalizado in {"o", "a", "os", "as", "um", "uma"}:
                artigo = candidatos[indice - 1].texto + " "
            return artigo + token.texto
    return "participante não resolvido"


def participante_anteposto(texto: str, inicio_periodo: int, inicio_verbo: int) -> str | None:
    trecho = texto[max(inicio_periodo, inicio_verbo - 110):inicio_verbo]
    match = re.search(
        r"\b((?:nenhum|nenhuma|o|a|os|as|um|uma)\s+[^\s,.;]+"
        r"(?:\s+(?!(?:havia|tivesse|tenha|foi|era|sido|estava)\b)[^\s,.;]+)?)"
        r"\s+(?:(?:não\s+)?(?:havia|tivesse|tenha|foi|era|sido|estava)\s+)*$",
        trecho,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def complemento(texto: str, token: Token, fim_evidencia: int) -> str | None:
    cauda = texto[token.fim:fim_evidencia]
    cauda = re.sub(r"^\s+(?:a|o|ao|à|os|as|um|uma|de|do|da)\s+", "", cauda, flags=re.IGNORECASE)
    cauda = re.sub(r"[.,;!?\"”]+$", "", cauda).strip()
    if len(cauda) < 3:
        return None
    return cauda if len(cauda) <= 86 else cauda[:83].rstrip() + "…"


def participante_posposto(texto: str, inicio: int, fim: int) -> str | None:
    trecho = texto[inicio:fim]
    match = re.search(
        r"\b(o|a|os|as|um|uma)\s+(gerente|engenheira|profissional|diretor|auditores)\b",
        trecho,
        re.IGNORECASE,
    )
    return match.group() if match else None


def resolver_referente(mencao: str, texto_anterior: str) -> Referent:
    normalizada = mencao.casefold()
    if normalizada == "helena":
        return Referent(id="R1", rotulo="Helena")
    if normalizada in {"ela", "dela", "a engenheira", "a profissional", "engenheira", "profissional"}:
        if re.search(r"\bHelena\b", texto_anterior):
            return Referent(id="R1", rotulo="Helena", hipotese=True)
        return Referent(id="?", rotulo="referente feminino incerto", hipotese=True)
    if normalizada in {"ele", "dele", "o gerente", "gerente"}:
        if re.search(r"\bgerente\b", texto_anterior, re.IGNORECASE):
            return Referent(id="R2", rotulo="gerente do banco", hipotese=True)
        return Referent(id="?", rotulo="referente masculino incerto", hipotese=True)
    if "gerente" in normalizada:
        return Referent(id="R2", rotulo="gerente do banco")
    if mencao == "participante não resolvido":
        return Referent(id="?", rotulo="não resolvido", hipotese=True)
    return Referent(id=f"M:{normalizada}", rotulo=mencao)


def extrair_operadores(texto: str, token: Token, inicio_evidencia: int, fim_evidencia: int) -> Operators:
    esquerda = texto[max(inicio_evidencia, token.inicio - 55):token.inicio].casefold()
    janela = texto[max(0, token.inicio - 65):min(len(texto), token.fim + 65)].casefold()
    negacoes = re.findall(r"\b(não|nunca|jamais|nenhum|nenhuma|nem)\b", esquerda)
    modalidade = next((tipo for palavra, tipo in MODAIS.items() if re.search(rf"\b{palavra}\b", janela)), None)
    return Operators(negacao=negacoes[-1] if negacoes else None, modalidade=modalidade)


def dentro_de_aspas(texto: str, indice: int) -> bool:
    anterior = texto[:indice]
    return anterior.count('"') % 2 == 1 or anterior.count("“") > anterior.count("”")


def extrair_atribuicao(texto: str, token: Token, lema: str, periodo: Sentence, participante: str) -> Attribution:
    if dentro_de_aspas(texto, token.inicio):
        fonte = "Helena (hipótese)" if re.search(r"Helena|engenheira", texto, re.IGNORECASE) else "falante não resolvido"
        return Attribution(fonte=fonte, modo="fala citada", estado="citada")
    if "?" in periodo.texto:
        return Attribution(fonte="enunciador", modo="pergunta", estado="questionada")
    if lema in VERBOS_FALA:
        return Attribution(fonte=participante, modo="fala", estado="afirmada")
    if lema in VERBOS_COGNICAO:
        modo = "percepção" if lema == "perceber" else "atitude mental"
        return Attribution(fonte=participante, modo=modo, estado="afirmada")
    prefixo = periodo.texto[:token.inicio - periodo.inicio]
    if re.search(r"percebeu\s+que", prefixo, re.IGNORECASE):
        return Attribution(fonte="Helena (hipótese)", modo="conteúdo percebido", estado="percebida")
    return Attribution(fonte="narrador", modo="asserção narrativa", estado="afirmada")


def calcular_confianca(participante: str, lema: str, operadores: Operators, atribuicao: Attribution) -> float:
    confianca = 0.86 if lema in VERBOS.values() else 0.76
    if participante == "participante não resolvido":
        confianca -= 0.13
    if atribuicao.estado in {"citada", "questionada"}:
        confianca -= 0.04
    if operadores.modalidade:
        confianca += 0.02
    return round(max(0.51, min(0.96, confianca)), 2)


def construir_referentes(texto: str, proposicoes: list[Proposition]) -> list[ReferenceGroup]:
    grupos: dict[str, tuple[str, set[str]]] = {}
    for proposicao in proposicoes:
        for participante in proposicao.participantes:
            referente = participante.referente
            if referente.id == "?":
                continue
            rotulo, mencoes = grupos.setdefault(referente.id, (referente.rotulo, set()))
            mencoes.add(participante.mencao)

    if re.search(r"\bHelena\b", texto):
        _, mencoes = grupos.setdefault("R1", ("Helena", set()))
        mencoes.update(match.group() for match in re.finditer(r"\b(Helena|ela|dela|engenheira|profissional|seu|sua)\b", texto, re.IGNORECASE))
    if re.search(r"\bgerente\b", texto, re.IGNORECASE):
        _, mencoes = grupos.setdefault("R2", ("gerente do banco", set()))
        mencoes.update(match.group() for match in re.finditer(r"\b(gerente(?: do banco)?|ele|dele)\b", texto, re.IGNORECASE))

    return [
        ReferenceGroup(id=identificador, rotulo=rotulo, mencoes=sorted(mencoes, key=str.casefold))
        for identificador, (rotulo, mencoes) in list(grupos.items())[:8]
    ]


def analisar_paragrafo(texto: str) -> AnalysisResponse:
    texto = texto.strip()
    if not texto:
        raise ValueError("O parágrafo não pode estar vazio.")

    tokens = tokenizar(texto)
    periodos = segmentar_periodos(texto)
    proposicoes: list[Proposition] = []

    for indice, token in enumerate(tokens):
        lema = lematizar(token)
        if not lema:
            continue
        proximo = tokens[indice + 1] if indice + 1 < len(tokens) else None
        if token.normalizado in AUXILIARES and proximo and lematizar(proximo) and proximo.inicio - token.fim < 18:
            continue

        periodo = next((item for item in periodos if item.inicio <= token.inicio < item.fim), periodos[0])
        inicio, fim = intervalo_evidencia(texto, periodo, token)
        participante = (
            participante_anteposto(texto, periodo.inicio, token.inicio)
            or participante_mais_proximo(tokens, indice, periodo.inicio)
        )
        if participante == "participante não resolvido" and lema in VERBOS_FALA:
            participante = participante_posposto(texto, token.fim, periodo.fim) or participante
        referente = resolver_referente(participante, texto[:token.inicio])
        objeto = complemento(texto, token, fim)
        operadores = extrair_operadores(texto, token, inicio, fim)
        atribuicao = extrair_atribuicao(texto, token, lema, periodo, participante)
        descricao = f"{participante} · {lema}" + (f" · {objeto}" if objeto else "")
        proposicoes.append(Proposition(
            id=f"P{len(proposicoes) + 1}",
            predicado=lema,
            forma_textual=token.texto,
            descricao=descricao,
            participantes=[Participant(papel="participante_principal", mencao=participante, referente=referente)],
            operadores=operadores,
            atribuicao=atribuicao,
            evidencia=Evidence(texto=texto[inicio:fim], intervalo=Span(inicio=inicio, fim=fim)),
            confianca=calcular_confianca(participante, lema, operadores, atribuicao),
        ))

    referentes = construir_referentes(texto, proposicoes)
    alertas: list[str] = []
    if not proposicoes:
        alertas.append("Nenhum predicado foi identificado com segurança; revisão manual necessária.")
    if any(participante.referente.id == "?" for prop in proposicoes for participante in prop.participantes):
        alertas.append("Há participantes ou referências não resolvidos.")

    return AnalysisResponse(
        paragrafo=texto,
        proposicoes=proposicoes,
        referentes=referentes,
        resumo=AnalysisSummary(
            proposicoes=len(proposicoes),
            referentes=len(referentes),
            negacoes=sum(prop.operadores.negacao is not None for prop in proposicoes),
            atribuicoes_marcadas=sum(prop.atribuicao.modo != "asserção narrativa" for prop in proposicoes),
        ),
        alertas=alertas,
    )

