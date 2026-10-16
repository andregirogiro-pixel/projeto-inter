# Interpretador fundamentado

Aplicativo para receber a saída da etapa `09_vetorizacao` e produzir interpretações rastreáveis ao texto original.

O primeiro recorte do produto é deliberadamente pequeno: interpretar **um parágrafo**, propor sua ideia central e gerar uma síntese fiel, sempre acompanhadas de evidências e alertas de checagem.

## Estado atual

O projeto está na **Etapa 1 — estrutura básica**. O motor e a API são escritos em Python; a primeira interface funcional está em `dist/`. Os anexos originais foram preservados em:

- `fixtures/vetorizacao-28.json`: exemplo real de entrada;
- `docs/referencias/arquitetura_interpretacao_fundamentada_v1.pdf`: referência conceitual.

O plano e os critérios de aceite estão em [`docs/01-escopo-e-etapas.md`](docs/01-escopo-e-etapas.md).

## Interface atual

A página recebe um parágrafo e chama a API Python local. Ela produz uma lista preliminar contendo predicado, participante principal, referente, negação, modalidade, atribuição, evidência e intervalo no original.

Esta versão é um extrator heurístico demonstrativo. Confiança e pendências são exibidas de forma explícita; a validação linguística e o motor semântico serão desenvolvidos nas próximas etapas.

## Baixar e executar

Depois de clonar o repositório, entre na pasta do projeto e execute:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
uvicorn interpretador.main:app --reload
```

Abra `http://127.0.0.1:8000`. A documentação da API fica em `http://127.0.0.1:8000/docs`.

## Testar

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

No PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

## Princípio de arquitetura

A interpretação não será inferida dos números do embedding isoladamente. O aplicativo usará o texto original, a análise estrutural e os vínculos presentes no JSON como fonte primária; os vetores servirão como sinal auxiliar para recuperação, associação e priorização. Toda afirmação relevante deverá apontar para trechos do original.

