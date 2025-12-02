import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
from collections import Counter
from datetime import datetime


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


def fetch_last_emails(limit: int = 10):
    """
    Se connecte au serveur IMAP, récupère les 'limit' derniers emails,
    et renvoie une liste de dictionnaires avec from / subject / date.
    """
    host = os.getenv("IMAP_HOST")
    port = int(os.getenv("IMAP_PORT", "993"))
    username = os.getenv("IMAP_EMAIL")
    password = os.getenv("IMAP_PASSWORD")

    # Vérification des variables d'environnement
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

    # On sélectionne la boîte de réception principale
    status, _ = mail.select("INBOX")
    if status != "OK":
        print("[ERREUR] Impossible de sélectionner le dossier INBOX.")
        mail.logout()
        return []

    # On récupère tous les IDs des emails
    status, data = mail.search(None, "ALL")
    if status != "OK":
        print("[ERREUR] Impossible de récupérer la liste des emails.")
        mail.logout()
        return []

    mail_ids = data[0].split()
    if not mail_ids:
        print("[INFO] Aucun email trouvé dans cette boîte.")
        mail.logout()
        return []

    # On prend les 'limit' derniers emails
    last_ids = mail_ids[-limit:]

    emails = []

    # reversed() pour afficher du plus récent au plus ancien
    for num in reversed(last_ids):
        status, msg_data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            print(f"[WARN] Impossible de récupérer l'email ID {num}.")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_mime_header(msg.get("Subject"))
        from_ = decode_mime_header(msg.get("From"))
        date_ = msg.get("Date") or ""

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


def generate_report(emails):
    """
    Génère un petit rapport texte à partir de la liste d'emails.
    C'est notre version 'v0' du rapport automatique.
    """
    if not emails:
        return "Aucun email à analyser."

    # Nombre total d'emails
    total = len(emails)

    # Période couverte (on suppose que emails est déjà trié du plus récent au plus ancien)
    dates = [em["date"] for em in emails if em.get("date")]
    periode = ""
    if dates:
        premiere = dates[-1]
        derniere = dates[0]
        periode = f"Du {premiere} au {derniere}"

    # Expéditeurs les plus fréquents
    senders = [em["from"] for em in emails if em.get("from")]
    sender_counts = Counter(senders)
    top_senders = sender_counts.most_common(5)

    # Construction du rapport
    lines = []
    lines.append("=== RAPPORT AUTOMATIQUE DES EMAILS ===")
    lines.append(f"Nombre d'emails analysés : {total}")
    if periode:
        lines.append(f"Période couverte         : {periode}")
    lines.append("")
    lines.append("Expéditeurs les plus fréquents :")
    for sender, count in top_senders:
        lines.append(f"  - {sender} : {count} email(s)")

    lines.append("")
    lines.append("Liste des sujets récents :")
    for em in emails:
        lines.append(f"  - {em['subject']} (par {em['from']})")

    lines.append("")
    lines.append("Fin du rapport ✅")

    return "\n".join(lines)


def main():
    # Charge le .env (IMAP_HOST, IMAP_EMAIL, etc.)
    load_dotenv()
    print("=== Assistant mail IA - prototype ===")

    emails = fetch_last_emails(limit=100)

    if not emails:
        print("Aucun email récupéré.")
        return

    print("\n== Derniers emails ==")
    for i, em in enumerate(emails, start=1):
        print(f"\n--- Email #{i} ---")
        print(f"De    : {em['from']}")
        print(f"Sujet : {em['subject']}")
        print(f"Date  : {em['date']}")

    print("\n== Rapport automatique ==\n")
    report = generate_report(emails)
    print(report)

    print("\nOK, on arrive à lire les mails et à faire un premier rapport ✅")


if __name__ == "__main__":
    main()
