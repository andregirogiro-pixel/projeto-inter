from .models import Mention


def validar_mencoes(texto: str, mencoes: list[Mention]) -> None:
    ids = {mencao.id for mencao in mencoes}
    if len(ids) != len(mencoes):
        raise ValueError("IDs de menção duplicados.")

    por_id = {mencao.id: mencao for mencao in mencoes}
    for mencao in mencoes:
        trecho = texto[mencao.intervalo.inicio:mencao.intervalo.fim]
        if trecho != mencao.texto:
            raise ValueError(f"Intervalo incompatível com o texto da menção {mencao.id}.")
        if mencao.mencao_pai_id is None:
            continue
        if mencao.mencao_pai_id not in ids:
            raise ValueError(f"Menção pai inexistente em {mencao.id}.")
        pai = por_id[mencao.mencao_pai_id]
        if not (
            pai.intervalo.inicio <= mencao.intervalo.inicio
            and pai.intervalo.fim >= mencao.intervalo.fim
        ):
            raise ValueError(f"Menção pai não contém o intervalo de {mencao.id}.")

