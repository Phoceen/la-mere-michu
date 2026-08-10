"""
Base de connaissances scientifiques pour l'écriture radio.

Ce fichier centralise :
- BIBLIO : la bibliographie structurée (chaque source a un id, un tier de fiabilité)
- FINDINGS : les conclusions actionnables par thème (seuils + renvois vers BIBLIO)
- ANGLICISMES : anglicismes évitables et leurs équivalents français
- JARGON_COMPREHENSION : taux de compréhension mesurés de termes journalistiques
  (importé depuis sondage_prive.py, fichier gitignoré — dict vide s'il est absent)

Il alimente :
- rules.py (seuils et messages des règles mécaniques)
- ai_analyzer.py (contexte scientifique du prompt IA)

La bibliographie complète et commentée (y compris les sources écartées) :
voir knowledge/bibliographie.md

Tiers de fiabilité :
- A : étude publiée dans une revue à comité de lecture (ou ouvrage académique)
- B : donnée institutionnelle sérieuse (OCDE, Arcom, médiateur, sondage n>1000)
Les sources de tier C (blogs, études marketing) sont documentées dans
bibliographie.md mais N'ENTRENT PAS dans ce fichier : l'outil ne les cite jamais.

À TERME : ce fichier sera enrichi/remplacé par un système RAG
qui ira chercher dynamiquement dans les PDFs des études.
"""

# ---------------------------------------------------------------------------
# BIBLIO — une entrée par source, référencée par id dans FINDINGS
# ---------------------------------------------------------------------------

BIBLIO = {
    # --- Tier A : revues à comité de lecture / ouvrages académiques ---
    "cowan2001": {"ref": "Cowan (2001)", "titre": "The Magical Number 4 in Short-Term Memory", "journal": "Behavioral and Brain Sciences", "tier": "A",
                  "finding": "La capacité réelle de la mémoire de travail est de 3 à 5 éléments (chunks), pas 7."},
    "miller1956": {"ref": "Miller (1956)", "titre": "The Magical Number Seven, Plus or Minus Two", "journal": "Psychological Review", "tier": "A",
                   "finding": "Estimation initiale de 7±2 éléments, révisée à la baisse depuis."},
    "baddeley1974": {"ref": "Baddeley & Hitch (1974-2000)", "titre": "Modèle de mémoire de travail", "journal": "Multiples", "tier": "A",
                     "finding": "La boucle phonologique ne retient l'info auditive que ~2 secondes avant dégradation."},
    "caplan1999": {"ref": "Caplan & Waters (1999)", "titre": "Verbal working memory and sentence comprehension", "journal": "Behavioral and Brain Sciences", "tier": "A",
                   "finding": "Les phrases syntaxiquement complexes sont plus difficiles et plus lentes à comprendre à l'oral. Les individus à faible capacité de mémoire de travail sont les plus pénalisés."},
    "baker2018": {"ref": "Baker et al. (2018)", "titre": "Cognitive Load Affects Numerical and Temporal Judgments", "journal": "Frontiers in Psychology", "tier": "A",
                  "finding": "Sous charge cognitive, les jugements numériques sont sous-estimés. Les chiffres sont encore plus difficiles à traiter quand le cerveau est déjà sollicité."},
    "sweller1988": {"ref": "Sweller (1988)", "titre": "Cognitive Load Theory", "journal": "Cognitive Science", "tier": "A",
                    "finding": "Toute surcharge extrinsèque (chiffres, infos inutiles) empêche le transfert vers la mémoire à long terme."},
    "binder2009": {"ref": "Binder et al. (2009)", "titre": "Neural representation of abstract and concrete concepts", "journal": "Human Brain Mapping", "tier": "A",
                   "finding": "Les mots concrets sont reconnus plus rapidement et mieux mémorisés grâce au double codage (verbal + image mentale)."},
    "paivio": {"ref": "Paivio — Théorie du double codage", "titre": "Dual Coding Theory", "journal": "Ouvrages académiques", "tier": "A",
               "finding": "Les mots concrets activent deux voies de rappel en mémoire (verbale et visuelle), les abstraits une seule."},
    "glanzer1966": {"ref": "Glanzer & Cunitz (1966)", "titre": "Two Storage Mechanisms in Free Recall", "journal": "J. of Verbal Learning and Verbal Behavior", "tier": "A",
                    "finding": "Les premiers éléments (primauté) et les derniers (récence) d'une liste sont les mieux mémorisés. Le milieu est le creux de rétention."},
    "kopp2015": {"ref": "Kopp, D'Mello & Mills (2015)", "titre": "Mind wandering during listening", "journal": "Frontiers in Psychology", "tier": "A",
                 "finding": "L'écoute passive produit le plus de vagabondage mental (32-43% du temps). Mémoire plus faible et moindre intérêt."},
    "murray2023": {"ref": "Murray et al. (2023)", "titre": "Mind wandering and recall", "journal": "Scientific Reports", "tier": "A",
                   "finding": "Plus le vagabondage mental est fréquent, plus la mémoire de rappel est faible (immédiatement et après une semaine)."},
    "rodero2012": {"ref": "Rodero (2012)", "titre": "See It on a Radio Story", "journal": "Communication Research", "tier": "A",
                   "finding": "Les effets sonores et plans sonores augmentent significativement l'imagerie mentale et l'attention."},
    "rodero2017": {"ref": "Rodero (2017)", "titre": "Pitch Range Variations Improve Cognitive Processing", "journal": "Human Communication Research", "tier": "A",
                   "finding": "Les variations de hauteur tonale améliorent l'attention (+15-25%), l'éveil et la mémoire."},
    "rodero2023": {"ref": "Rodero (2023)", "titre": "Best Prosody for News", "journal": "Communication Research", "tier": "A",
                   "finding": "Le style broadcast (intonation répétitive, ~200 mots/min) est moins bien perçu que le style narratif (~175 mots/min). La monotonie provoque une adaptation sensorielle."},
    "rayner2008": {"ref": "Rayner et al. (2008)", "titre": "Eye movements and reading speed", "journal": "Psychophysiology", "tier": "A",
                   "finding": "Lecture silencieuse : 200-400 mots/min. Compréhension orale : 125-160 mots/min. L'auditeur traite ~2x plus lentement qu'un lecteur."},
    "leroy2019": {"ref": "Leroy et al. (2019)", "titre": "Text vs audio comprehension", "journal": "JAMIA", "tier": "A",
                  "finding": "Compréhension comparable texte vs audio, mais la rétention en rappel libre est légèrement inférieure à l'écoute."},
    "wolpaw2022": {"ref": "Wolpaw et al. (2022)", "titre": "Podcast attention measured by EEG", "journal": "Western J. Emergency Medicine", "tier": "A",
                   "finding": "L'attention mesurée par EEG pendant un podcast est équivalente à celle pendant la lecture."},
    "mayer_redondance": {"ref": "Mayer — Principe de redondance", "titre": "Multimedia Learning", "journal": "Ouvrage académique", "tier": "A",
                         "finding": "Présenter la même info en narration ET en texte simultanément surcharge la mémoire de travail."},
    "mayer_coherence": {"ref": "Mayer — Principe de cohérence", "titre": "Multimedia Learning", "journal": "Ouvrage académique", "tier": "A",
                        "finding": "Éliminer toute information non essentielle améliore l'apprentissage."},
    "fedorenko2024": {"ref": "Fedorenko et al. (2024)", "titre": "Language and communication", "journal": "Nature", "tier": "A",
                      "finding": "C'est le juste niveau de complexité et d'inattendu qui active le cerveau. Trop simple = pas d'engagement. Trop complexe = décrochage."},
    "morillon2025": {"ref": "Morillon et al. (2025)", "titre": "Décodage cérébral de la parole : syllabes et phonèmes", "journal": "Science Advances (INSERM/Aix-Marseille)", "tier": "A",
                     "finding": "Le cortex auditif traite en parallèle deux rythmes : lent (syllabes) et rapide (phonèmes) — mécanisme universel vérifié en français. Un débit trop rapide ou une articulation imprécise dégradent ce double suivi, donc la compréhension."},
    "coupe2019": {"ref": "Coupé et al. (2019)", "titre": "Different languages, similar encoding efficiency", "journal": "Science Advances (CNRS/Lyon 2)", "tier": "A",
                  "finding": "Toutes les langues transmettent l'information à ~39 bits/s. Parler plus vite ne transmet pas plus : il existe un débit optimal de traitement cérébral de la parole."},
    "brainsciences2024": {"ref": "Brain Sciences (2024)", "titre": "Radio, Podcasts, and Music Streaming — EEG analysis", "journal": "Brain Sciences (MDPI)", "tier": "A",
                          "finding": "Mesuré par EEG, chaque format audio (radio, podcast, streaming) engage différemment attention, mémoire et émotion. La radio a un profil d'engagement attentionnel propre."},
    "praxematique2013": {"ref": "Cahiers de praxématique n°61 (2013)", "titre": "Le discours radiophonique en pratiques", "journal": "Cahiers de praxématique (Praxiling, Univ. Paul-Valéry)", "tier": "A",
                         "finding": "Première synthèse académique francophone sur le discours radiophonique : syntaxe de la phrase radio, prosodie, genres. Constat : les études de réception par les auditeurs sont quasi inexistantes."},
    "simon2013": {"ref": "Simon, Auchlin & Goldman (2013)", "titre": "Tendances prosodiques de la parole radiophonique", "journal": "Cahiers de praxématique", "tier": "A",
                  "finding": "Le débit, l'intonation et l'emphase de la parole radio française captent et maintiennent l'attention ; une accélération avec montée mélodique agit comme signal d'alerte attentionnelle."},
    "egjlle2024": {"ref": "EGJLLE (2024)", "titre": "L'influence des anglicismes et emprunts étrangers sur le français", "journal": "Études de Gestion et de Jurisprudence des Langues en Europe", "tier": "A",
                   "finding": "L'excès d'anglicismes non intégrés entrave la compréhension, en particulier entre jeunes générations et locuteurs plus âgés."},
    "charaudeau": {"ref": "Charaudeau (1984-)", "titre": "Le discours d'information médiatique", "journal": "Ouvrages académiques (Univ. Sorbonne Paris-Nord)", "tier": "A",
                   "finding": "Le journaliste est lié à son public par un « contrat de communication » : captation, crédibilisation, information. La clarté de la langue est une clause implicite de ce contrat."},

    # --- Tier B : données institutionnelles sérieuses ---
    "npr": {"ref": "Données NPR", "titre": "Audience podcast", "journal": "NPR (données d'audience)", "tier": "B",
            "finding": "En 18 mots, l'auditeur décide s'il continue. 40% d'attrition dans les 7 premières minutes."},
    "bbc2019": {"ref": "BBC Audio:Activated (2019)", "titre": "Écoute en activité", "journal": "BBC (étude interne)", "tier": "B",
                "finding": "Écoute en activité : +18% engagement, +40% intensité émotionnelle, +22% encodage mémoire à long terme."},
    "piaac2024": {"ref": "OCDE — PIAAC (2024)", "titre": "Évaluation internationale des compétences des adultes", "journal": "OCDE", "tier": "B",
                  "finding": "28% des adultes français (16-65 ans) sont au niveau 1 ou moins en littératie (+6 pts depuis 2012). 48% des 55-65 ans — cœur d'audience radio — sont en difficulté face aux textes complexes. Difficultés écrit et oral fortement corrélées."},
    "mediatrice_rf": {"ref": "Médiatrice de Radio France (2022-2026)", "titre": "Courriers d'auditeurs sur la langue française", "journal": "Radio France (médiation)", "tier": "B",
                      "finding": "Plainte n°1 des auditeurs sur la langue : les anglicismes non nécessaires (casting, think tank, storytelling, impacter...), suivis de l'appauvrissement lexical et du relâchement syntaxique."},
    "cegep2024": {"ref": "Olsen — Cégep de Jonquière (2024)", "titre": "La langue dans les radios québécoises", "journal": "Cégep de Jonquière (ATM)", "tier": "B",
                  "finding": "Sur 40 matinales analysées : anglicismes dans 40/40, impropriétés lexicales dans 38/40. Motif n°1 invoqué : « se rapprocher de l'auditeur ». 60% des professionnels perçoivent une dégradation de la langue."},
    "arcom2025": {"ref": "Arcom/IFOP (2025)", "titre": "Les Français et la radio", "journal": "Arcom", "tier": "B",
                  "finding": "83% des auditeurs font confiance aux informations de la radio — capital lié à la qualité perçue de la langue et à la clarté. 73% des Français écoutent la radio chaque semaine."},
    "falc2023": {"ref": "CNSA / Vivre FM (2023)", "titre": "« Tout compris ! », première émission radio en FALC", "journal": "CNSA", "tier": "B",
                 "finding": "La méthode FALC (Facile à Lire et à Comprendre) impose des phrases ≤ 12 mots, un vocabulaire courant, sans jargon ni métaphore — référence d'accessibilité maximale."},
}

# ---------------------------------------------------------------------------
# Données privées (sondage interne) — fichier gitignoré, absent du repo.
# En son absence (ex. déploiement cloud), le détecteur de jargon est inactif
# mais tout le reste fonctionne normalement.
# ---------------------------------------------------------------------------

try:
    from sondage_prive import BIBLIO_SONDAGE, JARGON_COMPREHENSION, JARGON_INSIGHTS, SONDAGE_REF
    BIBLIO["sondage_termes_2025"] = BIBLIO_SONDAGE
except ImportError:
    JARGON_COMPREHENSION = {}
    JARGON_INSIGHTS = []
    SONDAGE_REF = "Sondage interne (données non embarquées)"


# ---------------------------------------------------------------------------
# Conclusions actionnables par thème (sources = ids de BIBLIO)
# ---------------------------------------------------------------------------

FINDINGS = {
    "memoire_travail": {
        "seuil_chunks": 4,
        "plage_chunks": "3-5",
        "boucle_phonologique_sec": 2,
        "sources": ["cowan2001", "miller1956", "baddeley1974"],
    },
    "longueur_phrase": {
        "seuil_mots_warning": 25,
        "seuil_mots_error": 30,
        "seuil_info_max": 4,
        "sources": ["cowan2001", "caplan1999"],
    },
    "chiffres": {
        "seuil_max_par_phrase": 2,
        "sources": ["baker2018", "sweller1988"],
    },
    "mots_concrets": {
        "sources": ["binder2009", "paivio"],
    },
    "position_serielle": {
        "sources": ["glanzer1966"],
    },
    "vagabondage_mental": {
        "taux_decrochage_pct": "30-40",
        "sources": ["kopp2015", "murray2023"],
    },
    "prosodie": {
        "debit_optimal_mots_min": 175,
        "sources": ["rodero2017", "rodero2023", "rodero2012", "simon2013"],
    },
    "vitesse_traitement": {
        "lecture_mots_min": "200-400",
        "ecoute_mots_min": "125-160",
        "debit_information_bits_sec": 39,
        "sources": ["rayner2008", "leroy2019", "coupe2019", "morillon2025"],
    },
    "attention_podcast": {
        "seuil_decision_mots": 18,
        "duree_preferee_min": "15-30",
        "sources": ["npr", "bbc2019", "wolpaw2022", "brainsciences2024"],
    },
    "redondance": {
        "sources": ["mayer_redondance", "mayer_coherence"],
    },
    "complexite_syntaxique": {
        "sources": ["caplan1999", "fedorenko2024"],
    },
    "anglicismes": {
        "sources": ["mediatrice_rf", "cegep2024", "egjlle2024"],
    },
    "jargon_institutionnel": {
        "seuil_warning_pct": 50,
        "seuil_info_pct": 66,
        "sources": ["sondage_termes_2025", "charaudeau"],
    },
    "litteratie_audience": {
        "pct_adultes_niveau1_ou_moins": 28,
        "pct_55_65_en_difficulte": 48,
        "falc_mots_max": 12,
        "sources": ["piaac2024", "falc2023"],
    },
}


# ---------------------------------------------------------------------------
# ANGLICISMES — évitables à l'antenne, avec équivalent français
# (liste construite à partir des plaintes d'auditeurs recensées par la
#  Médiatrice de Radio France, complétée des anglicismes médiatiques courants)
# ---------------------------------------------------------------------------

ANGLICISMES = {
    "casting": "distribution",
    "think tank": "cercle de réflexion",
    "storytelling": "mise en récit",
    "story telling": "mise en récit",
    "greenwashing": "écoblanchiment",
    "bad buzz": "polémique",
    "buzz": "retentissement",
    "performer": "briller, réussir",
    "ranking": "classement",
    "impacter": "toucher, affecter",
    "timing": "calendrier, moment",
    "deadline": "date limite, échéance",
    "process": "procédure",
    "task force": "groupe de travail",
    "turnover": "rotation du personnel",
    "burn-out": "épuisement professionnel",
    "burnout": "épuisement professionnel",
    "cluster": "foyer, pôle",
    "come-back": "retour",
    "comeback": "retour",
    "challenge": "défi",
    "challenger": "défier, concurrencer",
    "leadership": "autorité, direction",
    "leader": "chef de file, meneur",
    "low cost": "à bas prix",
    "low-cost": "à bas prix",
    "mainstream": "grand public",
    "newsletter": "lettre d'information",
    "prime time": "première partie de soirée",
    "punchline": "formule choc",
    "spoiler": "divulgâcher",
    "teaser": "avant-goût, bande-annonce",
    "workshop": "atelier",
    "fake news": "infox, fausse information",
    "big data": "mégadonnées",
    "open space": "plateau ouvert",
    "pitch": "résumé, argument",
    "one-man-show": "spectacle solo",
    "hotline": "assistance téléphonique",
    "fact-checking": "vérification des faits",
    "best of": "florilège",
    "best-of": "florilège",
    "sponsor": "parrain, mécène",
    "sponsoriser": "parrainer",
    "scoop": "exclusivité",
    "deal": "accord, marché",
    "live": "en direct",
    "replay": "rediffusion",
    "start-up": "jeune pousse",
    "business": "affaires",
    "hashtag": "mot-dièse",
    "community manager": "animateur de communauté",
    "insider": "initié",
    "lobbying": "actions d'influence",
    "crash test": "essai de choc",
}


# ---------------------------------------------------------------------------
# Fonctions utilitaires (pour le prompt et le futur RAG)
# ---------------------------------------------------------------------------

def resolve_sources(theme: dict) -> list[dict]:
    """Résout les ids de sources d'un thème vers les entrées BIBLIO complètes."""
    return [BIBLIO[sid] for sid in theme.get("sources", []) if sid in BIBLIO]


def get_all_sources() -> list[dict]:
    """Retourne la liste plate de toutes les sources (entrées BIBLIO)."""
    return list(BIBLIO.values())


def get_prompt_context() -> str:
    """Génère le contexte scientifique à injecter dans le prompt IA."""
    lines = [
        "ÉTUDES SCIENTIFIQUES DE RÉFÉRENCE — utilise ces données pour appuyer tes analyses.",
        "Quand tu cites une source, cite-la précisément (auteur/institution + année) et ne cite QUE des sources de cette liste.\n",
    ]
    for theme_name, theme_data in FINDINGS.items():
        theme_label = theme_name.replace("_", " ").upper()
        lines.append(f"## {theme_label}")
        for src in resolve_sources(theme_data):
            lines.append(f"- {src['ref']} : {src['finding']}")
        # Ajouter les seuils numériques
        for key, val in theme_data.items():
            if key not in ("sources",) and not key.startswith("_"):
                lines.append(f"  → Seuil : {key} = {val}")
        lines.append("")

    # Données du sondage compréhension (résumé compact pour généralisation)
    # Bloc présent uniquement si les données privées sont disponibles en local.
    if JARGON_INSIGHTS:
        lines.append("## DONNÉES MESURÉES — COMPRÉHENSION DU VOCABULAIRE JOURNALISTIQUE")
        lines.append(f"{SONDAGE_REF} : taux de compréhension réels de termes de JT.")
        lines.append(f"CONFIDENTIALITÉ : cite cette étude UNIQUEMENT sous la forme « {SONDAGE_REF} » — "
                     "jamais de date, d'échantillon ou d'origine plus précis.")
        for insight in JARGON_INSIGHTS:
            lines.append(f"- {insight}")
        lines.append("Les 35 termes testés sont déjà détectés mécaniquement. Ton rôle : GÉNÉRALISE — "
                     "signale tout terme du même type (jargon institutionnel, judiciaire, économique, européen, "
                     "métonymie ou périphrase de lieu de pouvoir, sigle non développé) même s'il n'est pas dans la liste, "
                     "en t'appuyant sur ces ordres de grandeur.")
        lines.append("")
    return "\n".join(lines)
