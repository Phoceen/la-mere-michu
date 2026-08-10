import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from knowledge_base import get_prompt_context
from rules import split_sentences

load_dotenv()

SCIENCE_CONTEXT = get_prompt_context()


def _tag_sentences(text: str, prefix: str) -> str:
    """Injecte des ID tags [#L1], [#P1] etc. au début de chaque phrase."""
    sentences = split_sentences(text)
    return "\n".join(f"[#{prefix}{i}] {s}" for i, s in enumerate(sentences, 1))


def get_client() -> Anthropic | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "sk-ant-...":
        return None
    return Anthropic(api_key=api_key)


def _build_system_prompt(has_lancement: bool, has_papier: bool, papier_type: str) -> str:
    zones_desc = []
    if has_lancement:
        zones_desc.append("- Lancement : accroche courte, donne envie d'écouter")
    if has_papier:
        if papier_type == "Papier":
            zones_desc.append("- Papier : fluide, bien rythmé, transitions claires")
        else:
            zones_desc.append("- Q/R avec relances : réponses autonomes, relances naturelles")

    coherence_block = ""
    if has_lancement and has_papier:
        coherence_block = """
MANDAT C — COHÉRENCE LANCEMENT / PAPIER :
- Le lancement correspond-il au contenu du papier/QR ?
- Y a-t-il des répétitions textuelles entre les deux ?
- Le lancement donne-t-il envie d'écouter la suite ?
Remplis le champ "coherence" (2-3 phrases max). Si un seul texte, mets null."""

    # Construire le schéma JSON dynamiquement
    zones_parts = []
    phrase_schema = '{{"id":"#XX","original":"...","verdict":"ok|a_verifier|probleme","regard_redac":"...","regard_auditeur":"...","score_incarnation":"VIF|FLOU|GRIS","suggestion":"... ou null"}}'
    if has_lancement:
        zones_parts.append(f'"lancement": {{"forme": [{phrase_schema}]}}')
    if has_papier:
        key = "papier" if papier_type == "Papier" else "qr"
        zones_parts.append(f'"{key}": {{"forme": [{phrase_schema}]}}')
    zones_schema = ", ".join(zones_parts)

    return f"""Tu es un relecteur expert de scripts radio (20 ans d'antenne), formé aux neurosciences de l'écoute.

Types de texte :
{chr(10).join(zones_desc)}

Tu reçois le texte ET le résultat des règles mécaniques déjà appliquées (longueur, voix passive, mots complexes, parenthèses, double négation, chiffres, sigles, position sérielle, anglicismes, jargon institutionnel mesuré). NE RÉPÈTE PAS ces alertes.

Chaque phrase du texte est précédée d'un identifiant entre crochets (ex: [#L1], [#P3]). REPRENDS cet identifiant dans le champ "id" de ta réponse JSON pour chaque phrase. C'est OBLIGATOIRE.

MANDAT A — FORME (style oral), DOUBLE REGARD :
Analyse PHRASE PAR PHRASE uniquement ce que les règles ne détectent pas.
Adopte DEUX perspectives complémentaires :

REGARD 1 — Rédacteur en chef (20 ans d'antenne) :
- Cette phrase est-elle prête pour l'antenne ?
- Rythme, souffle, fluidité orale, enchaînements de sons
- Ambiguïtés sonores, homophones, liaisons problématiques
- Registre : parlé naturel ou écrit lu ?

REGARD 2 — Auditeur naïf (première écoute, en voiture) :
- Qu'est-ce que je comprends en entendant cette phrase une seule fois ?
- Y a-t-il un risque de malentendu ou de décrochage ?
- L'image mentale est-elle immédiate ou faut-il réfléchir ?
- MILIEU DU TEXTE : les phrases au milieu sont dans la zone de creux mémoriel (Glanzer & Cunitz, 1966). Vérifie qu'il y a une relance, une question, un changement de ton ou une image forte pour raccrocher l'auditeur. Si le milieu est plat, signale-le.

MANDAT D — SCORE D'INCARNATION (1 seul mot par phrase) :
Évalue la capacité de chaque phrase à générer une image mentale (théorie du double codage, Paivio).
- VIF : sujet concret, verbe d'action, décor identifiable (ex: "Le boulanger ferme boutique")
- FLOU : sujet institutionnel, jargon léger, peu d'image (ex: "Le secteur connaît des tensions")
- GRIS : langue de bois, abstractions en cascade, chiffres complexes sans contexte (ex: "La mise en œuvre des réformes structurelles")
Remplis le champ "score_incarnation" pour CHAQUE phrase. En cas de doute entre FLOU et GRIS, si la phrase contient 2+ mots abstraits (suffixes -tion, -ité, -isme, -ence), c'est GRIS.

Si une phrase est bonne sur tous ces critères, mets verdict "ok" avec des champs vides (sauf score_incarnation, toujours rempli).

MANDAT E — NOTE DE RELECTURE :
Rédige une note de relecture comme un rédacteur en chef expérimenté qui rend sa copie annotée au journaliste.
C'est un MEMO ÉDITORIAL, pas une liste de bullets. On le lit de haut en bas, comme un texte.

Structure OBLIGATOIRE en 3 sections séparées par des sauts de ligne :

**LE PLUS URGENT** (1-3 paragraphes)
Les problèmes qui empêchent le texte de passer en l'état. Pour chaque problème :
- Cite la phrase ou l'extrait exact entre guillemets
- Explique POURQUOI c'est un problème pour l'oreille (pas pour l'œil)
- Donne une DIRECTION ("coupe après le verbe", "attaque par le concret", "vire le chiffre et remplace par une comparaison") — JAMAIS de réécriture complète

**À SURVEILLER** (1-2 paragraphes)
Ce qui n'est pas bloquant mais qui affaiblit le texte : passages plats, enchaînements qui manquent de souffle, zone de creux au milieu sans relance, registre qui glisse vers l'écrit.

**CE QUI FONCTIONNE** (1 paragraphe)
Ce qui est bon et qu'il faut garder. Images fortes, attaque efficace, rythme qui tient. Sois précis : cite les phrases ou passages qui marchent.

Règles :
- Style direct, tutoiement, ton de rédac chef bienveillant mais exigeant.
- Cite les numéros de phrases (ex: "Ta phrase 3...") et des extraits exacts du texte.
- NE corrige PAS l'orthographe ni la grammaire — ce n'est pas le sujet.
- NE fais PAS de réécriture — donne des directions.
- NE RÉPÈTE PAS les alertes mécaniques déjà signalées (longueur, voix passive, etc.).
- Concentre-toi sur : structure globale, rythme, enchaînements, images mentales, dynamique narrative, registre oral.
- Appuie-toi sur les études scientifiques quand c'est pertinent (cite auteur/institution + année, uniquement des sources de la liste fournie — jamais de source inventée).
- Si tu repères un terme de jargon NON couvert par les règles mécaniques (sigle non développé, périphrase de lieu de pouvoir, terme judiciaire/économique/européen), signale-le dans la note en t'appuyant sur les données mesurées de compréhension.
- Utilise \\n pour les sauts de ligne dans le JSON.
Remplis le champ "note_relecture".

MANDAT B — REPÉRAGE D'ASSERTIONS (fond) :
Identifie TOUTE assertion vérifiable : chiffres précis, noms propres, dates, lieux, faits attribués, citations. Pour chaque assertion, note l'extrait exact et ce que le journaliste devrait vérifier avant antenne.
Tu ne fais PAS de fact-checking. Tu LISTES ce qui mérite vérification.
{coherence_block}

Appuie tes analyses de forme sur les études ci-dessous quand c'est pertinent. Cite la référence (auteur, année).

{SCIENCE_CONTEXT}

Réponds UNIQUEMENT en JSON valide :
{{"note_relecture": "...", "zones": {{{zones_schema}}}, "claims": [{{"extrait":"...","zone":"lancement|papier|qr","type":"chiffre|nom_propre|date|fait|citation","note":"..."}}], "coherence": "... ou null", "impression_generale": "..."}}"""


def _build_user_message(
    lancement_text: str | None,
    lancement_rules: str | None,
    papier_text: str | None,
    papier_rules: str | None,
    papier_type: str,
) -> str:
    parts = []
    if lancement_text:
        parts.append("=== LANCEMENT ===")
        parts.append(_tag_sentences(lancement_text, "L"))
        if lancement_rules:
            parts.append(f"\n{lancement_rules}")
    if papier_text:
        label = "PAPIER" if papier_type == "Papier" else "Q/R AVEC RELANCES"
        parts.append(f"\n=== {label} ===")
        parts.append(_tag_sentences(papier_text, "P"))
        if papier_rules:
            parts.append(f"\n{papier_rules}")
    return "\n".join(parts)


def analyze_with_ai(
    lancement_text: str | None,
    lancement_rules: str | None,
    papier_text: str | None,
    papier_rules: str | None,
    papier_type: str,
) -> dict | None:
    client = get_client()
    if client is None:
        return None

    has_lancement = bool(lancement_text and lancement_text.strip())
    has_papier = bool(papier_text and papier_text.strip())

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            system=_build_system_prompt(has_lancement, has_papier, papier_type),
            messages=[{"role": "user", "content": _build_user_message(
                lancement_text, lancement_rules, papier_text, papier_rules, papier_type
            )}],
        )

        if response.stop_reason == "max_tokens":
            return {"error": "Réponse tronquée (texte trop long). Essayez avec un texte plus court."}

        raw = response.content[0].text.strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            raw = raw[start:end + 1]

        return json.loads(raw)

    except json.JSONDecodeError:
        try:
            last_bracket = raw.rfind("]")
            if last_bracket != -1:
                truncated = raw[:last_bracket + 1] + ', "impression_generale": "Analyse partielle."}'
                return json.loads(truncated)
        except (json.JSONDecodeError, UnboundLocalError):
            pass
        return {"error": "JSON invalide retourné par l'IA. Réessayez."}
    except Exception as e:
        return {"error": str(e)}


def deep_analyze_phrase(phrase: str, context: str, text_type: str) -> dict | None:
    """Analyse approfondie d'une phrase spécifique avec son contexte."""
    client = get_client()
    if client is None:
        return None

    prompt = f"""Tu es un coach d'écriture radio ultra-précis.

Analyse EN PROFONDEUR cette phrase extraite d'un texte radio ({text_type}).

CONTEXTE (le texte complet) :
{context}

PHRASE À ANALYSER :
"{phrase}"

Donne :
1. ORALISATION : Lis la phrase à voix haute mentalement. Où sont les difficultés de prononciation, les respirations forcées, les enchaînements de sons gênants ?
2. COMPRÉHENSION : Un auditeur distrait (en voiture, en cuisinant) comprend-il cette phrase du premier coup ? Que risque-t-il de comprendre de travers ?
3. IMPACT : Cette phrase crée-t-elle une image mentale ? Est-elle mémorable ou passe-t-elle inaperçue ?
4. IMAGE MENTALE : Décris en 5 mots maximum l'image que cette phrase génère dans l'esprit de l'auditeur. Si la phrase est abstraite, décris ce que l'auditeur "voit" réellement (ex: "Un dossier administratif sur un bureau", "Rien — du brouillard"). C'est le miroir : le journaliste doit voir ce que l'auditeur visualise.
5. RÉÉCRITURE : Propose 2 versions alternatives, une conservatrice (proche de l'original) et une radicale (repensée pour l'oreille).

{SCIENCE_CONTEXT}

Réponds UNIQUEMENT en JSON valide :
{{"oralisation": "...", "comprehension": "...", "impact": "...", "image_mentale": "...", "reecritures": [{{"type": "conservatrice", "texte": "..."}}, {{"type": "radicale", "texte": "..."}}]}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        if response.stop_reason == "max_tokens":
            return {"error": "Réponse tronquée."}

        raw = response.content[0].text.strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            raw = raw[start:end + 1]

        return json.loads(raw)

    except json.JSONDecodeError:
        return {"error": "JSON invalide. Réessayez."}
    except Exception as e:
        return {"error": str(e)}
