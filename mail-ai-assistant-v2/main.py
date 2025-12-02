import os
import sys
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import requests
import argparse
from html import unescape
import re
import time
import threading

# 👉 utilisation de notre builder de prompt
from prompts import build_mail_analysis_prompt

# === IMPORTANT : forcer une sortie UTF-8 tolérante (évite les UnicodeEncodeError) ===
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def decode_mime_header(value: str) -> str:
    """
    Certaines parties des emails (sujet, nom de l'expéditeur)
    peuvent être encodées de façon bizarre (ex: =?UTF-8?Q?...?=).
    Cette fonction les remet en texte lisible.
    """
    if not value:
        return ""
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def html_to_text(html: str) -> str:
    """
    Convertit un contenu HTML en texte brut raisonnablement propre.
    (Actuellement plus utilisé, mais conservé au cas où on réactive le body un jour.)
    """
    if not html:
        return ""

    # Décode les entités HTML (&eacute;, &amp;, etc.)
    text = unescape(html)

    # Supprime les blocs <script> et <style>
    text = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", " ", text)

    # Supprime toutes les balises HTML restantes
    text = re.sub(r"(?s)<[^>]+>", " ", text)

    # Compacte les espaces / retours lignes
    text = re.sub(r"\s+", " ", text).strip()

    return text


def fetch_last_emails(limit: int = 20, email_filter: str = "all"):
    """
    Se connecte au serveur IMAP, récupère des emails selon le filtre demandé,
    et renvoie une liste de dictionnaires avec :
      - id
      - from
      - subject
      - date

    ⚠️ Le body n'est volontairement plus récupéré pour alléger le contexte IA.
    """

    host = os.getenv("IMAP_HOST")
    port = int(os.getenv("IMAP_PORT", "993"))
    username = os.getenv("IMAP_EMAIL")
    password = os.getenv("IMAP_PASSWORD")

    if not host or not username or not password:
        raise ValueError(
            "IMAP_HOST, IMAP_EMAIL ou IMAP_PASSWORD manquent dans le fichier .env"
        )

    print(f"[INFO] Connexion à {host}:{port} ...")
    mail = imaplib.IMAP4_SSL(host, port)

    try:
        mail.login(username, password)
    except imaplib.IMAP4.error as e:
        print("[ERREUR] Impossible de se connecter (login IMAP).")
        print("Vérifie l'email, le mot de passe d'application ou les paramètres IMAP.")
        print(e)
        return []

    status, _ = mail.select("INBOX")
    if status != "OK":
        print("[ERREUR] Impossible de sélectionner le dossier INBOX.")
        mail.logout()
        return []

    # Choix du critère IMAP en fonction du filtre
    if email_filter == "unread":
        search_criteria = "UNSEEN"
    else:
        search_criteria = "ALL"

    print(f"[INFO] Filtre IMAP utilisé : {search_criteria}")
    status, data = mail.search(None, search_criteria)
    if status != "OK":
        print(
            f"[ERREUR] Impossible de récupérer la liste des emails avec le filtre : {search_criteria}."
        )
        mail.logout()
        return []

    mail_ids = data[0].split()
    if not mail_ids:
        print("[INFO] Aucun email trouvé avec ce filtre.")
        mail.logout()
        return []

    # On prend les 'limit' derniers emails correspondant au filtre
    last_ids = mail_ids[-limit:]

    emails = []

    for num in reversed(last_ids):  # du plus récent au plus ancien
        status, msg_data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            print(f"[WARN] Impossible de récupérer l'email ID {num}.")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_mime_header(msg.get("Subject"))
        from_ = decode_mime_header(msg.get("From"))
        date_ = msg.get("Date") or ""

        # ⚠️ On ne récupère plus le body : on reste uniquement sur les métadonnées
        emails.append(
            {
                "id": num.decode(),
                "from": from_,
                "subject": subject,
                "date": date_,
            }
        )

    mail.logout()
    return emails


def build_email_context(emails):
    """
    Format texte simple (utile si on veut afficher la liste brute en console).
    """
    lines = []
    for i, em in enumerate(emails, start=1):
        lines.append(f"Email #{i}")
        lines.append(f"De    : {em.get('from', '')}")
        lines.append(f"Date  : {em.get('date', '')}")
        lines.append(f"Sujet : {em.get('subject', '')}")
        lines.append("")
    return "\n".join(lines)


def summarize_with_local_ai(prompt: str, model: str) -> str:
    """
    Appel IA avec timeout. Le timer d'affichage est désactivé pour le moment.
    """

    print(f"[INFO] Appel au modèle IA '{model}'...")

    result_container = {"response": None, "error": None}

    # Temps limite en secondes
    TIMEOUT = 45

    # --- THREAD : appel Ollama ---
    def call_ollama():
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=TIMEOUT
            )
            response.raise_for_status()
            result_container["response"] = response.json().get("response", "").strip()
        except Exception as e:
            result_container["error"] = str(e)

    # Lancement du thread IA
    t = threading.Thread(target=call_ollama)
    t.start()

    # --- TIMER (désactivé en affichage) ---
    start = time.time()
    elapsed = 0

    while t.is_alive() and elapsed < TIMEOUT:
        time.sleep(1)
        elapsed = int(time.time() - start)
        # print(f"[IA] Temps écoulé : {elapsed} s")  # Timer désactivé

    # Si dépasse timeout → stop
    if elapsed >= TIMEOUT and t.is_alive():
        return (
            f"[ERREUR IA] Le modèle '{model}' n'a pas répondu en {TIMEOUT} secondes.\n"
            "💡 Conseil : essaye avec moins d'emails ou un modèle plus léger (qwen2.5, phi3)."
        )

    # Si erreur dans Ollama
    if result_container["error"]:
        return f"[ERREUR IA] {result_container['error']}"

    # Réponse OK
    return result_container["response"]


def main():
    parser = argparse.ArgumentParser(description="Assistant mail IA")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Nombre d'emails à analyser (par défaut: 20)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="deepseek-r1",
        help="Modèle IA Ollama à utiliser (ex: deepseek-r1, qwen2.5, mistral-nemo, llama3.2:latest)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default="all",
        choices=["all", "unread"],
        help="Filtre d'emails : 'all' (tous) ou 'unread' (non lus uniquement)",
    )
    args = parser.parse_args()

    load_dotenv()
    print("=== Assistant mail IA - prototype ===")
    print(f"[INFO] Nombre d'emails analysés demandé : {args.limit}")
    print(f"[INFO] Modèle IA utilisé : {args.model}")
    print(f"[INFO] Filtre emails : {args.filter}")

    emails = fetch_last_emails(limit=args.limit, email_filter=args.filter)

    if not emails:
        print("Aucun email récupéré avec ces paramètres.")
        return

    print("\n== Derniers emails (filtrés) ==")
    for i, em in enumerate(emails, start=1):
        print(f"\n--- Email #{i} ---")
        print(f"De    : {em['from']}")
        print(f"Sujet : {em['subject']}")
        print(f"Date  : {em['date']}")
        # On n'affiche plus d'extrait de body, puisqu'on ne le récupère plus.

    print("\n== Rapport IA (locale) ==\n")

    # Construction du prompt façon assistant exécutif pour Alex
    prompt = build_mail_analysis_prompt(emails, user_name="Alex")

    # Envoi au modèle IA
    report = summarize_with_local_ai(prompt, args.model)
    print(report)

    print(
        "\nOK, on lit les mails, on applique le filtre et on génère un rapport IA pour aider à les lire et les prioriser ✅"
    )


if __name__ == "__main__":
    main()
