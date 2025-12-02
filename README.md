# 📧 Mail AI Assistant (Local)

Projet simple permettant de récupérer des emails via IMAP, de les analyser avec un modèle IA local (Ollama), et d'afficher un rapport depuis un dashboard web.

> ⚠️ **Note importante**  
> Ce projet n'est pas un assistant avancé : il a été réalisé en une seule nuit, par curiosité, pour tester ce que pouvait faire une IA locale.  
> Les IA locales restent très limitées : compréhension faible, hallucinations possibles, incapacité à gérer un email complet (pas de body) et analyse approximative.

---

## 📁 Structure du projet

```
mail-ai-assistant/
│
├── main.py
├── prompts.py
├── .env
│
├── dashboard-ia/
│   ├── index.php
│   ├── api.php
│   ├── script.js
│   ├── style.css
│   └── assets/
│
└── README.md
```

**Organisation :**
- ✔ Placer les fichiers Python dans : `mail-ai-assistant/`
- ✔ Placer le dossier `dashboard-ia` dans : `C:/wamp64/www/`

---

## ⚙️ Installation

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/<username>/mail-ai-assistant
cd mail-ai-assistant
```

### 2️⃣ Créer un environnement virtuel

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Installer Ollama

Télécharger et installer Ollama : [https://ollama.com/download](https://ollama.com/download)

```bash
ollama pull qwen2.5
```

### 5️⃣ Configurer les identifiants IMAP

Créer un fichier `.env` à la racine du projet :

```env
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_EMAIL=ton.email@gmail.com
IMAP_PASSWORD=mot_de_passe_application
```

> 💡 **Pour Gmail** : Utiliser un [mot de passe d'application](https://support.google.com/accounts/answer/185833)

---

## 🚀 Utilisation

### 📟 En ligne de commande

```bash
python main.py --limit 10 --model qwen2.5 --filter unread
```

**Options disponibles :**
- `--limit` : Nombre d'emails à analyser (défaut : 10)
- `--model` : Modèle Ollama à utiliser (défaut : qwen2.5)
- `--filter` : Filtre IMAP (`all`, `unread`, `seen`, etc.)

---

### 🌐 Avec interface web (WAMP)

#### 1️⃣ Copier le dashboard

```bash
# Copier le dossier dashboard-ia dans :
C:/wamp64/www/dashboard-ia/
```

#### 2️⃣ Lancer WAMP

- Démarrer WAMP
- Vérifier que tous les services sont au vert

#### 3️⃣ Accéder au dashboard

Ouvrir dans le navigateur :

```
http://localhost/dashboard-ia/
```

#### 4️⃣ Lancer l'analyse

- Choisir le modèle IA
- Définir le nombre d'emails
- Choisir le filtre
- Cliquer sur "🚀 Lancer l'analyse"

---

## ⚠️ Limitations importantes

- ❌ **IA locale peu fiable** : Qwen2.5 et autres modèles locaux ont des capacités limitées
- ❌ **Analyse superficielle** : Pas de compréhension approfondie du contexte
- ❌ **Pas de body complet** : Limitation technique IMAP
- ❌ **Résultats approximatifs** : Hallucinations possibles
- ❌ **Projet expérimental** : Réalisé en une nuit, non optimisé pour la production

---

## 🛠️ Technologies utilisées

- **Python 3.x** : Backend et traitement
- **Ollama** : Modèles IA locaux
- **IMAP** : Récupération des emails
- **PHP** : Interface web (dashboard)
- **JavaScript** : Interactions frontend
- **WAMP** : Serveur local (Windows)

---

## 📝 Modèles IA recommandés

| Modèle | Taille | Performance | Recommandation |
|--------|--------|-------------|----------------|
| `qwen2.5` | ~7B | ⭐⭐⭐ | Recommandé |
| `mistral` | ~7B | ⭐⭐⭐ | Alternatif |
| `phi3` | ~3B | ⭐⭐ | Rapide mais moins précis |
| `deepseek-r1` | ~7B | ⭐⭐⭐ | Bon pour analyse |

Installation d'un modèle :
```bash
ollama pull nom_du_modele
```

---

## 🐛 Dépannage

### 1️⃣ Le dashboard ne s'affiche pas

**Checklist rapide :**

1. **Vérifie WAMP**
   * Icône WAMP dans la barre → doit être verte
   * Si orange/rouge → clic gauche → `Restart All Services`

2. **Vérifie l'emplacement du dossier**
   * Ton projet web doit être là : `C:\wamp64\www\dashboard-ia\index.php`
   * Donc dans l'explorateur Windows tu dois voir : `C:\wamp64\www\dashboard-ia\index.php`

3. **URL dans le navigateur**
   * Tape exactement : `http://localhost/dashboard-ia/`
   * Si tu as mis un autre nom de dossier, adapte l'URL.

4. **Erreur "Not Found" / page blanche**
   * Vérifie que le fichier `index.php` existe bien dans `dashboard-ia`
   * Essaie aussi : `http://localhost/dashboard-ia/index.php`

5. **Si tu as une erreur PHP**
   * Regarde le message affiché (genre "Fatal error …")
   * Ça vient souvent d'un `require` manquant ou d'une faute de syntaxe.

---

### 2️⃣ Erreur de connexion IMAP

**Les causes les plus courantes :**

1. **Mauvais identifiants dans `.env`**
   
   Vérifie :
   ```env
   IMAP_HOST=imap.gmail.com
   IMAP_PORT=993
   IMAP_EMAIL=ton.email@gmail.com
   IMAP_PASSWORD=mot_de_passe_application
   ```
   * Pas d'espace, pas de guillemets.

2. **Tu utilises un mot de passe normal Gmail**
   * Sur Gmail, il faut un mot de passe d'application, pas ton mot de passe habituel.
   * Dans ton compte Google → Sécurité → Mots de passe d'application → générer → coller dans `IMAP_PASSWORD`.

3. **IMAP pas activé côté fournisseur**
   * Pour Gmail : Paramètres → Transfert et POP/IMAP → activer IMAP.

4. **Message d'erreur classique**
   * Si tu vois : `imaplib.IMAP4.error: b'[AUTHENTICATIONFAILED] ...'` → c'est presque toujours un problème d'identifiants ou de mot de passe d'application.

5. **Tester vite fait**
   * Ajoute un `print(host, username)` dans `main.py` avant la connexion pour vérifier que `.env` est bien lu.

---

### 3️⃣ Ollama ne répond pas

**Cas typiques :**

#### 🔹 Cas A : le serveur n'est pas lancé

**Symptômes :**
* Erreur type : `ConnectionError: [Errno 111] Connection refused`
* Ou `[ERREUR IA] HTTPConnectionPool ...`

**À faire :**
```bash
ollama serve
```
Laisse cette fenêtre ouverte, puis relance ton script.

#### 🔹 Cas B : mauvais modèle / modèle non installé

**Symptômes :**
* Erreur 404 ou message genre : `model not found`
* Tu appelles `qwen2.5` mais tu ne l'as jamais installé

**Vérifie les modèles dispo :**
```bash
ollama list
```

**Installe le modèle si besoin :**
```bash
ollama pull qwen2.5
```

**Et teste :**
```bash
ollama run qwen2.5 "Dis bonjour en un mot."
```
Si ça répond → le modèle est OK.

#### 🔹 Cas C : port déjà occupé / Ollama planté

**Symptômes :**
* `Error: listen tcp 127.0.0.1:11434: bind: ...`
* Tu as plusieurs Ollama qui tournent

**Solution :**

1. Voir qui utilise le port 11434 :
   ```bash
   netstat -ano | findstr 11434
   ```

2. Tu récupères le PID (dernier nombre sur la ligne), puis :
   ```bash
   taskkill /PID <PID> /F
   ```

3. Relance :
   ```bash
   ollama serve
   ```

---



**Fait le en une nuit, par curiosité**
