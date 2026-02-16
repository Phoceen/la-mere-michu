"""
Base de connaissances scientifiques pour l'écriture radio.

Ce fichier centralise les conclusions des études cognitives et neuroscientifiques
pertinentes pour l'analyse de textes radio. Il alimente :
- rules.py (seuils et messages des règles mécaniques)
- ai_analyzer.py (contexte scientifique du prompt IA)

À TERME : ce fichier sera enrichi/remplacé par un système RAG
qui ira chercher dynamiquement dans les PDFs des études.
"""

# ---------------------------------------------------------------------------
# Conclusions structurées par thème
# ---------------------------------------------------------------------------

FINDINGS = {
    "memoire_travail": {
        "seuil_chunks": 4,
        "plage_chunks": "3-5",
        "boucle_phonologique_sec": 2,
        "sources": [
            {"ref": "Cowan (2001)", "titre": "The Magical Number 4 in Short-Term Memory", "journal": "Behavioral and Brain Sciences", "finding": "La capacité réelle de la mémoire de travail est de 3 à 5 éléments (chunks), pas 7."},
            {"ref": "Miller (1956)", "titre": "The Magical Number Seven, Plus or Minus Two", "journal": "Psychological Review", "finding": "Estimation initiale de 7±2 éléments, révisée à la baisse depuis."},
            {"ref": "Baddeley & Hitch (1974-2000)", "titre": "Modèle de mémoire de travail", "journal": "Multiples", "finding": "La boucle phonologique ne retient l'info auditive que ~2 secondes avant dégradation."},
        ],
    },
    "longueur_phrase": {
        "seuil_mots_warning": 25,
        "seuil_mots_error": 30,
        "seuil_info_max": 4,
        "sources": [
            {"ref": "Cowan (2001)", "finding": "3-5 chunks max en mémoire de travail → une phrase radio ne devrait pas dépasser 3-4 unités d'information."},
            {"ref": "Caplan & Waters (1999)", "finding": "Les phrases syntaxiquement complexes sont plus difficiles et plus lentes à comprendre à l'oral."},
        ],
    },
    "chiffres": {
        "seuil_max_par_phrase": 2,
        "sources": [
            {"ref": "Baker et al. (2018)", "titre": "Cognitive Load Affects Numerical and Temporal Judgments", "journal": "Frontiers in Psychology", "finding": "Sous charge cognitive, les jugements numériques sont sous-estimés. Les chiffres sont encore plus difficiles à traiter quand le cerveau est déjà sollicité."},
            {"ref": "Sweller (1988)", "titre": "Cognitive Load Theory", "finding": "Toute surcharge extrinsèque (chiffres, infos inutiles) empêche le transfert vers la mémoire à long terme."},
        ],
    },
    "mots_concrets": {
        "sources": [
            {"ref": "Binder et al. (2009)", "titre": "Neural representation of abstract and concrete concepts", "journal": "Human Brain Mapping", "finding": "Les mots concrets sont reconnus plus rapidement et mieux mémorisés grâce au double codage (verbal + image mentale)."},
            {"ref": "Paivio — Théorie du double codage", "finding": "Les mots concrets activent deux voies de rappel en mémoire (verbale et visuelle), les abstraits une seule."},
        ],
    },
    "position_serielle": {
        "sources": [
            {"ref": "Glanzer & Cunitz (1966)", "titre": "Two Storage Mechanisms in Free Recall", "finding": "Les premiers éléments (primauté) et les derniers (récence) d'une liste sont les mieux mémorisés. Le milieu est le creux de rétention."},
        ],
    },
    "vagabondage_mental": {
        "taux_decrochage_pct": "30-40",
        "sources": [
            {"ref": "Kopp, D'Mello & Mills (2015)", "journal": "Frontiers in Psychology", "finding": "L'écoute passive produit le plus de vagabondage mental (32-43% du temps). Mémoire plus faible et moindre intérêt."},
            {"ref": "Murray et al. (2023)", "journal": "Scientific Reports", "finding": "Plus le vagabondage mental est fréquent, plus la mémoire de rappel est faible (immédiatement et après une semaine)."},
        ],
    },
    "prosodie": {
        "debit_optimal_mots_min": 175,
        "sources": [
            {"ref": "Rodero (2017)", "titre": "Pitch Range Variations Improve Cognitive Processing", "journal": "Human Communication Research", "finding": "Les variations de hauteur tonale améliorent l'attention (+15-25%), l'éveil et la mémoire."},
            {"ref": "Rodero (2023)", "titre": "Best Prosody for News", "journal": "Communication Research", "finding": "Le style broadcast (intonation répétitive, ~200 mots/min) est moins bien perçu que le style narratif (~175 mots/min). La monotonie provoque une adaptation sensorielle."},
            {"ref": "Rodero (2012)", "titre": "See It on a Radio Story", "journal": "Communication Research", "finding": "Les effets sonores et plans sonores augmentent significativement l'imagerie mentale et l'attention."},
        ],
    },
    "vitesse_traitement": {
        "lecture_mots_min": "200-400",
        "ecoute_mots_min": "125-160",
        "sources": [
            {"ref": "Rayner et al. (2008)", "journal": "Psychophysiology", "finding": "Lecture silencieuse : 200-400 mots/min. Compréhension orale : 125-160 mots/min. L'auditeur traite ~2x plus lentement qu'un lecteur."},
            {"ref": "Leroy et al. (2019)", "journal": "JAMIA", "finding": "Compréhension comparable texte vs audio, mais la rétention en rappel libre est légèrement inférieure à l'écoute."},
        ],
    },
    "attention_podcast": {
        "seuil_decision_mots": 18,
        "duree_preferee_min": "15-30",
        "sources": [
            {"ref": "Données NPR", "finding": "En 18 mots, l'auditeur décide s'il continue. 40% d'attrition dans les 7 premières minutes."},
            {"ref": "BBC Audio:Activated (2019)", "finding": "Écoute en activité : +18% engagement, +40% intensité émotionnelle, +22% encodage mémoire à long terme."},
            {"ref": "Wolpaw et al. (2022)", "journal": "Western J. Emergency Medicine", "finding": "L'attention mesurée par EEG pendant un podcast est équivalente à celle pendant la lecture."},
        ],
    },
    "redondance": {
        "sources": [
            {"ref": "Mayer — Principe de redondance", "finding": "Présenter la même info en narration ET en texte simultanément surcharge la mémoire de travail."},
            {"ref": "Mayer — Principe de cohérence", "finding": "Éliminer toute information non essentielle améliore l'apprentissage."},
        ],
    },
    "complexite_syntaxique": {
        "sources": [
            {"ref": "Caplan & Waters (1999)", "titre": "Verbal working memory and sentence comprehension", "journal": "Behavioral and Brain Sciences", "finding": "Les phrases complexes syntaxiquement sont plus difficiles et plus lentes à comprendre. Les individus à faible capacité de mémoire de travail sont les plus pénalisés."},
            {"ref": "Fedorenko et al. (2024)", "journal": "Nature", "finding": "C'est le juste niveau de complexité et d'inattendu qui active le cerveau. Trop simple = pas d'engagement. Trop complexe = décrochage."},
        ],
    },
}


# ---------------------------------------------------------------------------
# Fonctions utilitaires (pour le futur RAG et pour le prompt)
# ---------------------------------------------------------------------------

def get_all_sources() -> list[dict]:
    """Retourne la liste plate de toutes les sources."""
    sources = []
    for theme in FINDINGS.values():
        sources.extend(theme.get("sources", []))
    return sources


def get_prompt_context() -> str:
    """Génère le contexte scientifique à injecter dans le prompt IA."""
    lines = ["ÉTUDES SCIENTIFIQUES DE RÉFÉRENCE — utilise ces données pour appuyer tes analyses :\n"]
    for theme_name, theme_data in FINDINGS.items():
        theme_label = theme_name.replace("_", " ").upper()
        lines.append(f"## {theme_label}")
        for src in theme_data.get("sources", []):
            ref = src["ref"]
            finding = src["finding"]
            lines.append(f"- {ref} : {finding}")
        # Ajouter les seuils numériques
        for key, val in theme_data.items():
            if key not in ("sources",) and not key.startswith("_"):
                lines.append(f"  → Seuil : {key} = {val}")
        lines.append("")
    return "\n".join(lines)
