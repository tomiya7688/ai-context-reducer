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

  async function runAction(event) {
    event.preventDefault();
    const action = state.activeAction;
    if (!action) return;
    if (action.heavy && !allowHeavy.checked) {
      showLocalFailure("Large / heavy解析の明示確認が必要です。", "confirmation_required");
      return;
    }
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
          values: collectValues(),
          allow_heavy: allowHeavy.checked,
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
  cancelButton.addEventListener("click", () => state.controller?.abort());
  el("close-panel").addEventListener("click", () => runPanel.classList.add("hidden"));
  loadCatalog().catch((error) => {
    health.textContent = "Unavailable";
    health.className = "status-chip failure";
    showLocalFailure(error.message || String(error));
  });
})();
