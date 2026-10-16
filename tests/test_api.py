import unittest

from interpretador.main import app, health
from interpretador.models import AnalysisRequest
from interpretador.main import analisar


class ApiTests(unittest.TestCase):
    def test_health(self) -> None:
        self.assertEqual(health(), {"status": "ok"})

    def test_endpoint_de_analise(self) -> None:
        resultado = analisar(AnalysisRequest(paragrafo="Helena percebeu o problema."))
        self.assertEqual(resultado.schema_version, "0.2.0")
        self.assertGreaterEqual(resultado.resumo.proposicoes, 1)

    def test_rotas_publicadas_no_openapi(self) -> None:
        caminhos = app.openapi()["paths"]
        self.assertIn("/health", caminhos)
        self.assertIn("/api/analisar", caminhos)


if __name__ == "__main__":
    unittest.main()

