(() => {
  const sessionToken = document.querySelector('meta[name="acr-session"]').content;
  const state = { categories: [], actions: [], activeCategory: "", activeAction: null, controller: null };
  const el = (id) => document.getElementById(id);
  const projectRoot = el("project-root");
  const categories = el("categories");
  const actions = el("actions");
  const categoryTitle = el("category-title");
  const runPanel = el("run-panel");
  const actionTitle = el("action-title");
  const actionDescription = el("action-description");
  const fields = el("fields");
  const heavyConfirm = el("heavy-confirm");
  const allowHeavy = el("allow-heavy");
  const form = el("action-form");
  const runButton = el("run-button");
  const cancelButton = el("cancel-button");
  const resultPanel = el("result-panel");
  const resultHeadline = el("result-headline");
  const resultState = el("result-state");
  const summary = el("summary");
  const detailOutput = el("detail-output");
  const stderrBox = el("stderr-box");
  const stderrOutput = el("stderr-output");
  const resultError = el("result-error");
  const health = el("health");
  const analyzeProjectButton = el("analyze-project");
  const analysisState = el("analysis-state");
  const recommendationsPanel = el("recommendations-panel");
  const projectProfile = el("project-profile");
  const recommendedList = el("recommended-list");
  const conditionalList = el("conditional-list");
  const unavailableSection = el("unavailable-section");
  const unavailableList = el("unavailable-list");
  const analysisDetail = el("analysis-detail");
  const selectionDetail = el("selection-detail");

  async function loadCatalog() {
    const response = await fetch("/api/actions", { cache: "no-store" });
    if (!response.ok) throw new Error("機能一覧を取得できませんでした");
    const payload = await response.json();
    state.categories = payload.categories;
    state.actions = payload.actions;
    projectRoot.value = payload.initial_project || "";
    state.activeCategory = payload.categories[0]?.id || "";
    renderCategories();
    renderActions();
  }

  function renderCategories() {
    categories.innerHTML = "";
    for (const category of state.categories) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "category-button" + (category.id === state.activeCategory ? " active" : "");
      button.textContent = category.title;
      button.addEventListener("click", () => {
        state.activeCategory = category.id;
        renderCategories();
        renderActions();
      });
      categories.appendChild(button);
    }
  }

  function renderActions() {
    const category = state.categories.find((item) => item.id === state.activeCategory);
    categoryTitle.textContent = category?.title || "";
    actions.innerHTML = "";
    for (const action of state.actions.filter((item) => item.category === state.activeCategory)) {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "action-card";
      const badges = [];
      if (action.heavy) badges.push('<span class="badge warning">Explicit confirm</span>');
      if (action.writes_files) badges.push('<span class="badge">Writes file</span>');
      card.innerHTML = '<h3></h3><p></p><div class="badges">' + badges.join("") + "</div>";
      card.querySelector("h3").textContent = action.title;
      card.querySelector("p").textContent = action.description;
      card.addEventListener("click", () => selectAction(action));
      actions.appendChild(card);
    }
  }

  function selectAction(action) {
    state.activeAction = action;
    actionTitle.textContent = action.title;
    actionDescription.textContent = action.description;
    fields.innerHTML = "";
    allowHeavy.checked = false;
    heavyConfirm.classList.toggle("hidden", !action.heavy);
    for (const field of action.fields) {
      if (field.kind === "project_root") continue;
      fields.appendChild(renderField(field));
    }
    runPanel.classList.remove("hidden");
    runPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function renderField(field) {
    const wrapper = document.createElement("div");
    wrapper.className = "field" + (field.kind === "multiline" ? " full" : "");
    const label = document.createElement("label");
    label.htmlFor = "field-" + field.id;
    label.textContent = field.label + (field.required ? " *" : "");
    wrapper.appendChild(label);

    let input;
    if (field.kind === "multiline") {
      input = document.createElement("textarea");
    } else if (field.kind === "select") {
      input = document.createElement("select");
      for (const option of field.options || []) {
        const node = document.createElement("option");
        node.value = option.value;
        node.textContent = option.label;
        input.appendChild(node);
      }
    } else if (field.kind === "boolean") {
      input = document.createElement("input");
      input.type = "checkbox";
      input.value = "true";
    } else {
      input = document.createElement("input");
      input.type = "text";
    }

    input.id = "field-" + field.id;
    input.dataset.fieldId = field.id;
    input.dataset.kind = field.kind;
    if (field.placeholder) input.placeholder = field.placeholder;
    if (field.default && field.kind !== "boolean") input.value = field.default;
    if (field.kind === "boolean") input.checked = field.default === "true";
    input.required = Boolean(field.required);
    wrapper.appendChild(input);

    if (field.help) {
      const help = document.createElement("p");
      help.className = "field-help";
      help.textContent = field.help;
      wrapper.appendChild(help);
    }
    return wrapper;
  }

  function collectValues() {
    const values = {};
    fields.querySelectorAll("[data-field-id]").forEach((input) => {
      values[input.dataset.fieldId] = input.dataset.kind === "boolean" ? (input.checked ? "true" : "false") : input.value;
    });
    return values;
  }

  function setRunning(running) {
    runButton.disabled = running;
    analyzeProjectButton.disabled = running;
    cancelButton.classList.toggle("hidden", !running);
    health.textContent = running ? "Running" : "Ready";
    health.className = "status-chip " + (running ? "running" : "neutral");
  }

  function showResult(payload) {
    const result = payload.result;
    resultPanel.classList.remove("hidden");
    resultHeadline.textContent = result.headline;
    resultState.textContent = result.state;
    resultState.className = "status-chip " + result.state;
    summary.innerHTML = "";
    for (const item of result.summary || []) {
      const box = document.createElement("dl");
      box.className = "summary-item";
      const dt = document.createElement("dt");
      dt.textContent = item.label;
      const dd = document.createElement("dd");
      dd.textContent = item.value;
      box.append(dt, dd);
      summary.appendChild(box);
    }
    detailOutput.textContent = result.detail || "(no detail)";
    stderrOutput.textContent = result.stderr || "";
    stderrBox.classList.toggle("hidden", !result.stderr);
    if (result.error) {
      resultError.textContent = result.error;
      resultError.classList.remove("hidden");
    } else {
      resultError.textContent = "";
      resultError.classList.add("hidden");
    }
    resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  async function executeAction(action, values = {}, heavyAllowed = false) {
    state.controller = new AbortController();
    setRunning(true);
    resultPanel.classList.add("hidden");
    try {
      const response = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-ACR-Session": sessionToken },
        body: JSON.stringify({
          action_id: action.id,
          project_root: projectRoot.value,
          values,
          allow_heavy: heavyAllowed,
        }),
        signal: state.controller.signal,
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "実行要求に失敗しました");
      showResult(payload);
    } catch (error) {
      if (error.name === "AbortError") showLocalFailure("キャンセルしました。", "cancelled");
      else showLocalFailure(error.message || String(error));
    } finally {
      state.controller = null;
      setRunning(false);
    }
  }

  async function runAction(event) {
    event.preventDefault();
    const action = state.activeAction;
    if (!action) return;
    if (action.heavy && !allowHeavy.checked) {
      showLocalFailure("Large / heavy解析の明示確認が必要です。", "confirmation_required");
      return;
    }
    await executeAction(action, collectValues(), allowHeavy.checked);
  }

  function recommendationNeedsInput(action) {
    return action.heavy || action.writes_files || (action.fields || []).some((field) => field.kind !== "project_root");
  }

  async function runRecommendation(row) {
    if (!row.action_id) return;
    const action = state.actions.find((item) => item.id === row.action_id);
    if (!action) return;
    if (recommendationNeedsInput(action)) {
      state.activeCategory = action.category;
      renderCategories();
      renderActions();
      selectAction(action);
      return;
    }
    state.activeAction = action;
    await executeAction(action, {}, false);
  }

  function recommendationCard(row) {
    const card = document.createElement("div");
    card.className = "recommendation-card " + row.kind;
    const title = document.createElement("h4");
    title.textContent = row.title;
    const reason = document.createElement("p");
    reason.textContent = row.reason || "selector recommendation";
    const meta = document.createElement("div");
    meta.className = "recommendation-meta";
    for (const value of [row.kind, row.availability, row.activation].filter(Boolean)) {
      const badge = document.createElement("span");
      badge.className = "badge";
      badge.textContent = value;
      meta.appendChild(badge);
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = row.kind === "unavailable" ? "secondary" : "primary";
    button.textContent = row.kind === "unavailable" ? "Unavailable" : "Run";
    button.disabled = !row.action_id;
    if (row.action_id) button.addEventListener("click", () => runRecommendation(row));
    card.append(title, reason, meta, button);
    return card;
  }

  function renderRecommendationList(target, rows) {
    target.innerHTML = "";
    for (const row of rows) target.appendChild(recommendationCard(row));
    if (!rows.length) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = "該当候補はありません。";
      target.appendChild(empty);
    }
  }

  function showProjectAnalysis(payload) {
    analysisState.textContent = payload.state;
    analysisState.className = "status-chip " + payload.state;
    if (payload.state !== "success") {
      showLocalFailure(payload.error || payload.headline || "Project Analysisに失敗しました。", payload.state || "failure");
      return;
    }
    const types = (payload.detected_project_types || []).join(", ");
    projectProfile.textContent = "size: " + (payload.project_size_class || "unknown") + (types ? " / type: " + types : "");
    const unavailable = [...(payload.recommended || []), ...(payload.conditional || [])].filter((row) => row.kind === "unavailable");
    const recommended = (payload.recommended || []).filter((row) => row.kind === "recommended");
    const conditional = (payload.conditional || []).filter((row) => row.kind === "conditional");
    renderRecommendationList(recommendedList, recommended);
    renderRecommendationList(conditionalList, conditional);
    renderRecommendationList(unavailableList, unavailable);
    unavailableSection.classList.toggle("hidden", unavailable.length === 0);
    analysisDetail.textContent = payload.analysis?.detail || "(no detail)";
    selectionDetail.textContent = payload.selection?.detail || "(no detail)";
    recommendationsPanel.classList.remove("hidden");
    recommendationsPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  async function runProjectAnalysis() {
    if (!projectRoot.value.trim()) {
      showLocalFailure("Project rootを指定してください。");
      return;
    }
    state.controller = new AbortController();
    setRunning(true);
    analysisState.textContent = "running";
    analysisState.className = "status-chip running";
    recommendationsPanel.classList.add("hidden");
    try {
      const response = await fetch("/api/project-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-ACR-Session": sessionToken },
        body: JSON.stringify({ project_root: projectRoot.value }),
        signal: state.controller.signal,
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Project Analysisに失敗しました");
      showProjectAnalysis(payload);
    } catch (error) {
      if (error.name === "AbortError") {
        analysisState.textContent = "cancelled";
        analysisState.className = "status-chip cancelled";
        showLocalFailure("Project Analysisをキャンセルしました。", "cancelled");
      } else {
        analysisState.textContent = "failure";
        analysisState.className = "status-chip failure";
        showLocalFailure(error.message || String(error));
      }
    } finally {
      state.controller = null;
      setRunning(false);
    }
  }

  function showLocalFailure(message, stateName = "failure") {
    showResult({
      result: {
        state: stateName,
        headline: stateName === "cancelled" ? "キャンセルしました" : (stateName === "confirmation_required" ? "明示確認が必要です" : "実行できませんでした"),
        exit_code: -1,
        summary: [],
        detail: "",
        stderr: "",
        error: message,
      },
    });
  }

  form.addEventListener("submit", runAction);
  analyzeProjectButton.addEventListener("click", runProjectAnalysis);
  cancelButton.addEventListener("click", () => state.controller?.abort());
  el("close-panel").addEventListener("click", () => runPanel.classList.add("hidden"));
  loadCatalog().catch((error) => {
    health.textContent = "Unavailable";
    health.className = "status-chip failure";
    showLocalFailure(error.message || String(error));
  });
})();
