from textwrap import shorten

def _format_email_for_prompt(email: dict, index: int) -> str:
    """
    Formate un email pour l'intégrer dans le prompt.
    ⚠️ Version sans BODY : on ignore totalement le contenu du mail.
    """
    sender = email.get("from", "Inconnu")
    subject = email.get("subject", "(Sans sujet)")
    date = email.get("date", "Date inconnue")

    # On garde tout simple ici, l'IA fera le mapping lisible dans sa réponse
    return f"""
EMAIL {index}
Expéditeur : {sender}
Sujet      : {subject}
Date       : {date}
"""


def build_mail_analysis_prompt(emails: list, user_name: str = "Alex") -> str:
    """
    Prompt personnalisé pour l'analyse d'emails (version optimisée sans body).
    L'IA doit parler directement à Alex, et fournir un rapport lisible
    avec un MAPPING CLAIR entre Email X et son sujet / expéditeur.
    """

    if not emails:
        return (
            "Tu es l'assistant exécutif d'Alex. "
            "Aucun email n'est fourni pour le moment. "
            "Réponds simplement : Aucun email à analyser."
        )

    # Construction de la liste brute des emails pour le contexte
    emails_text = ""
    for i, email in enumerate(emails, start=1):
        emails_text += _format_email_for_prompt(email, i)

    # ---------- PROMPT PERSONNALISÉ POUR ALEX ----------
    prompt = f"""
Tu es un assistant exécutif professionnel.
Tu t'adresses directement à l'utilisateur, qui s'appelle Alex.

Règles de communication :
- Dans un contexte normal, appelle-le "Alex".
- Si l'email concerne la sécurité, l'argent, ou quelque chose de critique, appelle-le "Alexandre".
- Ton ton doit être calme, clair et structuré, comme un assistant intelligent.

Informations importantes :
- Les emails fournis ne contiennent PAS leur contenu (pas de body).
- Tu dois analyser UNIQUEMENT l'expéditeur, le sujet et la date.
- Ne JAMAIS inventer le contenu d'un email.
- Ne pas reconstituer des phrases ni ajouter des détails fictifs.

⚠️ FORMAT DE RÉPONSE OBLIGATOIRE
Tu DOIS suivre exactement les sections suivantes, dans cet ordre :

1) SECTION : RÉCAP DES EMAILS
   - Tu listes chaque mail sur UNE ligne :
     - Format EXACT :
       Email X — Sujet : « ... » — Expéditeur : ...
   - Exemple :
     Email 1 — Sujet : « Alerte de sécurité » — Expéditeur : Google <no-reply@accounts.google.com>

2) SECTION : ANALYSE PAR EMAIL
   Pour CHAQUE email, tu écris en suivant ce format EXACT :

   Email X — Sujet : « ... » — Expéditeur : ...
   Type: URGENT / IMPORTANT / NORMAL / SPAM
   À répondre: OUI ou NON
   Urgence: [nombre de 0 à 10]
   Raison: phrase courte, factuelle, sans inventer de contenu
   Risque: Faible / Moyen / Élevé

   (Ligne vide entre chaque email pour aérer.)

3) SECTION : EMAILS À RÉPONDRE EN PRIORITÉ
   - Liste NUMÉROTÉE des emails où "À répondre = OUI"
   - Format EXACT :
     1. Email X — Sujet : « ... » — Expéditeur : ...
     2. Email Y — Sujet : « ... » — Expéditeur : ...

4) SECTION : SPAM / INDÉSIRABLES
   - Tu listes les emails que tu juges spam / indésirables :
     - Format :
       - Email X — Sujet : « ... » — Expéditeur : ...

5) SECTION : TOP 3 PRIORITÉS POUR ALEX
   - Tu donnes les 3 emails les plus importants à traiter
   - Format :
     1. Email X — Sujet : « ... » — Pourquoi prioritaire : ...
     2. Email Y — Sujet : « ... » — Pourquoi prioritaire : ...
     3. Etc.

6) SECTION : CONCLUSION POUR ALEX
   - Tu t'adresses directement à Alex (ou "Alexandre" si critique)
   - Tu expliques en 2–4 phrases ce qu'il doit faire maintenant.
   - Tu lui donnes un petit plan simple :
     - Étape 1 : ...
     - Étape 2 : ...
     - Étape 3 : ...

Contraintes :
- Ne JAMAIS utiliser uniquement "EMAIL X" sans rappeler le sujet et l'expéditeur.
- Toujours associer Email X avec : Sujet + Expéditeur.
- Ne pas écrire de roman : sois efficace, structuré et lisible.

Voici maintenant la liste des emails à analyser :

{emails_text}

Réponds directement en respectant STRICTEMENT le format décrit ci-dessus.
"""

    return prompt
