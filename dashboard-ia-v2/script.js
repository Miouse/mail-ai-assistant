// Récupération des éléments du DOM
const runBtn           = document.getElementById("runBtn");
const limitEl          = document.getElementById("limit");
const modelEl          = document.getElementById("model");
const filterEl         = document.getElementById("filter");
const terminal         = document.getElementById("terminal");
const report           = document.getElementById("report");
const loadingIndicator = document.getElementById("loadingIndicator");

// -----------------------------
// Gestion du loading
// -----------------------------
function setLoading(isLoading) {
    if (isLoading) {
        loadingIndicator.classList.remove("hidden");
        runBtn.disabled = true;
        runBtn.textContent = "Analyse…";
    } else {
        loadingIndicator.classList.add("hidden");
        runBtn.disabled = false;
        runBtn.textContent = "Lancer l'analyse";
    }
}

// -----------------------------
// Formatage du terminal (logs IA)
// -----------------------------
function formatTerminalOutput(raw) {
    if (!raw) return "";

    // Échapper le HTML pour éviter l'injection
    const safe = raw
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    const lines = safe.split(/\r?\n/);
    let html = "";

    for (let line of lines) {
        const trimmed = line.trim();

        if (trimmed === "") {
            html += "<div class=\"t-line\">&nbsp;</div>";
            continue;
        }

        // Ligne de commande ">>> Exécution : ..."
        if (trimmed.startsWith(">>>")) {
            html += `<div class="t-line t-cmd">${trimmed}</div>`;
            continue;
        }

        // Titre de section "== Rapport IA (locale) =="
        if (trimmed.startsWith("==") && trimmed.endsWith("==")) {
            html += `<div class="t-line t-title">${trimmed}</div>`;
            continue;
        }

        // [INFO] ...
        if (trimmed.startsWith("[INFO]")) {
            const content = trimmed.replace("[INFO]", "").trim();
            html += `<div class="t-line">
                <span class="t-badge t-info">INFO</span>${content}
            </div>`;
            continue;
        }

        // [IA] ...
        if (trimmed.startsWith("[IA]")) {
            const content = trimmed.replace("[IA]", "").trim();
            html += `<div class="t-line">
                <span class="t-badge t-ia">IA</span>${content}
            </div>`;
            continue;
        }

        // [ERREUR IA] ou [ERREUR] ...
        if (trimmed.startsWith("[ERREUR IA]") || trimmed.startsWith("[ERREUR]") || trimmed.startsWith("[ERROR]")) {
            const content = trimmed.replace(/^\[.*?\]\s*/, "");
            html += `<div class="t-line">
                <span class="t-badge t-error">ERREUR</span>${content}
            </div>`;
            continue;
        }

        // Autres lignes : texte normal
        html += `<div class="t-line">${trimmed}</div>`;
    }

    return html;
}

// -----------------------------
// Conversion simple Markdown → HTML pour le rapport IA
// (bold, paragraphes, listes, titres de base)
// -----------------------------
function markdownToHtml(md) {
    if (!md) return "<p>(Rapport IA vide.)</p>";

    // Échapper le HTML
    let text = md
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Titres ###, ##, #
    text = text.replace(/^### (.*)$/gm, "<h3>$1</h3>");
    text = text.replace(/^## (.*)$/gm, "<h2>$1</h2>");
    text = text.replace(/^# (.*)$/gm, "<h1>$1</h1>");

    // Gras **texte**
    text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Listes à puces
    const lines = text.split(/\r?\n/);
    let html = "";
    let inList = false;

    for (let line of lines) {
        const trimmed = line.trim();

        if (/^[-*]\s+/.test(trimmed)) {
            if (!inList) {
                html += "<ul>";
                inList = true;
            }
            html += "<li>" + trimmed.replace(/^[-*]\s+/, "") + "</li>";
        } else {
            if (inList) {
                html += "</ul>";
                inList = false;
            }
            if (trimmed === "") {
                html += "<br>";
            } else {
                html += "<p>" + trimmed + "</p>";
            }
        }
    }
    if (inList) {
        html += "</ul>";
    }

    return html;
}

// -----------------------------
// Click sur "Lancer l'analyse"
// -----------------------------
if (runBtn) {
    runBtn.addEventListener("click", async () => {
        const limit  = (limitEl && limitEl.value)  ? limitEl.value  : "20";
        const model  = (modelEl && modelEl.value)  ? modelEl.value  : "qwen2.5";
        const filter = (filterEl && filterEl.value) ? filterEl.value : "all";

        setLoading(true);
        terminal.innerHTML = '<div class="t-line">Analyse en cours…</div>';
        report.innerHTML = "<p>Analyse en cours…</p>";

        try {
            const formData = new FormData();
            formData.append("limit",  limit);
            formData.append("model",  model);
            formData.append("filter", filter);

            const res = await fetch("api.php", {
                method: "POST",
                body: formData,
            });

            if (!res.ok) {
                const text = await res.text();
                terminal.innerHTML = formatTerminalOutput("[ERREUR] Réponse HTTP " + res.status + " : " + text);
                report.innerHTML = "<p>Impossible de récupérer le rapport (erreur HTTP).</p>";
                return;
            }

            const data = await res.json();
            const fullOutput = data.output || "";

            // On garde la commande en haut du terminal si dispo
            let rawTerminal = "";
            if (data.cmd) {
                rawTerminal += ">>> " + data.cmd + "\n\n";
            }

            // On coupe la sortie en deux blocs : logs / rapport IA
            const parts = fullOutput.split("== Rapport IA (locale) ==");

            rawTerminal += parts[0] || "";
            terminal.innerHTML = formatTerminalOutput(rawTerminal);

            if (parts[1]) {
                // On remet le marqueur pour le rapport
                const reportBlock = "== Rapport IA (locale) ==" + parts[1];
                report.innerHTML = markdownToHtml(reportBlock);
            } else {
                report.innerHTML = "<p>(Aucun bloc de rapport IA trouvé dans la sortie.)</p>";
            }
        } catch (e) {
            console.error("Erreur fetch API:", e);
            terminal.innerHTML = formatTerminalOutput("[ERREUR] Erreur lors de l'appel à l'API PHP : " + e);
            report.innerHTML = "<p>Impossible de récupérer le rapport.</p>";
        } finally {
            setLoading(false);
        }
    });
}
