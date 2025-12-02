<?php

header("Content-Type: application/json; charset=utf-8");

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    http_response_code(405);
    echo json_encode([
        "ok" => false,
        "error" => "Méthode non autorisée"
    ]);
    exit;
}

// Récup paramètres depuis le formulaire
$limit  = intval($_POST["limit"] ?? 10);
$model  = $_POST["model"] ?? "qwen2.5";
$filter = $_POST["filter"] ?? "all";

// Dossier du projet Python
$projectDir = 'C:\Users\larai\Documents\mail-ai-assistant';

// On se place dans ce dossier
if (!is_dir($projectDir)) {
    echo json_encode([
        "ok"    => false,
        "error" => "Dossier projet introuvable : {$projectDir}"
    ]);
    exit;
}
chdir($projectDir);

// Python du venv si dispo
$python = $projectDir . '\.venv\Scripts\python.exe';
if (!file_exists($python)) {
    $python = 'python'; // fallback global
}

// Chemin vers main.py
$mainScript = $projectDir . '\main.py';
if (!file_exists($mainScript)) {
    echo json_encode([
        "ok"    => false,
        "error" => "main.py introuvable dans {$projectDir}"
    ]);
    exit;
}

// On échappe le modèle et le filtre pour la ligne de commande
$modelEsc  = escapeshellarg($model);
$filterEsc = escapeshellarg($filter);

// Commande complète
$cmd = "\"{$python}\" \"{$mainScript}\" --limit {$limit} --model {$modelEsc} --filter {$filterEsc} 2>&1";

// Exécution
$output = shell_exec($cmd);

if ($output === null) {
    echo json_encode([
        "ok"    => false,
        "cmd"   => $cmd,
        "error" => "La commande n'a renvoyé aucune sortie (shell_exec null)."
    ]);
    exit;
}

echo json_encode([
    "ok"     => true,
    "cmd"    => $cmd,
    "output" => $output
]);
