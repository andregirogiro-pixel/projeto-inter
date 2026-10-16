import unittest

from interpretador.extractor import analisar_paragrafo


EXEMPLO = (
    "Quando Helena se sentou no banco da praça, percebeu que o gerente não havia "
    "assinado o contrato. Ele afirmou que talvez assinasse amanhã."
)


class ExtractorTests(unittest.TestCase):
    def test_extrai_proposicoes_com_evidencias_validas(self) -> None:
        resultado = analisar_paragrafo(EXEMPLO)
        self.assertGreaterEqual(len(resultado.proposicoes), 3)
        for proposicao in resultado.proposicoes:
            intervalo = proposicao.evidencia.intervalo
            self.assertEqual(
                proposicao.evidencia.texto,
                resultado.paragrafo[intervalo.inicio:intervalo.fim],
            )

    def test_detecta_negacao(self) -> None:
        resultado = analisar_paragrafo(EXEMPLO)
        negadas = [prop for prop in resultado.proposicoes if prop.operadores.negacao]
        self.assertTrue(negadas)
        self.assertTrue(any(prop.predicado == "assinar" for prop in negadas))

    def test_resolve_helena_e_gerente(self) -> None:
        resultado = analisar_paragrafo(EXEMPLO)
        ids = {referente.id for referente in resultado.referentes}
        self.assertIn("R1", ids)
        self.assertIn("R2", ids)

    def test_cadeia_auxiliar_gera_uma_proposicao_lexical(self) -> None:
        resultado = analisar_paragrafo("Nenhuma falha tivesse sido encontrada.")
        predicados = [proposicao.predicado for proposicao in resultado.proposicoes]
        self.assertEqual(predicados, ["encontrar"])
        self.assertEqual(resultado.proposicoes[0].participantes[0].mencao, "Nenhuma falha")


if __name__ == "__main__":
    unittest.main()

