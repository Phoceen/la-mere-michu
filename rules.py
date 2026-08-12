import re
from dataclasses import dataclass, field
from knowledge_base import FINDINGS, ANGLICISMES, JARGON_COMPREHENSION, SONDAGE_REF

@dataclass
class Alert:
    rule: str
    message: str
    severity: str  # "info", "warning", "error"
    source: str = ""  # référence scientifique

@dataclass
class SentenceAnalysis:
    sentence: str
    alerts: list[Alert] = field(default_factory=list)

    @property
    def severity(self) -> str:
        if any(a.severity == "error" for a in self.alerts):
            return "error"
        if any(a.severity == "warning" for a in self.alerts):
            return "warning"
        if any(a.severity == "info" for a in self.alerts):
            return "info"
        return "ok"


def _syllables(word: str) -> int:
    word = word.lower().strip()
    vowels = "aeiouyàâéèêëïîôùûüæœ"
    count, prev = 0, False
    for c in word:
        if c in vowels:
            if not prev:
                count += 1
            prev = True
        else:
            prev = False
    if word.endswith("e") and count > 1:
        count -= 1
    if word.endswith("es") and count > 1:
        count -= 1
    return max(count, 1)


# Repère de diffusion sonore : « BOB 1 », « Son : itw maire », « EXTRAIT 2 - ... »
# Anchré en début d'unité : « Son avenir est incertain » ne matche pas.
_BROADCAST_MARKER = re.compile(
    r"^\s*(?:bob|son|extrait)s?\s*(?:n[°º]|no|#)?\s*\d*\s*(?:[:\-–—].*)?$",
    re.IGNORECASE,
)


def is_broadcast_marker(sentence: str) -> bool:
    """Indication de diffusion sonore — repère technique, jamais du texte lu."""
    return bool(_BROADCAST_MARKER.match(sentence.strip()))


def split_sentences(text: str) -> list[str]:
    """Découpe en unités de souffle, pas seulement en phrases grammaticales.

    Les journalistes radio ponctuent rarement de façon classique : ils marquent
    les respirations avec /, //, ... ou de simples retours à la ligne. Toutes
    ces marques sont traitées comme des fins d'unité. Le texte original est
    préservé (rien n'est réécrit), seuls les / servant de séparateurs — jamais
    ceux collés comme dans « km/h » — sont consommés.

    Les repères de diffusion sonore (« bob », « son », « extrait », numérotés
    ou non) sont écartés : ils ne sont pas du texte à l'antenne et ne doivent
    jamais être analysés.
    """
    raw = re.split(
        r"(?<=[.!?…])\s+"      # ponctuation classique (couvre aussi .. et ...)
        r"|\s*\n+\s*"          # retour à la ligne = nouvelle unité de souffle
        r"|\s+/+\s*|\s*/+\s+", # / ou // entourés d'au moins un espace
        text.strip(),
    )
    return [
        s.strip() for s in raw
        if s.strip() and re.search(r"\w", s) and not is_broadcast_marker(s)
    ]


# --- Règles enrichies par les études ---

_mem = FINDINGS["memoire_travail"]
_len = FINDINGS["longueur_phrase"]
_num = FINDINGS["chiffres"]
_vag = FINDINGS["vagabondage_mental"]

def _length(s: str) -> list[Alert]:
    n = len(s.split())
    if n > _len["seuil_mots_error"]:
        return [Alert(
            "Trop long", f"{n} mots — la mémoire de travail ne retient que {_mem['plage_chunks']} éléments (Cowan, 2001). Coupez cette phrase.",
            "error", "Cowan (2001), Caplan & Waters (1999)"
        )]
    if n > _len["seuil_mots_warning"]:
        return [Alert(
            "Un peu long", f"{n} mots — au-delà de 25 mots, la boucle phonologique (~{_mem['boucle_phonologique_sec']}s) peine à suivre (Baddeley).",
            "warning", "Baddeley & Hitch (1974)"
        )]
    return []

def _complex_words(s: str) -> list[Alert]:
    words = [w for w in re.findall(r"[a-zàâéèêëïîôùûüæœç'-]+", s.lower()) if _syllables(w) > 4]
    if words:
        return [Alert(
            "Mots complexes", f'{", ".join(words[:4])} — les mots concrets et courts sont mieux mémorisés grâce au double codage verbal + image (Binder et al., 2009).',
            "warning", "Binder et al. (2009), Paivio"
        )]
    return []

def _passive(s: str) -> list[Alert]:
    if re.search(r"\b(?:est|sont|a été|ont été|sera|seront)\s+\w+[éi]e?s?\b", s, re.IGNORECASE):
        return [Alert(
            "Voix passive", "La voix active est plus directe. Les phrases complexes syntaxiquement sont plus lentes à traiter à l'oral (Caplan & Waters, 1999).",
            "warning", "Caplan & Waters (1999)"
        )]
    return []

def _parenthetical(s: str) -> list[Alert]:
    alerts = []
    if "(" in s:
        alerts.append(Alert("Parenthèses", "L'auditeur ne les entend pas. Faites une phrase à part.", "warning"))
    if re.search(r",\s*[^,]{30,},", s):
        alerts.append(Alert(
            "Incise longue", "L'auditeur perd le fil — la mémoire de travail ne gère que 3-5 éléments simultanés (Cowan, 2001).",
            "warning", "Cowan (2001)"
        ))
    return alerts

def _negation(s: str) -> list[Alert]:
    patterns = [r"\bne\s+\w+\s+pas\s+(?:ne|sans|aucun|jamais)\b", r"\bni\s+\w+\s+ni\b"]
    for p in patterns:
        if re.search(p, s, re.IGNORECASE):
            return [Alert("Double négation", "Reformulez en positif — moins de charge cognitive pour l'auditeur (Sweller, 1988).", "warning", "Sweller (1988)")]
    return []

def _is_round(num_str: str) -> bool:
    """Un chiffre est 'rond' s'il est simple à retenir à l'oral."""
    cleaned = re.sub(r"[\s.,]", "", num_str)
    if not cleaned.isdigit():
        return False
    if len(cleaned) <= 2:  # « 25 ans », « 8 à 9 mois » : se disent sans effort
        return True
    return cleaned.endswith("00") or cleaned.endswith("000")


def _has_round_context(s: str) -> bool:
    """Détecte si la phrase contient des mots qui arrondissent les chiffres."""
    return bool(re.search(r"\b(million|milliard|millier|dizaine|centaine|environ|près de|quasi|presque)\b", s, re.IGNORECASE))


def _numbers(s: str) -> list[Alert]:
    alerts = []
    nums = re.findall(r"\b\d[\d\s,.]*\d\b|\b\d+\b", s)
    if len(nums) > _num["seuil_max_par_phrase"]:
        alerts.append(Alert(
            "Trop de chiffres", f"{len(nums)} nombres — sous charge cognitive, les chiffres sont sous-estimés et mal retenus (Baker et al., 2018). Préférez une comparaison concrète.",
            "error", "Baker et al. (2018), Sweller (1988)"
        ))
    elif nums:
        has_context = _has_round_context(s)
        precise = [n for n in nums if not _is_round(n) and not has_context]
        if precise:
            alerts.append(Alert(
                "Chiffres précis", f'{", ".join(precise[:3])} — un chiffre non arrondi sature la boucle phonologique (~2s). Préférez « près de 12 000 » à « 12 457 ».',
                "warning", "Baker et al. (2018), Baddeley & Hitch (1974)"
            ))
        else:
            alerts.append(Alert("Chiffres", "Dites-les à voix haute. Vérifiez qu'ils passent bien à l'oral.", "info", "Baker et al. (2018)"))
    acronyms = [a for a in re.findall(r"\b[A-Z]{2,}\b", s) if a not in _JARGON_ACRONYMS]
    if acronyms:
        alerts.append(Alert("Sigles", f'{", ".join(acronyms[:4])} — développez au moins une fois pour l\'auditeur.', "info"))
    return alerts

_ABSTRACT_SUFFIXES = re.compile(r"\b\w+(tion|ité|isme|ence|ance|ude|ment)\b", re.IGNORECASE)
_VAGUE_WORDS = {
    "dispositif", "problématique", "synergie", "optimisation", "mécanisme",
    "dynamique", "processus", "paradigme", "transversalité", "modalité",
    "gouvernance", "écosystème", "levier", "enjeu", "dimension",
}


def _vague_meter(s: str) -> list[Alert]:
    words = re.findall(r"[a-zàâéèêëïîôùûüæœç'-]+", s.lower())
    vague_found = [w for w in words if w in _VAGUE_WORDS]
    abstract_found = _ABSTRACT_SUFFIXES.findall(s)
    total = len(vague_found) + len(abstract_found)
    if total >= 3:
        examples = (vague_found + [m for m in abstract_found])[:4]
        return [Alert(
            "Langue abstraite",
            f'{", ".join(examples)} — les mots concrets créent une image mentale et sont 2x mieux mémorisés (Paivio). Préférez le concret.',
            "info", "Binder et al. (2009), Paivio"
        )]
    return []


# --- Anglicismes (Médiatrice Radio France, Cégep de Jonquière, EGJLLE) ---

# Alternation triée par longueur décroissante : "bad buzz" matche avant "buzz",
# "challenger" avant "challenge".
_ANGLICISM_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(a) for a in sorted(ANGLICISMES, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

# Verbes anglicisés : détecter aussi les formes conjuguées (« a impacté », « sponsorise »)
_VERB_STEMS = {"impact": "impacter", "sponsoris": "sponsoriser", "perform": "performer"}
_ANGLICISM_VERB_RE = re.compile(
    r"\b(" + "|".join(_VERB_STEMS) + r")(?:e|es|ent|é|ée|és|ées|er|era|eront|ait|aient)\b",
    re.IGNORECASE,
)


def _anglicisms(s: str) -> list[Alert]:
    found = []
    seen = set()
    for m in _ANGLICISM_RE.finditer(s):
        key = m.group(0).lower()
        if key in ANGLICISMES and key not in seen:
            seen.add(key)
            found.append(f"« {m.group(0)} » (→ {ANGLICISMES[key]})")
    for m in _ANGLICISM_VERB_RE.finditer(s):
        infinitive = _VERB_STEMS[m.group(1).lower()]
        if infinitive not in seen:
            seen.add(infinitive)
            found.append(f"« {m.group(0)} » (→ {ANGLICISMES[infinitive]})")
    if found:
        return [Alert(
            "Anglicisme",
            f'{", ".join(found[:4])} — 1ʳᵉ plainte des auditeurs sur la langue (Médiatrice de Radio France) ; '
            f"l'excès d'anglicismes creuse l'écart de compréhension entre générations (EGJLLE, 2024).",
            "warning", "Médiatrice Radio France, EGJLLE (2024), Olsen (2024)"
        )]
    return []


# --- Jargon institutionnel (sondage de compréhension — données privées) ---
# Si sondage_prive.py est absent, JARGON_COMPREHENSION est vide et ce
# détecteur ne lève simplement aucune alerte.

_jar = FINDINGS["jargon_institutionnel"]
_SONDAGE_SRC = SONDAGE_REF


# Termes qui s'accordent en genre/nombre : motif explicite
_JARGON_OVERRIDES = {
    "mise en examen": r"\bmise?s? en examen\b",
    "écroué": r"\bécroué(?:e|s|es)?\b",
    "non-lieu": r"\bnon-lieux?\b",
    "missiles balistiques": r"\bmissiles? balistiques?\b",
    "directive européenne": r"\bdirectives? européennes?\b",
}


def _jargon_pattern(term: str) -> re.Pattern:
    """Sigles : sensibles à la casse (OMS ≠ oms). Le reste : insensible."""
    if term in _JARGON_OVERRIDES:
        return re.compile(_JARGON_OVERRIDES[term], re.IGNORECASE)
    if term.upper() == term and re.fullmatch(r"[A-Z0-9 ]+", term):
        return re.compile(r"\b" + re.escape(term) + r"\b")
    return re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)


_JARGON_PATTERNS = [(_jargon_pattern(k), v) for k, v in JARGON_COMPREHENSION.items()]

# Sigles couverts par le sondage — exclus de l'alerte générique "Sigles"
# (le détecteur jargon donne un message plus riche, avec le taux mesuré)
_JARGON_ACRONYMS = {k for k in JARGON_COMPREHENSION if k.upper() == k and re.fullmatch(r"[A-Z0-9 ]+", k)}


def _jargon(s: str) -> list[Alert]:
    hard, soft = [], []
    for pattern, data in _JARGON_PATTERNS:
        if pattern.search(s):
            label = f"« {data['terme']} » ({data['pct']}%)"
            if data["pct"] < _jar["seuil_warning_pct"]:
                hard.append(label)
            elif data["pct"] < _jar["seuil_info_pct"]:
                soft.append(label)
    alerts = []
    if hard:
        alerts.append(Alert(
            "Jargon opaque",
            f'{", ".join(hard)} — compris par moins d\'un Français sur deux (taux mesurés). '
            f"Explicitez le terme ou remplacez-le par du concret. "
            f"NB : taux mesuré sur le mot isolé — vérifiez aussi que la phrase entière reste compréhensible.",
            "warning", _SONDAGE_SRC
        ))
    if soft:
        alerts.append(Alert(
            "Jargon à expliciter",
            f'{", ".join(soft)} — un gros tiers des Français ne comprend pas ce terme (mesure sur le mot isolé). '
            f"Une incise d'explication suffit souvent (« l'OMS, l'agence de l'ONU pour la santé »).",
            "info", _SONDAGE_SRC
        ))
    return alerts


def _info_position(s: str, index: int, total: int) -> list[Alert]:
    """Vérifie si l'info clé est bien placée (début/fin, pas au milieu)."""
    if total >= 4 and index == total // 2:
        return [Alert(
            "Zone de creux", "Cette phrase est au milieu du texte — la zone la moins mémorisée (Glanzer & Cunitz, 1966). Placez-y l'info la moins cruciale ou ajoutez une relance.",
            "info", "Glanzer & Cunitz (1966)"
        )]
    return []


RULES = [_length, _complex_words, _passive, _parenthetical, _negation, _numbers, _vague_meter, _anglicisms, _jargon]


def analyze_text(text: str) -> list[SentenceAnalysis]:
    sentences = split_sentences(text)
    total = len(sentences)
    results = []
    for i, s in enumerate(sentences):
        analysis = SentenceAnalysis(sentence=s)
        for rule in RULES:
            analysis.alerts.extend(rule(s))
        analysis.alerts.extend(_info_position(s, i, total))
        results.append(analysis)
    return results


def summarize_for_prompt(results: list[SentenceAnalysis]) -> str:
    """Résumé compact des alertes mécaniques pour le contexte Claude."""
    lines = ["RÉSULTATS DES RÈGLES MÉCANIQUES (déjà signalés — NE PAS re-signaler) :"]
    clean = []
    for i, r in enumerate(results, 1):
        if r.alerts:
            short = r.sentence[:60] + ("..." if len(r.sentence) > 60 else "")
            names = ", ".join(a.rule for a in r.alerts)
            lines.append(f'- Phrase {i} ("{short}"): {names}')
        else:
            clean.append(str(i))
    if clean:
        lines.append(f"Phrases sans alerte mécanique : {', '.join(clean)}")
    return "\n".join(lines)
