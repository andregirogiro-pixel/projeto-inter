const exampleParagraph = `Quando Helena finalmente se sentou no banco da praça, percebeu que o gerente do banco não havia assinado o contrato de financiamento por pura cautela. Durante toda a reunião matinal, ele bombardeou a proposta dela com argumentos pesados, embora nenhuma falha técnica tivesse sido encontrada nos cálculos pelos auditores externos. "Claro, porque perder três semanas revisando planilhas é exatamente o meu conceito de eficiência", murmurou a engenheira para si mesma, enquanto a bateria do seu celular morria lentamente sob a sombra das árvores.`;

const paragraphInput = document.querySelector("#paragraph");
const charCount = document.querySelector("#char-count");
const analyzeButton = document.querySelector("#analyze");
const exampleButton = document.querySelector("#example");
const clearButton = document.querySelector("#clear");
const emptyState = document.querySelector("#empty-state");
const analysisOutput = document.querySelector("#analysis-output");
const propositionList = document.querySelector("#proposition-list");
const referenceMap = document.querySelector("#reference-map");
const resultStats = document.querySelector("#result-stats");

function updateCount() {
  const count = [...paragraphInput.value].length;
  charCount.textContent = `${count} ${count === 1 ? "caractere" : "caracteres"}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderReferences(groups) {
  const content = groups.length
    ? groups.map(group => `<span class="reference-group"><strong>${escapeHtml(group.id)}</strong> ${escapeHtml(group.rotulo)} ← ${escapeHtml(group.mencoes.join(", "))}</span>`).join("")
    : `<span class="reference-group"><strong>—</strong> Nenhuma cadeia referencial segura detectada</span>`;
  referenceMap.innerHTML = `
    <header>
      <h3 id="reference-title">Mapa preliminar de referentes</h3>
      <span>${groups.length} ${groups.length === 1 ? "grupo" : "grupos"}</span>
    </header>
    <div class="reference-groups">${content}</div>
  `;
}

function renderPropositions(propositions) {
  propositionList.innerHTML = propositions.map((prop, index) => {
    const participant = prop.participantes[0];
    const negation = prop.operadores.negacao ? `sim — marcador “${prop.operadores.negacao}”` : "não detectada";
    const modality = prop.operadores.modalidade || "não marcada";
    const negationClass = prop.operadores.negacao ? "operator-alert" : "operator-none";
    const modalityClass = prop.operadores.modalidade ? "operator-alert" : "operator-none";
    return `
      <li class="proposition-card" style="animation-delay:${Math.min(index * 45, 360)}ms">
        <div class="card-top">
          <span class="proposition-id">${escapeHtml(prop.id)}</span>
          <div class="card-badges">
            <span class="status-chip ${escapeHtml(prop.atribuicao.estado)}">${escapeHtml(prop.atribuicao.estado)}</span>
            <span class="confidence">${Math.round(prop.confianca * 100)}% confiança</span>
          </div>
        </div>
        <h3 class="proposition-title">${escapeHtml(prop.descricao)}</h3>
        <dl class="field-grid">
          <div class="field">
            <dt>Predicado</dt>
            <dd>${escapeHtml(prop.predicado)} <span class="operator-none">(“${escapeHtml(prop.forma_textual)}”)</span></dd>
          </div>
          <div class="field">
            <dt>Participante principal</dt>
            <dd>${escapeHtml(participant.mencao)} · ${escapeHtml(participant.papel)}</dd>
          </div>
          <div class="field">
            <dt>Referente</dt>
            <dd>${escapeHtml(participant.referente.id)} · ${escapeHtml(participant.referente.rotulo)}${participant.referente.hipotese ? " · hipótese" : ""}</dd>
          </div>
          <div class="field">
            <dt>Atribuição</dt>
            <dd>${escapeHtml(prop.atribuicao.fonte)} · ${escapeHtml(prop.atribuicao.modo)}</dd>
          </div>
          <div class="field">
            <dt>Negação</dt>
            <dd class="${negationClass}">${escapeHtml(negation)}</dd>
          </div>
          <div class="field">
            <dt>Modalidade</dt>
            <dd class="${modalityClass}">${escapeHtml(modality)}</dd>
          </div>
        </dl>
        <blockquote class="evidence">“${escapeHtml(prop.evidencia.texto)}”<span>[${prop.evidencia.intervalo.inicio}, ${prop.evidencia.intervalo.fim})</span></blockquote>
      </li>
    `;
  }).join("");
}

function renderError(message) {
  emptyState.hidden = true;
  analysisOutput.hidden = false;
  referenceMap.innerHTML = "";
  propositionList.innerHTML = `<li class="error-state">${escapeHtml(message)}</li>`;
  resultStats.hidden = true;
}

async function renderAnalysis() {
  const text = paragraphInput.value.trim();
  if (!text) {
    renderError("Insira um parágrafo antes de iniciar a análise.");
    paragraphInput.focus();
    return;
  }

  const label = analyzeButton.querySelector("span");
  const originalLabel = label.textContent;
  analyzeButton.disabled = true;
  label.textContent = "Analisando…";

  try {
    const response = await fetch("/api/analisar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paragrafo: text })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail?.[0]?.msg || data.detail || "Não foi possível analisar o parágrafo.");

    emptyState.hidden = true;
    analysisOutput.hidden = false;
    renderReferences(data.referentes);
    if (data.proposicoes.length) renderPropositions(data.proposicoes);
    else propositionList.innerHTML = `<li class="error-state">${escapeHtml(data.alertas[0] || "Nenhuma proposição identificada.")}</li>`;

    const summary = data.resumo;
    resultStats.innerHTML = `
      <span class="mini-chip">${summary.proposicoes} proposições</span>
      <span class="mini-chip">${summary.referentes} referentes</span>
      <span class="mini-chip">${summary.negacoes} negações</span>
      <span class="mini-chip">${summary.atribuicoes_marcadas} atribuídas</span>
    `;
    resultStats.hidden = false;
  } catch (error) {
    renderError(error.message || "Falha inesperada durante a análise.");
  } finally {
    analyzeButton.disabled = false;
    label.textContent = originalLabel;
  }
}

paragraphInput.addEventListener("input", updateCount);
analyzeButton.addEventListener("click", renderAnalysis);
exampleButton.addEventListener("click", () => {
  paragraphInput.value = exampleParagraph;
  updateCount();
  renderAnalysis();
});
clearButton.addEventListener("click", () => {
  paragraphInput.value = "";
  updateCount();
  emptyState.hidden = false;
  analysisOutput.hidden = true;
  resultStats.hidden = true;
  paragraphInput.focus();
});

paragraphInput.value = exampleParagraph;
updateCount();

