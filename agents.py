"""
Pipeline d'analyse orchestré — remplace l'appel LLM monolithique.

Architecture : 4 agents spécialisés, chacun un appel Claude court avec une
sortie structurée (client.messages.parse + Pydantic — plus de JSON parsé à la
main). L'orchestration est du Python déterministe :

    rules.py (mécanique, gratuit)
        │
        ├─ en PARALLÈLE :
        │    agent_forme      → phrase par phrase (regard rédac, incarnation)
        │    agent_assertions → faits à vérifier (extraction pure → Haiku)
        │    agent_coherence  → lancement↔papier, transitions, sobriété
        │    agent_ecoute     → écoute simulée multi-tours (inspirée STORM) :
        │                       le texte arrive morceau par morceau, l'auditeur
        │                       dit ce qu'il retient sans voir la suite, puis
        │                       restitue. Trace d'écoute conservée.
        │
        └─ PUIS :
             agent_memo       → la note de relecture, synthèse des sorties
                                précédentes — elle OUVRE sur la restitution

Un agent qui échoue dégrade proprement (champ vide) au lieu de tout faire tomber.
Côté utilisateur, une analyse = 1 crédit de quota, quel que soit le nombre
d'appels API sous le capot (le quota est compté dans app.py par action).
"""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Literal, Optional

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

from knowledge_base import get_prompt_context
from rules import split_sentences

load_dotenv()

# Jugement éditorial (forme, cohérence, mémo) vs extraction pure (assertions)
MODEL_JUGEMENT = "claude-sonnet-5"
MODEL_EXTRACTION = "claude-haiku-4-5"


def get_client() -> Anthropic | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "sk-ant-...":
        return None
    return Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Schémas de sortie (validés par l'API — le modèle ne peut pas dévier)
# ---------------------------------------------------------------------------

class PhraseForme(BaseModel):
    id: str  # reprend l'identifiant [#L1], [#P3]...
    verdict: Literal["ok", "a_verifier", "probleme"]
    regard_redac: str
    regard_auditeur: str
    score_incarnation: Literal["VIF", "FLOU", "GRIS"]
    suggestion: Optional[str]  # une direction, jamais une réécriture — null si ok


class FormeResult(BaseModel):
    phrases: list[PhraseForme]


class Claim(BaseModel):
    extrait: str
    zone: Literal["lancement", "papier", "qr"]
    type: Literal["chiffre", "nom_propre", "date", "fait", "citation"]
    note: str


class ClaimsResult(BaseModel):
    claims: list[Claim]


class CoherenceResult(BaseModel):
    coherence: Optional[str]  # null si une seule zone de texte
    transitions: list[str]  # transitions brutales repérées (endroit + nature du pivot manquant)
    sobriete: list[str]  # affirmations sur-dramatisées à adoucir


class EcouteResult(BaseModel):
    restitution: str           # ce que l'auditeur retient, dans ses mots
    perdus: list[str]          # infos du texte qui n'ont pas survécu à l'écoute
    malentendus: list[str]     # ce qui risque d'être compris de travers
    decrochage: Optional[str]  # l'endroit où l'attention a lâché, null sinon


class MemoResult(BaseModel):
    note_relecture: str
    impression_generale: str


class Reecriture(BaseModel):
    type: Literal["conservatrice", "radicale"]
    texte: str


class DeepResult(BaseModel):
    oralisation: str
    comprehension: str
    impact: str
    image_mentale: str
    reecritures: list[Reecriture]


# ---------------------------------------------------------------------------
# Socle commun des prompts
# ---------------------------------------------------------------------------

_REGLES_METIER = """PONCTUATION MÉTIER : les journalistes radio ponctuent rarement de façon classique. \
Les « / », « // », « ... » et retours à la ligne sont des MARQUES DE RESPIRATION volontaires — \
ce n'est JAMAIS une faute, ne les signale pas. Ne corrige ni l'orthographe ni les coquilles : \
à l'antenne, ça ne s'entend pas. Seule exception : une coquille qui peut faire trébucher la \
lecture à voix haute ou créer un contresens sonore.
CITATIONS : appuie-toi sur les études fournies quand c'est pertinent (auteur/institution + année). \
Ne cite JAMAIS une source hors liste."""


def _tag_sentences(text: str, prefix: str) -> tuple[str, dict[str, str]]:
    """Injecte des ID [#L1], [#P1]... et retourne aussi la table id → phrase."""
    sentences = split_sentences(text)
    mapping = {f"#{prefix}{i}": s for i, s in enumerate(sentences, 1)}
    tagged = "\n".join(f"[{sid}] {s}" for sid, s in mapping.items())
    return tagged, mapping


def _dedupe_claims(claims: list[Claim]) -> list[dict]:
    """Fusionne les assertions dont l'extrait est contenu dans un autre (même zone).

    Évite de faire vérifier deux fois le même passage : « une fusée SpaceX,
    l'entreprise d'Elon Musk » disparaît au profit de la phrase complète qui le
    contient, sa note étant reversée dans celle de l'assertion englobante.
    """
    def norm(s: str) -> str:
        return " ".join(s.lower().split())

    items = [c.model_dump() for c in claims]
    kept = []
    for i, c in enumerate(items):
        containers = [
            (j, o) for j, o in enumerate(items)
            if j != i and c["zone"] == o["zone"]
            and norm(c["extrait"]) in norm(o["extrait"])
            # sur extraits identiques, seul le premier survit
            and (len(norm(o["extrait"])) > len(norm(c["extrait"])) or j < i)
        ]
        if containers:
            # on reverse la note dans l'extrait le plus englobant (pas de fusion en chaîne)
            _, best = max(containers, key=lambda t: len(norm(t[1]["extrait"])))
            if norm(c["note"]) not in norm(best["note"]):
                best["note"] = f"{best['note']} — {c['note']}"
        else:
            kept.append(c)
    return kept


def _parse(client: Anthropic, model: str, system: str, user: str,
           schema: type[BaseModel], max_tokens: int) -> BaseModel:
    """Un appel avec sortie structurée validée par l'API."""
    response = client.messages.parse(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_format=schema,
    )
    if response.parsed_output is None:
        raise ValueError(f"Sortie non parsable (stop_reason={response.stop_reason})")
    return response.parsed_output


# ---------------------------------------------------------------------------
# Les 4 agents
# ---------------------------------------------------------------------------

def agent_forme(client: Anthropic, corpus: str, papier_type: str) -> FormeResult:
    """Mandats A + D : style oral phrase par phrase, double regard, incarnation."""
    context = get_prompt_context(themes=[
        "memoire_travail", "longueur_phrase", "mots_concrets", "position_serielle",
        "prosodie", "vitesse_traitement", "complexite_syntaxique", "vagabondage_mental",
    ])
    system = f"""Tu es un relecteur expert de scripts radio (20 ans d'antenne), formé aux neurosciences de l'écoute.
Analyse PHRASE PAR PHRASE uniquement ce que les règles mécaniques (déjà appliquées, listées dans le message) ne détectent pas. NE RÉPÈTE PAS ces alertes.
Chaque phrase est précédée d'un identifiant [#L1], [#P3]... REPRENDS-LE tel quel dans le champ id (avec le #).

DEUX REGARDS pour chaque phrase :
- regard_redac (rédacteur en chef) : prête pour l'antenne ? Rythme, souffle, fluidité orale, ambiguïtés sonores, registre parlé vs écrit lu.
- regard_auditeur (auditeur naïf, première écoute) : compréhension LOCALE de cette phrase uniquement — jargon institutionnel/judiciaire/économique/européen, sigles non développés, périphrases de lieux de pouvoir, ambiguïtés sonores. L'expérience d'écoute globale (mémoire, décrochage, restitution) est mesurée par un autre agent : ne t'en occupe pas.

score_incarnation (théorie du double codage, Paivio) :
- VIF : sujet concret, verbe d'action, décor identifiable
- FLOU : sujet institutionnel, jargon léger, peu d'image
- GRIS : langue de bois, abstractions en cascade (en cas de doute FLOU/GRIS : 2+ mots abstraits en -tion/-ité/-isme/-ence = GRIS)

Les phrases au milieu du texte sont en zone de creux mémoriel (Glanzer & Cunitz, 1966) : vérifie qu'une relance raccroche l'auditeur.
suggestion : une DIRECTION (« coupe après le verbe », « attaque par le concret ») — JAMAIS de réécriture complète. null si la phrase est bonne.
Si une phrase est bonne : verdict ok, regards très courts, suggestion null.
{_REGLES_METIER}

{context}"""
    return _parse(client, MODEL_JUGEMENT, system, corpus, FormeResult, max_tokens=16000)


def agent_assertions(client: Anthropic, corpus: str) -> ClaimsResult:
    """Mandat B : extraction des faits à vérifier avant antenne (pas de fact-checking)."""
    system = """Tu extrais d'un script radio TOUTE assertion vérifiable : chiffres précis, noms propres, dates, lieux, faits attribués, citations.
Tu ne fais PAS de fact-checking : tu LISTES ce que le journaliste devrait vérifier avant antenne.
Pour chaque assertion : l'extrait exact, sa zone (lancement/papier/qr selon l'en-tête de section), son type, et une note disant quoi vérifier précisément.
REGROUPE : une seule assertion par passage. Si plusieurs éléments imbriqués dans la même affirmation (un nom propre dans un fait, un chiffre dans une date...) se vérifient d'un même geste, produis UNE assertion — type le plus englobant — dont la note liste tous les points à vérifier. Ne crée jamais deux assertions dont les extraits se recouvrent.
Sois exhaustif sur les FAITS, pas sur les fiches : mieux vaut une assertion de trop qu'un fait faux à l'antenne, mais jamais deux fois la même vérification."""
    return _parse(client, MODEL_EXTRACTION, system, corpus, ClaimsResult, max_tokens=4096)


_PERSONA_AUDITEUR = """Tu n'es PAS un analyste, PAS un relecteur. Tu es un AUDITEUR de radio ordinaire :
tu conduis, tu écoutes d'une oreille, tu ne peux JAMAIS revenir en arrière ni relire.
Ta mémoire est celle d'un humain moyen : 3-4 éléments retenus maximum, les détails
du milieu s'effacent, un mot inconnu ou technique te fait perdre la phrase entière.
Tu as un niveau de lecture moyen (en France, un adulte sur trois est en difficulté
face à un texte complexe — tu es dans la moyenne, pas un expert).
Tu ne connais ni les numéros de phrases ni le texte écrit : tu ne cites que ce que
tu as ENTENDU, avec tes mots à toi, comme au café en racontant à un ami.
Sois honnête : si tu as tout compris et tout retenu, dis-le. N'invente pas de la
confusion pour faire plaisir."""


def agent_ecoute(client: Anthropic, texte_brut: str, chunk_size: int = 2) -> dict:
    """Écoute simulée multi-tours (inspirée de STORM, Shao et al. 2024).

    Le texte arrive morceau par morceau ; l'auditeur dit ce qu'il retient à
    chaque étape SANS voir la suite (une seule passe, comme à l'antenne), puis
    restitue. La trace d'écoute (états intermédiaires) situe le décrochage au
    moment où il se produit, pas rétrospectivement.
    """
    sentences = split_sentences(texte_brut)
    chunks = [" ".join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]

    system = f"""{_PERSONA_AUDITEUR}

On te fait écouter un papier radio MORCEAU PAR MORCEAU. Après chaque morceau, dis en
1-2 phrases maximum ce que tu comprends et retiens À CE STADE (ton état mental, pas une
analyse). Tu ne sais pas ce qui vient ensuite. Ta mémoire est limitée : si trop
d'informations s'accumulent, les premières s'effacent — dis-le quand ça arrive.
Si un passage te perd ou t'ennuie, dis-le sur le moment."""

    messages: list[dict] = []
    trace: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        messages.append({"role": "user", "content": f"[morceau {i}/{len(chunks)}]\n{chunk}"})
        resp = client.messages.create(
            model=MODEL_JUGEMENT, max_tokens=1024,
            system=system, messages=messages,
        )
        etat = "".join(b.text for b in resp.content if b.type == "text").strip()
        trace.append(etat)
        messages.append({"role": "assistant", "content": etat})

    messages.append({"role": "user", "content": """Le papier est terminé. Sans le relire (tu ne peux pas), restitue ton expérience :
- restitution : ce que tu retiens au final, dans tes mots (2-3 phrases)
- perdus : les infos entendues en route mais qui ne sont plus dans ta tête
- malentendus : ce que tu as peut-être compris de travers
- decrochage : le moment où ton attention a lâché, si elle a lâché (null sinon)"""})
    final = client.messages.parse(
        model=MODEL_JUGEMENT, max_tokens=2048,
        system=system, messages=messages,
        output_format=EcouteResult,
    )
    if final.parsed_output is None:
        raise ValueError(f"Sortie non parsable (stop_reason={final.stop_reason})")
    return {**final.parsed_output.model_dump(), "trace": trace}


def agent_coherence(client: Anthropic, corpus: str, has_both_zones: bool) -> CoherenceResult:
    """Mandat C + transitions + sobriété éditoriale."""
    context = get_prompt_context(
        themes=["attention_podcast", "redondance", "position_serielle"],
        include_sondage=False,
    )
    coherence_part = (
        """COHÉRENCE LANCEMENT / PAPIER : le lancement correspond-il au contenu ? Répétitions textuelles entre les deux ? Le lancement donne-t-il envie d'écouter la suite ? Remplis coherence (2-3 phrases max)."""
        if has_both_zones
        else "Une seule zone de texte : mets coherence à null."
    )
    system = f"""Tu es un rédacteur en chef radio. Trois vérifications sur ce script :

1. {coherence_part}

2. TRANSITIONS : repère les sauts brutaux d'un sujet à l'autre sans phrase pivot. Pour chacun, indique l'endroit exact et la NATURE du pivot manquant (« il manque une phrase qui annonce la limite avant d'y entrer ») — sans l'écrire à la place du journaliste. Liste vide si le déroulé coule bien.

3. SOBRIÉTÉ : repère les affirmations sur-dramatisées ou trop catégoriques pour une antenne d'info. Indique la direction (« adoucis », « attribue à une source ») sans reformuler. Liste vide si le ton est juste.
{_REGLES_METIER}

{context}"""
    return _parse(client, MODEL_JUGEMENT, system, corpus, CoherenceResult, max_tokens=4096)


def agent_memo(client: Anthropic, corpus: str, syntheses: str) -> MemoResult:
    """Mandat E : la note de relecture, rédigée en SYNTHÈSE des autres agents."""
    context = get_prompt_context(themes=["litteratie_audience", "attention_podcast"])
    system = f"""Tu es un rédacteur en chef radio expérimenté qui rend sa copie annotée au journaliste.
Tu reçois le texte ET les constats déjà établis (règles mécaniques, analyse phrase par phrase, cohérence, faits relevés). Ta note est une SYNTHÈSE hiérarchisée de ces constats — tu ne re-analyses pas tout, tu tries ce qui compte et tu le racontes.

C'est un MEMO ÉDITORIAL, pas une liste de bullets. Structure OBLIGATOIRE, 4 sections séparées par des sauts de ligne :

**CE QU'IL RESTE APRÈS UNE ÉCOUTE** (1 paragraphe)
Un auditeur simulé a écouté le papier une seule fois (résultat dans les constats : restitution, infos perdues, décrochage). Ouvre là-dessus : ce qui survit à l'écoute, ce qui s'est perdu, et l'écart avec ce que le papier voulait faire passer. C'est le miroir — le journaliste doit voir en premier ce que l'auditeur retient vraiment.

**LE PLUS URGENT** (1-3 paragraphes)
Ce qui empêche le texte de passer en l'état. Cite la phrase exacte entre guillemets, explique POURQUOI c'est un problème pour l'oreille, donne une DIRECTION — jamais de réécriture.

**À SURVEILLER** (1-2 paragraphes)
Ce qui affaiblit sans bloquer : passages plats, zone de creux sans relance, registre écrit, transitions manquantes, sur-dramatisation.

**CE QUI FONCTIONNE** (1 paragraphe)
Ce qui est bon et qu'il faut garder. Sois précis : cite les passages qui marchent.

Règles : style direct, tutoiement, ton de rédac chef bienveillant mais exigeant. Cite les numéros de phrases. Reste succinct — le journaliste est dans le feu de l'action, il veut les grands trucs à reprendre et avancer.
impression_generale : le verdict en 1-2 phrases.
{_REGLES_METIER}

{context}"""
    user = f"{corpus}\n\n=== CONSTATS DES AUTRES ANALYSES ===\n{syntheses}"
    return _parse(client, MODEL_JUGEMENT, system, user, MemoResult, max_tokens=8192)


# ---------------------------------------------------------------------------
# Orchestrateur
# ---------------------------------------------------------------------------

def analyze_pipeline(
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

    # -- Construction du corpus commun (texte taggé + alertes mécaniques) --
    parts, mapping = [], {}
    if has_lancement:
        tagged, m = _tag_sentences(lancement_text, "L")
        mapping.update(m)
        parts.append(f"=== LANCEMENT ===\n{tagged}")
        if lancement_rules:
            parts.append(lancement_rules)
    if has_papier:
        label = "PAPIER" if papier_type == "Papier" else "Q/R AVEC RELANCES"
        tagged, m = _tag_sentences(papier_text, "P")
        mapping.update(m)
        parts.append(f"=== {label} ===\n{tagged}")
        if papier_rules:
            parts.append(papier_rules)
    corpus = "\n\n".join(parts)

    # L'auditeur simulé « entend » le texte brut, dans l'ordre antenne :
    # ni tags, ni alertes mécaniques — il n'est pas analyste.
    texte_brut = "\n\n".join(
        t for t in (lancement_text, papier_text) if t and t.strip()
    )

    # -- Phase 1 : forme, assertions, cohérence, écoute en parallèle --
    def _safe(fn, *args):
        try:
            return fn(client, *args)
        except Exception as e:
            return e

    with ThreadPoolExecutor(max_workers=4) as pool:
        f_forme = pool.submit(_safe, agent_forme, corpus, papier_type)
        f_claims = pool.submit(_safe, agent_assertions, corpus)
        f_coher = pool.submit(_safe, agent_coherence, corpus, has_lancement and has_papier)
        f_ecoute = pool.submit(_safe, agent_ecoute, texte_brut)
        forme, claims, coher, ecoute = (
            f_forme.result(), f_claims.result(), f_coher.result(), f_ecoute.result()
        )

    forme_ok = isinstance(forme, FormeResult)
    claims_ok = isinstance(claims, ClaimsResult)
    coher_ok = isinstance(coher, CoherenceResult)
    ecoute_ok = isinstance(ecoute, dict)

    if not (forme_ok or claims_ok or coher_ok):
        return {"error": f"Analyse indisponible : {forme}"}

    # -- Phase 2 : le mémo synthétise ce que la phase 1 a trouvé --
    # L'écoute simulée d'abord : le mémo ouvre sur la restitution.
    syntheses = []
    if ecoute_ok:
        bloc = [f"ÉCOUTE SIMULÉE (une seule passe, auditeur moyen) :",
                f"Restitution : {ecoute['restitution']}"]
        if ecoute["perdus"]:
            bloc.append("Infos perdues : " + " | ".join(ecoute["perdus"]))
        if ecoute["malentendus"]:
            bloc.append("Malentendus possibles : " + " | ".join(ecoute["malentendus"]))
        if ecoute["decrochage"]:
            bloc.append(f"Décrochage : {ecoute['decrochage']}")
        syntheses.append("\n".join(bloc))
    if forme_ok:
        points = [
            f"- {p.id} [{p.verdict}/{p.score_incarnation}] {p.regard_auditeur}"
            + (f" → {p.suggestion}" if p.suggestion else "")
            for p in forme.phrases if p.verdict != "ok"
        ]
        gris = [p.id for p in forme.phrases if p.score_incarnation == "GRIS"]
        syntheses.append("PHRASE PAR PHRASE (hors phrases ok) :\n" + ("\n".join(points) or "- rien à signaler"))
        if gris:
            syntheses.append(f"Phrases GRISES (aucune image mentale) : {', '.join(gris)}")
    if coher_ok:
        if coher.coherence:
            syntheses.append(f"COHÉRENCE : {coher.coherence}")
        if coher.transitions:
            syntheses.append("TRANSITIONS MANQUANTES :\n" + "\n".join(f"- {t}" for t in coher.transitions))
        if coher.sobriete:
            syntheses.append("SOBRIÉTÉ :\n" + "\n".join(f"- {s}" for s in coher.sobriete))
    claims_list = _dedupe_claims(claims.claims) if claims_ok else []
    if claims_ok:
        syntheses.append(f"FAITS À VÉRIFIER : {len(claims_list)} assertions relevées (listées à part, ne les détaille pas).")

    try:
        memo = agent_memo(client, corpus, "\n\n".join(syntheses))
        note, impression = memo.note_relecture, memo.impression_generale
    except Exception as e:
        note, impression = f"(Note de relecture indisponible : {e})", ""

    # -- Assemblage au format attendu par app.py (inchangé) --
    zones: dict = {}
    if forme_ok:
        papier_key = "papier" if papier_type == "Papier" else "qr"
        for p in forme.phrases:
            key = "lancement" if p.id.startswith("#L") else papier_key
            zones.setdefault(key, {"forme": []})["forme"].append({
                "id": p.id,
                "original": mapping.get(p.id, ""),
                "verdict": p.verdict,
                "regard_redac": p.regard_redac,
                "regard_auditeur": p.regard_auditeur,
                "score_incarnation": p.score_incarnation,
                "suggestion": p.suggestion,
            })

    return {
        "note_relecture": note,
        "impression_generale": impression,
        "zones": zones,
        "claims": claims_list,
        "coherence": coher.coherence if coher_ok else None,
        "transitions": coher.transitions if coher_ok else [],
        "sobriete": coher.sobriete if coher_ok else [],
        "ecoute": ecoute if ecoute_ok else None,
    }


# ---------------------------------------------------------------------------
# Chirurgie de phrase (analyse approfondie à la demande)
# ---------------------------------------------------------------------------

def deep_analyze_phrase(phrase: str, context: str, text_type: str) -> dict | None:
    client = get_client()
    if client is None:
        return None

    science = get_prompt_context(themes=["memoire_travail", "mots_concrets", "prosodie", "vitesse_traitement"])
    system = f"""Tu es un coach d'écriture radio ultra-précis. Analyse EN PROFONDEUR une phrase extraite d'un texte radio ({text_type}).
1. oralisation : lis-la à voix haute mentalement — difficultés de prononciation, respirations forcées, enchaînements de sons gênants.
2. comprehension : un auditeur distrait la comprend-il du premier coup ? Que risque-t-il de comprendre de travers ?
3. impact : crée-t-elle une image mentale ? Mémorable ou invisible ?
4. image_mentale : en 5 mots max, l'image que l'auditeur visualise (« Un dossier sur un bureau », « Rien — du brouillard »). C'est le miroir.
5. reecritures : 2 versions, une conservatrice (proche de l'original) et une radicale (repensée pour l'oreille). C'est le SEUL endroit où tu proposes une réécriture, car le journaliste l'a explicitement demandée.
{_REGLES_METIER}

{science}"""
    user = f"CONTEXTE (texte complet) :\n{context}\n\nPHRASE À ANALYSER :\n\"{phrase}\""
    try:
        result = _parse(client, MODEL_JUGEMENT, system, user, DeepResult, max_tokens=4096)
        return result.model_dump()
    except Exception as e:
        return {"error": str(e)}
