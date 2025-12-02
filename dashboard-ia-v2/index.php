<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8" />
    <title>Dashboard Mail IA - Miouse Labs</title>
    <link rel="stylesheet" href="style.css" />
</head>
<body>
    <div class="layout">

        <!-- Header -->
        <header class="topbar">
            <div>
                <h1>📨 Mail IA Dashboard</h1>
                <p class="subtitle">
                    Assistant local pour analyser et prioriser tes emails.
                </p>
            </div>
            <div class="badge-brand">
                Miouse Labs
            </div>
        </header>

        <main class="grid">

            <!-- Carte de configuration -->
            <section class="card">
                <h2>Paramètres d'analyse</h2>
                <p class="card-subtitle">
                    Choisis le modèle, le nombre d'emails et le filtre à appliquer.
                </p>

                <div class="form-group">
                    <label for="limit">Nombre d'emails à analyser</label>
                    <input type="number" id="limit" min="1" max="50" value="10" />
                </div>

                <div class="form-group">
                    <label for="model">Modèle IA</label>
                    <select id="model">
                        <option value="qwen2.5">qwen2.5 (recommandé)</option>
                        <option value="phi3">phi3</option>
                        <option value="mistral-nemo">mistral-nemo</option>
                        <option value="deepseek-r1:latest">deepseek-r1:latest</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="filter">Filtre d'emails</label>
                    <select id="filter">
                        <option value="all">Tous les emails</option>
                        <option value="unread">Non lus uniquement</option>
                    </select>
                </div>

                <button id="runBtn" class="btn-primary">
                    Lancer l'analyse
                </button>

                <div id="loadingIndicator" class="loading hidden">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span>Analyse en cours…</span>
                </div>
            </section>

            <!-- Terminal brut -->
            <section class="card">
                <h2>Terminal</h2>
                <p class="card-subtitle">
                    Logs de l'exécution Python, appels IA, timer, erreurs éventuelles.
                </p>
                <div id="terminal" class="terminal">
                    <div class="t-line">En attente d'exécution…</div>
                </div>
            </section>

            <!-- Rapport IA -->
            <section class="card card-full">
                <h2>Rapport IA</h2>
                <p class="card-subtitle">
                    Synthèse lisible générée par l'IA à partir des emails analysés.
                </p>
                <div id="report" class="report">
                    <p>Aucun rapport généré pour l’instant.</p>
                </div>
            </section>

            <!-- Carte info modèles (optionnelle mais cool) -->
            <section class="card card-full">
                <h2>Modèles IA disponibles</h2>
                <p class="card-subtitle">
                    Quelques repères pour choisir le bon modèle selon le contexte.
                </p>

                <div class="model-grid">
                    <div class="model-card">
                        <div class="model-header">
                            <span class="model-name">qwen2.5</span>
                            <span class="model-tag model-tag-reco">Recommandé</span>
                        </div>
                        <p class="model-desc">
                            Très bon respect des consignes, idéal pour classer les emails et décider à quoi répondre en priorité.
                        </p>
                        <ul class="model-list">
                            <li>Tri des emails importants</li>
                            <li>Priorisation + urgence</li>
                            <li>Assistant “Jarvis” fiable</li>
                        </ul>
                    </div>

                    <div class="model-card">
                        <div class="model-header">
                            <span class="model-name">phi3</span>
                            <span class="model-tag">Léger</span>
                        </div>
                        <p class="model-desc">
                            Modèle rapide et peu gourmand, bon pour des rapports simples et des machines modestes.
                        </p>
                        <ul class="model-list">
                            <li>Très rapide</li>
                            <li>Idéal tests rapides</li>
                            <li>Tri simple des notifications</li>
                        </ul>
                    </div>

                    <div class="model-card">
                        <div class="model-header">
                            <span class="model-name">mistral-nemo</span>
                            <span class="model-tag">Pro</span>
                        </div>
                        <p class="model-desc">
                            Bonne structure et ton professionnel, adapté aux emails clients / business.
                        </p>
                        <ul class="model-list">
                            <li>Ton corporate</li>
                            <li>Rapports propres</li>
                            <li>Bonne cohérence</li>
                        </ul>
                    </div>

                    <div class="model-card">
                        <div class="model-header">
                            <span class="model-name">deepseek-r1</span>
                            <span class="model-tag model-tag-warning">Analyse</span>
                        </div>
                        <p class="model-desc">
                            Excellent pour le raisonnement profond, moins discipliné pour des formats stricts avec beaucoup d'emails.
                        </p>
                        <ul class="model-list">
                            <li>Analyse détaillée d’un email</li>
                            <li>Questions complexes</li>
                            <li>À éviter pour 20 mails d'un coup</li>
                        </ul>
                    </div>
                </div>
            </section>

        </main>
    </div>

    <script src="script.js"></script>
</body>
</html>
