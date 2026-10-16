const exampleContext = `Quando Helena finalmente se sentou no banco da praça, percebeu que o gerente do banco não havia assinado o contrato de financiamento por pura cautela. Durante toda a reunião matinal, ele bombardeou a proposta dela com argumentos pesados, embora nenhuma falha técnica tivesse sido encontrada nos cálculos pelos auditores externos. "Claro, porque perder três semanas revisando planilhas é exatamente o meu conceito de eficiência", murmurou a engenheira para si mesma, enquanto a bateria do seu celular morria lentamente sob a sombra das árvores.`;
const exampleParagraph = `Apesar daquele revés temporário, a profissional não abandonou o campo de batalha nem desistiu de buscar novos recursos para o projeto solar. No fim da tarde, o documento atualizado foi enviado por ela ao diretor financeiro através de um mensageiro expresso, pois o tempo já estava se esgotando. Você realmente acredita que uma simples burocracia bancária seria capaz de frear alguém que construiu toda a carreira transformando crises em combustível?`;

const paragraphInput = document.querySelector("#paragraph");
const contextInput = document.querySelector("#previous-context");
const contextBox = document.querySelector(".context-box");
const charCount = document.querySelector("#char-count");
const analyzeButton = document.querySelector("#analyze");
const exampleButton = document.querySelector("#example");
const clearButton = document.querySelector("#clear");
const emptyState = document.querySelector("#empty-state");
const analysisOutput = document.querySelector("#analysis-output");
const propositionList = document.querySelector("#proposition-list");
const mentionMap = document.querySelector("#mention-map");
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

function typeLabel(type) {
  return ({
    nome_proprio: "nome próprio",
    descricao_nominal: "descrição",
    descricao_complexa: "descrição complexa",
    pronome_pessoal: "pronome",
    pronome_possessivo: "possessivo"
  })[type] || type;
}

function renderMentionGroup(title, mentions, sourceLabel) {
  if (!mentions.length) return "";
  const items = mentions.map(mention => `
    <li class="mention-item ${mention.mencao_pai_id ? "nested" : ""}">
      <span class="mention-id">${escapeHtml(mention.id)}</span>
      <span class="mention-text">“${escapeHtml(mention.texto)}”</span>
      <span class="mention-type">${escapeHtml(typeLabel(mention.tipo))}</span>
      <span class="mention-meta">${escapeHtml(mention.caracteristicas.classe_semantica)} · [${mention.intervalo.inicio}, ${mention.intervalo.fim})${mention.mencao_pai_id ? ` · dentro de ${escapeHtml(mention.mencao_pai_id)}` : ""}</span>
    </li>
  `).join("");
  return `
    <section class="mention-source">
      <h4>${escapeHtml(title)} <small>${escapeHtml(sourceLabel)}</small></h4>
      <ul class="mention-list">${items}</ul>
    </section>
  `;
}

function renderMentions(mentions) {
  const fromContext = mentions.filter(item => item.origem === "contexto_anterior");
  const fromParagraph = mentions.filter(item => item.origem === "paragrafo");
  mentionMap.innerHTML = `
    <header>
      <div>
        <h3 id="mention-title">Menções detectadas</h3>
        <p>Os referentes R1/R2 serão formados no próximo incremento.</p>
      </div>
      <span>${mentions.length} ${mentions.length === 1 ? "menção" : "menções"}</span>
    </header>
    ${renderMentionGroup("Contexto anterior", fromContext, "apoio referencial")}
    ${renderMentionGroup("Parágrafo principal", fromParagraph, "origem das proposições")}
  `;
}

function renderPropositions(propositions) {
  propositionList.innerHTML = propositions.map((prop, index) => {
    const participant = prop.participantes[0] || null;
    const negation = prop.operadores.negacao ? `sim — marcador “${prop.operadores.negacao}”` : "não detectada";
    const modality = prop.operadores.modalidade || "não marcada";
    const negationClass = prop.operadores.negacao ? "operator-alert" : "operator-none";
    const modalityClass = prop.operadores.modalidade ? "operator-alert" : "operator-none";
    const participantText = participant
      ? `${escapeHtml(participant.mencao)} · ${escapeHtml(participant.papel)}`
      : `<span class="operator-alert">não localizado</span>`;
    const mentionText = participant
      ? `${escapeHtml(participant.mencao_id)} · [${participant.intervalo.inicio}, ${participant.intervalo.fim})`
      : `<span class="operator-none">sem menção vinculada</span>`;
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
            <dd>${participantText}</dd>
          </div>
          <div class="field">
            <dt>Menção vinculada</dt>
            <dd>${mentionText}</dd>
          </div>
          <div class="field">
            <dt>Referente</dt>
            <dd class="operator-none">aguardando resolução</dd>
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
  mentionMap.innerHTML = "";
  propositionList.innerHTML = `<li class="error-state">${escapeHtml(message)}</li>`;
  resultStats.hidden = true;
}

async function renderAnalysis() {
  const text = paragraphInput.value.trim();
  const context = contextInput.value.trim();
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
      body: JSON.stringify({ paragrafo: text, contexto_anterior: context || null })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail?.[0]?.msg || data.detail || "Não foi possível analisar o parágrafo.");

    emptyState.hidden = true;
    analysisOutput.hidden = false;
    renderMentions(data.mencoes);
    if (data.proposicoes.length) renderPropositions(data.proposicoes);
    else propositionList.innerHTML = `<li class="error-state">${escapeHtml(data.alertas[0] || "Nenhuma proposição identificada.")}</li>`;

    const summary = data.resumo;
    resultStats.innerHTML = `
      <span class="mini-chip">${summary.proposicoes} proposições</span>
      <span class="mini-chip">${summary.mencoes} menções</span>
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
  contextInput.value = exampleContext;
  contextBox.open = true;
  updateCount();
  renderAnalysis();
});
clearButton.addEventListener("click", () => {
  paragraphInput.value = "";
  contextInput.value = "";
  updateCount();
  emptyState.hidden = false;
  analysisOutput.hidden = true;
  resultStats.hidden = true;
  paragraphInput.focus();
});

paragraphInput.value = exampleParagraph;
contextInput.value = exampleContext;
contextBox.open = true;
updateCount();

